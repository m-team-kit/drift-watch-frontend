"""Configuration module for Drift Watch API client."""

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Settings class for the Drift Watch API client.

    This class encapsulates the configuration settings required to interact with the Drift Watch API,
    including the API scheme, host, version, authorization scheme, and timeout duration.
    """

    # Configuration for case sensitivity of environment variable overrides
    model_config = SettingsConfigDict(
        case_sensitive=False,  # Environment variables are not case-sensitive
    )

    # API connection details
    DRIFT_WATCH_SCHEME: str = "https"  # Scheme for API (e.g., 'http' or 'https')
    DRIFT_WATCH_HOST: str = "drift-watch.dev.ai4eosc.eu"  # API host domain
    DRIFT_WATCH_VERSION: str = "latest"  # API version to use

    # Authentication and timeout configurations
    AUTH_SCHEME: str = "Bearer"  # Authorization scheme, e.g., 'Bearer'
    API_TIMEOUT: int = 10  # Timeout in seconds for API requests

    # Pagination settings
    DEFAULT_PAGE: int = 1  # Default page number for paginated requests
    DEFAULT_PAGE_SIZE: int = 99  # Default page size for paginated requests
    
    
    @property
    def base_api_url(self) -> str:
        """
        Constructs and returns the base API URL.

        The base URL is formed using the scheme, host, and optional versioning path if specified.
        The URL format is: "<scheme>://<host>/api/<version>"

        Returns:
            str: The complete base URL for API requests.
        """
        url = f"{self.DRIFT_WATCH_SCHEME}://{self.DRIFT_WATCH_HOST}"
        
        # Append version to URL if specified
        if self.DRIFT_WATCH_VERSION:
            url += f"/api/{self.DRIFT_WATCH_VERSION}"
        

        return url

# Initialize the settings object for use in the application
settings = Settings()
