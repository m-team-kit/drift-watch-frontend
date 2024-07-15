"""Configuration module for drift_monitor detection client."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings class for drift_monitor detection client."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
    )

    DRIFT_MONITOR_SCHEME: str = "http"
    DRIFT_MONITOR_HOST: str = "localhost"
    DRIFT_MONITOR_PORT: int = 5000
    DRIFT_MONITOR_VERSION: str = ""
    DRIFT_MONITOR_TIMEOUT: int = 10


# Initialize the settings object
settings = Settings()
monitoring_url = (
    f"{settings.DRIFT_MONITOR_SCHEME}:"
    f"//{settings.DRIFT_MONITOR_HOST}"
    f":{settings.DRIFT_MONITOR_PORT}"
)
if settings.DRIFT_MONITOR_VERSION:
    api_prefix = f"/api/{settings.DRIFT_MONITOR_VERSION}"
    monitoring_url += api_prefix
