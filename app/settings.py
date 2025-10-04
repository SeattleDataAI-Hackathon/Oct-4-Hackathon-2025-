from pydantic import BaseModel
import os
from dotenv import load_dotenv
load_dotenv()  


class Settings(BaseModel):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    neon_database_url: str = os.getenv("NEON_DATABASE_URL", "")
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "*")
    env: str = os.getenv("ENV", "dev")

settings = Settings()
