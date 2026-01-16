from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List
import secrets

class Settings(BaseSettings):
    PROJECT_NAME: str = "Lion Delivery BOT"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # CORS - Security: Restrict origins in production
    CORS_ORIGINS: str = "*"  # Comma-separated list of allowed origins

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS into a list"""
        if self.CORS_ORIGINS == "*":
            if self.ENVIRONMENT == "production":
                # In production, require explicit origins
                return ["https://liondelivery.com", "https://admin.liondelivery.com"]
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # Database - No default password for security
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str  # Required, no default
    POSTGRES_DB: str = "lionbot"
    DATABASE_URL: Optional[str] = None

    # Database Pool Settings
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 300
    DB_POOL_TIMEOUT: int = 30

    # Security - Generate secure default if not provided
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v):
        if v == "YOUR_SECRET_KEY_HERE" or len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters. Generate with: python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
        return v

    @field_validator('FIRST_SUPERUSER_PASSWORD')
    @classmethod
    def validate_admin_password(cls, v):
        weak_passwords = ['password', '123456', 'admin', 'lionbot', 'password123']
        if v.lower() in weak_passwords or len(v) < 8:
            raise ValueError("FIRST_SUPERUSER_PASSWORD must be at least 8 characters and not a common password")
        return v

    # WhatsApp Cloud API
    WHATSAPP_API_TOKEN: Optional[str] = None
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_VERIFY_TOKEN: Optional[str] = None
    WHATSAPP_BUSINESS_ACCOUNT_ID: Optional[str] = None
    WHATSAPP_APP_SECRET: Optional[str] = None

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Google Gemini AI
    GEMINI_API_KEY: Optional[str] = None
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_URL: Optional[str] = None
    
    # Upstash Redis (for serverless)
    UPSTASH_REDIS_REST_URL: Optional[str] = None
    UPSTASH_REDIS_REST_TOKEN: Optional[str] = None
    
    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"  # Default rate limit
    RATE_LIMIT_LOGIN: str = "5/minute"  # Stricter for login attempts
    RATE_LIMIT_WEBHOOK: str = "200/minute"  # Higher for webhooks
    RATE_LIMIT_API: str = "60/minute"  # Standard API endpoints

    # Security Headers
    ENABLE_SECURITY_HEADERS: bool = True
    TRUSTED_HOSTS: str = "*"  # Comma-separated list or *

    # Pricing Configuration
    BASE_DELIVERY_FEE: float = 2.0
    PER_KM_DELIVERY_FEE: float = 0.5
    MIN_DELIVERY_FEE: float = 2.0
    MAX_DELIVERY_FEE: float = 15.0
    FREE_DELIVERY_THRESHOLD: float = 50.0
    SURGE_MULTIPLIER: float = 1.0  # 1.0 = no surge
    DEFAULT_COMMISSION_RATE: float = 0.15  # 15%
    DRIVER_PLATFORM_CUT: float = 0.20  # 20% platform fee on delivery
    TAX_RATE: float = 0.0
    
    # Notifications
    ENABLE_WHATSAPP_NOTIFICATIONS: bool = True
    ENABLE_PUSH_NOTIFICATIONS: bool = True

    # Firebase Cloud Messaging
    FCM_SERVER_KEY: Optional[str] = None
    
    # Admin
    FIRST_SUPERUSER_EMAIL: str = "admin@lionbot.com"
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_PHONE: str = "+1234567890"
    
    # Google Maps (for distance calculation)
    GOOGLE_MAPS_API_KEY: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = ".env"

    def get_database_url(self):
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
    
    def get_redis_url(self):
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    def get_celery_broker_url(self):
        if self.CELERY_BROKER_URL:
            return self.CELERY_BROKER_URL
        return self.get_redis_url()

settings = Settings()

