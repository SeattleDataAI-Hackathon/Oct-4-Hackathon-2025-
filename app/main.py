# app/main.py — full, updated
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.messaging_response import MessagingResponse
from httpx import BasicAuth
import httpx, os, json

from .settings import settings
from .db import init_pool, close_pool, execute, fetchrow
from .logic import build_reply
from .ai import analyze_image_non_diagnostic
from .utils.images import basic_quality

app = FastAPI(title="WhatsApp Triage Bot", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.allowed_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DB pool lifecycle ---
@app.on_event("startup")
async def _startup():
    await init_pool()

@app.on_event("shutdown")
async def _shutdown():
    await close_pool()

# --- Health & ping ---
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/db/ping")
async def db_ping():
    row = await fetchrow("SELECT 'neon_ok' AS status")
    return row

# --- Twilio media helper (auth + redirects + content-type check) ---
async def fetch_twilio_media(url: str) -> bytes:
    """Download WhatsApp media from Twilio with required Basic Auth.
    Follows redirects and validates content-type.
    """
    auth = BasicAuth(os.getenv("TWILIO_ACCOUNT_SID", ""), os.getenv("TWILIO_AUTH_TOKEN", ""))
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, auth=auth) as client:
        r = await client.get(url)
        r.raise_for_status()
        ctype = r.headers.get("content-type", "").lower()
        if not ctype.startswith("image/") and ctype not in ("application/octet-stream",):
            raise ValueError(f"Non-image content-type from Twilio: {ctype}")
        return r.content

# --- WhatsApp webhook ---
@app.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    num_media = int(form.get("NumMedia", "0"))
    from_number = form.get("From", "unknown")
    media_url = form.get("MediaUrl0")

    resp = MessagingResponse()

    if num_media == 0 or not media_url:
        resp.message("Please send a clear photo. (Educational triage only; not a diagnosis.)")
        return Response(content=str(resp), media_type="application/xml")

    # Download Twilio-hosted image with auth + safe fallback
    try:
        img_bytes = await fetch_twilio_media(media_url)
    except Exception:
        resp.message("I couldn't access the image from WhatsApp (permissions or format). Please resend, or try a JPG/PNG.\nNot a diagnosis.")
        return Response(content=str(resp), media_type="application/xml")

    # Local quick quality screen
    q = basic_quality(img_bytes)

    # AI (non-diagnostic) analysis
    ai = await analyze_image_non_diagnostic(img_bytes)
    # Prefer stricter quality gate if local check fails
    if isinstance(ai, dict):
        ai["image_quality"] = q if not q.get("ok") else ai.get("image_quality", q)
    else:
        ai = {"image_quality": q, "triage_bucket": "non_specific", "observed_features": [], "notes": []}

    message_text = build_reply(ai)

    # Store metadata only (no raw images) — psycopg uses %s placeholders
    await execute(
        """
        INSERT INTO uploads (user_phone, media_url, ai_result, quality, triage_bucket)
        VALUES (%s, %s, %s::jsonb, %s::jsonb, %s)
        """,
        from_number,
        media_url,
        json.dumps(ai),
        json.dumps(q),
        ai.get("triage_bucket", "unclear"),
    )

    resp.message(message_text)
    return Response(content=str(resp), media_type="application/xml")

# Optional alias if your Twilio webhook is /twilio/sms
@app.post("/twilio/sms")
async def twilio_sms_alias(request: Request):
    return await whatsapp_webhook(request)
