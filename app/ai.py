# app/ai.py — robust parsing fix (handles string fields safely)
from typing import Dict, Any, List
import base64, os, json
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Controlled label sets to keep outputs consistent
STD_LABELS: List[str] = [
    "Genital herpes (HSV)",
    "Syphilis (chancre)",
    "HPV genital warts",
    "Molluscum contagiosum",
    "Scabies (burrows)",
    "Chancroid",
]

NON_STD_LABELS: List[str] = [
    "Folliculitis",
    "Ingrown hair",
    "Contact dermatitis",
    "Irritant dermatitis",
    "Tinea cruris (ringworm)",
    "Candidiasis (yeast)",
    "Impetigo",
    "Insect bites",
    "Acneiform eruption",
    "Eczema/dermatitis",
]

SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "image_quality": {
            "type": "object",
            "properties": {
                "ok": {"type": "boolean"},
                "too_blurry": {"type": "boolean"},
                "too_dark": {"type": "boolean"},
            },
            "required": ["ok", "too_blurry", "too_dark"],
            "additionalProperties": False,
        },
        "observed_features": {"type": "array", "items": {"type": "string"}},
        "triage_bucket": {
            "type": "string",
            "enum": ["unclear", "concerning", "non_specific"],
        },
        "notes": {"type": "array", "items": {"type": "string"}},
        # NEW: overall STD likeness (percent), plus candidate lists
        "std_overall": {
            "type": "object",
            "properties": {
                "likelihood_percent": {"type": "integer", "minimum": 0, "maximum": 100},
                "rationale": {"type": "string"},
            },
            "required": ["likelihood_percent"],
            "additionalProperties": False,
        },
        "std_candidates": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "label": {"type": "string", "enum": STD_LABELS + ["Other STD"]},
                    "score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "rationale": {"type": "string"},
                },
                "required": ["label", "score"],
                "additionalProperties": False,
            },
        },
        "non_std_candidates": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "label": {"type": "string", "enum": NON_STD_LABELS + ["Other non-STD"]},
                    "score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "rationale": {"type": "string"},
                },
                "required": ["label", "score"],
                "additionalProperties": False,
            },
        },
    },
    "required": [
        "image_quality",
        "triage_bucket",
        "std_overall",
        "std_candidates",
        "non_std_candidates",
    ],
    "additionalProperties": False,
}

PROMPT = (
    "You are a dermatology *triage* assistant. You do NOT diagnose. "
    "From the image, describe visible features (ulcer, vesicle, pustule, crust, scaling, erosion, distribution) "
    "and assess *pattern similarity*, not probability."
    "\nReturn strictly the JSON matching the provided schema."
    "\nRules:" \
    "\n- 'likelihood_percent' reflects visual *pattern similarity* that the lesion is an STI/STD-related condition, not a medical probability." \
    "\n- 'score' values must be in [0,1] and represent relative pattern match; convert to percent by score*100 when displaying." \
    "\n- Fill both std_candidates and non_std_candidates with up to 3 best labels each, sorted by score desc."
)


def _ensure_dict(x: Any) -> Dict[str, Any]:
    if isinstance(x, dict):
        return x
    if isinstance(x, str):
        try:
            parsed = json.loads(x)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def _ensure_list_of_objs(x: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if isinstance(x, list):
        for it in x:
            if isinstance(it, dict):
                out.append(it)
    elif isinstance(x, str):
        try:
            parsed = json.loads(x)
            if isinstance(parsed, list):
                for it in parsed:
                    if isinstance(it, dict):
                        out.append(it)
        except Exception:
            pass
    return out


def _coerce_percent(v: Any, default: int = 0) -> int:
    try:
        if isinstance(v, (int, float)):
            n = int(round(float(v)))
        elif isinstance(v, str):
            n = int(round(float(v.strip().replace('%', ''))))
        else:
            n = default
    except Exception:
        n = default
    return max(0, min(100, n))


def _norm_candidates(cands: List[Dict[str, Any]], allow: List[str]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for c in cands[:5]:  # limit
        label = str(c.get("label", "")).strip() or "Other"
        if label not in allow and label not in ("Other STD", "Other non-STD", "Other"):
            # map unknowns to Other
            label = "Other STD" if allow is STD_LABELS else "Other non-STD"
        score = c.get("score", 0)
        try:
            score = float(score)
        except Exception:
            score = 0.0
        score = max(0.0, min(1.0, score))
        rationale = str(c.get("rationale", ""))[:280]
        out.append({"label": label, "score": score, "rationale": rationale})
    # sort desc by score
    out.sort(key=lambda x: x["score"], reverse=True)
    return out[:3]


async def analyze_image_non_diagnostic(img_bytes: bytes) -> Dict[str, Any]:
    """Call OpenAI vision (chat.completions) and coerce to our schema.
    Returns keys: image_quality, observed_features, triage_bucket, notes,
    std_overall{likelihood_percent, rationale}, std_candidates[], non_std_candidates[].
    """
    b64 = base64.b64encode(img_bytes).decode("utf-8")

    messages = [
        {"role": "system", "content": "Return only valid JSON per the schema. Do not diagnose."},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": PROMPT},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
            ],
        },
    ]

    data: Dict[str, Any]

    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "triage", "schema": SCHEMA},
            },
            messages=messages,
            temperature=0.2,
        )
        data = getattr(resp.choices[0].message, "parsed", None)
        if not isinstance(data, dict):
            raw = resp.choices[0].message.content
            data = json.loads(raw) if isinstance(raw, str) else {}
    except Exception:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=messages,
            temperature=0.2,
        )
        raw = resp.choices[0].message.content
        data = json.loads(raw) if isinstance(raw, str) else (raw or {})
        if not isinstance(data, dict):
            data = {}

    # --- Coerce & defaults ---
    iq = _ensure_dict(data.get("image_quality"))
    image_quality = {
        "ok": bool(iq.get("ok", True)),
        "too_blurry": bool(iq.get("too_blurry", False)),
        "too_dark": bool(iq.get("too_dark", False)),
    }

    observed = data.get("observed_features") or []
    if not isinstance(observed, list):
        observed = [str(observed)] if observed else []

    triage = data.get("triage_bucket")
    triage_bucket = triage if isinstance(triage, str) and triage in {"unclear", "concerning", "non_specific"} else "non_specific"

    notes = data.get("notes") or []
    if not isinstance(notes, list):
        notes = [str(notes)] if notes else []

    std_overall_raw = _ensure_dict(data.get("std_overall"))
    likelihood_percent = _coerce_percent(std_overall_raw.get("likelihood_percent", 0))
    std_overall = {
        "likelihood_percent": likelihood_percent,
        "rationale": str(std_overall_raw.get("rationale", ""))[:400],
    }

    std_cands = _norm_candidates(_ensure_list_of_objs(data.get("std_candidates")), STD_LABELS)
    nonstd_cands = _norm_candidates(_ensure_list_of_objs(data.get("non_std_candidates")), NON_STD_LABELS)

    return {
        "image_quality": image_quality,
        "observed_features": observed,
        "triage_bucket": triage_bucket,
        "notes": notes,
        "std_overall": std_overall,
        "std_candidates": std_cands,
        "non_std_candidates": nonstd_cands,
    }

