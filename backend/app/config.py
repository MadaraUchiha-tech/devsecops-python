from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CareSlot API"
    app_version: str = "1.0.0"
    database_url: str = "postgresql+psycopg://careslot:careslot@localhost:5432/careslot"
    # Populate a few doctors/patients on first start so the demo UI is not empty.
    seed_demo_data: bool = False
    cors_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
