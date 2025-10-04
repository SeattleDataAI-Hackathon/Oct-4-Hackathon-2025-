import hmac, hashlib, base64
from .settings import settings

def validate_twilio_signature(url: str, params: dict, signature: str) -> bool:
    """
    Validate X-Twilio-Signature header (optional in dev, recommended in prod).
    """
    s = url
    # Twilio signature expects concatenated params sorted by key
    for key in sorted(params.keys()):
        s += key + str(params[key])
    mac = hmac.new(settings.twilio_auth_token.encode(), s.encode(), hashlib.sha1)
    digest = base64.b64encode(mac.digest()).decode()
    return hmac.compare_digest(digest, signature)
