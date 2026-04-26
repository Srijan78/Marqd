"""
Marqd Backend Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-fallback-key")
    API_KEY = os.getenv("API_KEY")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///marqd.db"
    )

    # Google Cloud
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "marqd-assets")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

    # External APIs
    SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

    # App settings
    USE_MOCK_APIS = os.getenv("USE_MOCK_APIS", "true").lower() == "true"
    SCAN_INTERVAL_HOURS = int(os.getenv("SCAN_INTERVAL_HOURS", "24"))

    # File uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
    TEMP_FOLDER = os.path.join(os.path.dirname(__file__), "temp")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
    ALLOWED_VIDEO_EXTENSIONS = {"mp4", "mov"}


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = "development"


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = "production"


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}


def get_config():
    env = os.getenv("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)
