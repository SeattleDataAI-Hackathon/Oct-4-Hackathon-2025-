from pydantic import BaseModel

class AIResult(BaseModel):
    image_quality: dict
    observed_features: list[str]
    triage_bucket: str
    explanations: list[str]
