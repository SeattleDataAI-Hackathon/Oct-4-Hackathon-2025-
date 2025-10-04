# WhatsApp Skin Photo Triage Bot (Non‑diagnostic)

Team Member:
Corneille Ngoy

https://github.com/JCorneilleN/

> **Educational triage only — not medical advice.** This bot looks at a **WhatsApp‑sent photo** (via Twilio) and returns:
>
> * A **likeness that it could be an STD** (low/medium/high + percent)
> * Top **STD name candidates** with percent‑style *pattern match* scores
> * If unlikely to be an STD, top **non‑STD possibilities** with scores
> * Observed features + simple care guidance
>
> It **does not diagnose**, and it **does not store raw images** — only metadata/results.

---

## Stack

* **API**: FastAPI + Uvicorn
* **WhatsApp**: Twilio (Sandbox or a WhatsApp Business number)
* **AI**: OpenAI Vision (e.g., `gpt-4o-mini`) via the official Python SDK
* **DB**: Neon (serverless Postgres) using `psycopg` async pool
* **OS**: Works on Windows/macOS/Linux; commands below show Windows PowerShell

---

## Project Layout

```
app/
  main.py           # FastAPI app + Twilio webhook (/twilio/sms)
  ai.py             # vision call → JSON (likeness %, candidates, features)
  logic.py          # builds safe reply message text
  db.py             # Neon Postgres connection + simple helpers
  utils/
    images.py       # image-type/quality checks (no raw images stored)
requirements.txt    # pinned deps
README.md           # this file
```

---

## Quick Start (Local Dev)

### 1) Python & venv

```powershell
# from your project folder
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2) Environment variables (`.env`)

Create a file named `.env` in the project root:

```ini
# OpenAI
OPENAI_API_KEY=sk-...your-key...

# Neon (Postgres) — paste your full connection string
# Example (make sure you use your own):
DATABASE_URL=postgresql://USER:PASSWORD@HOST/dbname?sslmode=require&channel_binding=require

# Optional: Twilio signature validation (not required for TwiML replies)
# TWILIO_AUTH_TOKEN=your_twilio_auth_token
```

### 3) Database table

Run this SQL once (e.g., in Neon SQL console):

```sql
CREATE TABLE IF NOT EXISTS uploads (
  id            BIGSERIAL PRIMARY KEY,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  user_phone    TEXT,
  media_url     TEXT,
  ai_result     JSONB,
  quality       JSONB,
  triage_bucket TEXT
);
```

### 4) Start the API

```powershell
uvicorn app.main:app --reload --port 8000
```

* Open docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Health checks:

  * `GET /health` → `{"status":"ok"}`
  * `GET /db/ping` → confirms DB connectivity

### 5) Expose to the Internet (ngrok)

```powershell
ngrok http http://127.0.0.1:8000
```

Copy the HTTPS forwarding URL, e.g. `https://abc123.ngrok-free.app`

### 6) Twilio WhatsApp Sandbox

1. In the Twilio Console → **Messaging → Try it out → WhatsApp Sandbox**
2. Join the sandbox from your WhatsApp using the join code Twilio shows you
3. Set **When a message comes in** to your webhook URL:

   * `https://<your-ngrok-domain>/twilio/sms`
4. From WhatsApp, send a test **photo** to the sandbox number

If everything is wired, Twilio will POST the photo to your webhook and you’ll get an automated reply.

---

## How It Works (High Level)

1. **Webhook** (`POST /twilio/sms`) receives Twilio’s form‑encoded payload.
2. We fetch `MediaUrl0` and `MediaContentType0` (short‑lived Twilio URL), download bytes.
3. **Image checks** (`utils/images.py`) reject non‑images and flag quality (blurry, dark).
4. **AI call** (`ai.py`) sends the image (base64 in a data URL) and a strict JSON schema request to OpenAI. The model returns:

   * `std_overall.likelihood_percent` → visual pattern likeness (not probability)
   * `std_candidates[]` and `non_std_candidates[]` → top labels + scores
   * `observed_features[]`, `triage_bucket`, `notes[]`
5. **Reply builder** (`logic.py`) formats a safe WhatsApp reply:

   * “Educational triage only” disclaimer
   * STD likeness band + percent
   * If ≥40% show STD candidates; otherwise show non‑STD candidates
   * Observed features + testing guidance
6. **DB write** (`db.py`) stores **metadata** (phone, Twilio media URL, JSON result). **Raw images are not stored.**

---

## Endpoints

* `GET /health` – service is up
* `GET /db/ping` – DB connectivity ok
* `POST /twilio/sms` – Twilio WhatsApp webhook (TwiML response)
* `GET /docs` – auto OpenAPI docs (Swagger UI)

### Local cURL (simulate Twilio)

> Twilio sends `application/x-www-form-urlencoded`. Here’s a minimal mock:

```bash
curl -X POST http://127.0.0.1:8000/twilio/sms \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "From=whatsapp:+123456789" \
  --data-urlencode "NumMedia=1" \
  --data-urlencode "MediaUrl0=https://example.com/your-test.jpg" \
  --data-urlencode "MediaContentType0=image/jpeg"
```

---

## Configuration Notes

* **Model**: default `gpt-4o-mini` for vision JSON. You can change in `app/ai.py`.
* **Safety language**: `logic.py` keeps wording conservative (non‑diagnostic).
* **Labels**: A small, curated set is defined in `app/ai.py` for both STD and non‑STD conditions. You can edit/expand the lists anytime.
* **Costs**: You pay OpenAI per request; images add tokens. Keep photos 1 per message and throttle as needed.
* **Rate limiting**: Consider a simple IP/phone throttle if you go beyond testing.

---

## Troubleshooting

**Twilio hits `/twilio/sms` but I get 404**

* Ensure your Twilio **webhook URL path** exactly matches `/twilio/sms` and your server is running.

**500 with `cannot identify image file`**

* Make sure you’re using `MediaUrl0` that is an image, and include `MediaContentType0`. The code checks content type and falls back gracefully.

**OpenAI 400 about `input_image`**

* The code uses the supported `image_url` content type. If you changed it, revert to `{"type":"image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}`.

**DB errors (placeholders/parameters)**

* The app uses standard `$1..$n` placeholders with `psycopg`. Make sure the SQL and args count match (see `main.py` insert statement).

**Pool deprecation warning**

* `psycopg_pool` warns if opened in constructor. Current code still works; can be updated later to `await pool.open()` in startup.

---

## Privacy & Compliance

* **No raw images stored**. Only metadata (phone, Twilio URL, AI JSON) is saved.
* This project is **not HIPAA compliant** out of the box. Do not market as a diagnostic tool.
* Add a **consent banner** if you deploy beyond personal testing.

---

## Deploying

* Any host that can run FastAPI + reach Twilio + connect to Neon works (Render, Railway, Fly.io, etc.).
* Make sure your public URL is HTTPS and reachable by Twilio, then update the webhook URL in the Twilio Console.

---

## Extending

* **Signature validation**: verify Twilio requests using `TWILIO_AUTH_TOKEN`.
* **Triage policy**: adjust threshold (e.g., show STD candidates only if ≥50%).
* **Labeling**: expand `STD_LABELS`/`NON_STD_LABELS` in `app/ai.py`.
* **Messaging UX**: add a first‑time disclaimer message or follow‑up instructions.

---


