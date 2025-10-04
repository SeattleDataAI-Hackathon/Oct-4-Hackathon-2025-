from typing import Dict, Any, List

def _pct(n: float | int) -> str:
    try:
        return f"{int(round(float(n)))}%"
    except Exception:
        return "0%"


def _band(p: int) -> str:
    if p >= 70:
        return "high"
    if p >= 40:
        return "medium"
    return "low"


def _fmt_cands(cands: List[Dict[str, Any]], max_items: int = 3) -> List[str]:
    out: List[str] = []
    for c in (cands or [])[:max_items]:
        label = c.get("label", "?")
        score = c.get("score", 0.0)
        try:
            score_pct = int(round(float(score) * 100))
        except Exception:
            score_pct = 0
        out.append(f"• {label} — {score_pct}%")
    return out


def build_reply(ai: Dict[str, Any]) -> str:
    iq = ai.get("image_quality", {})
    too_blurry = iq.get("too_blurry")
    too_dark = iq.get("too_dark")

    lines: List[str] = []
    lines.append("⚠️ Educational triage only — not a medical diagnosis.")

    if too_blurry or too_dark:
        tips = []
        if too_blurry:
            tips.append("steady the camera or move closer")
        if too_dark:
            tips.append("use bright natural light")
        lines.append("Photo quality issue: " + ", ".join(tips) + ". If possible, send a clearer photo.")

    # STD likelihood
    std_overall = ai.get("std_overall", {})
    p = int(std_overall.get("likelihood_percent", 0) or 0)
    band = _band(p)
    lines.append(f"STD likeness based on visual pattern: {band} ({_pct(p)}).")

    std_cands = ai.get("std_candidates", []) or []
    nonstd_cands = ai.get("non_std_candidates", []) or []

    if p >= 40 and std_cands:
        lines.append("Possible STD-related patterns:")
        lines.extend(_fmt_cands(std_cands))
    else:
        lines.append("More likely non-STD patterns:")
        lines.extend(_fmt_cands(nonstd_cands))

    obs = ai.get("observed_features") or []
    if obs:
        lines.append("Seen in the photo: " + ", ".join(obs[:6]))

    # Safety / next steps
    lines.append(
        "Next steps: if you’re worried or have pain, fever, or spreading sores, get checked by a clinician. "
        "Testing (e.g., swab/PCR for herpes, blood tests for syphilis) is the only way to know for sure."
    )

    return "\n".join(lines)
