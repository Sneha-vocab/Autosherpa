from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "dev"
    DATABASE_URL: str = "postgresql://neondb_owner:npg_Ldl6Qa1sGTHM@ep-weathered-scene-ad5h9iby-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    LLM_PROVIDER: str = "gemini"    
    LLM_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    WHATSAPP_TOKEN: str | None = None
    WHATSAPP_PHONE_ID: str | None = None  # Bot's WhatsApp Business Phone Number ID (from Meta)
    META_API_VERSION: str = "v17.0"
    FROM_PHONE: str | None = None  # Bot's phone number (optional, currently unused - phone_id is used instead)
    WEBHOOK_VERIFY_TOKEN: str | None = None  # Optional: Webhook verification token for Meta
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env

settings = Settings()
