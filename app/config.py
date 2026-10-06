from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Production ML Image Classification API"
    app_version: str = "1.0.0"
    environment: str = "development"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    model_version: str = "v1"
    max_image_size_mb: int = 5 # "5242850 bites max"
    allowed_image_types: str = "image/jpeg,image/png,image/webp"
    cache_ttl_seconds:int = 86400 # max 24 hrs time limit to delete
    model_config = SettingsConfigDict(
        env_file = ".env",
        case_sensitive=False,
        extra = "ignore"
    )
    @property # we are calling those properties
    def max_image_size_bytes(self) -> int: #expected to return in int form
        return self.max_image_size_mb * 1024 * 1024

    @property
    def allowed_image_type_list(self) -> list[str]: # expected to return in list of string
        return [
            image_type.strip()
            for image_type in self.allowed_image_types.split(",")
        ]


settings = Settings()

