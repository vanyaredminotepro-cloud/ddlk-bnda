from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ddlk-banda"
    database_url: str = "sqlite:///./ddlk_banda.db"

    model_config = SettingsConfigDict(env_prefix="DDLK_", env_file=".env", extra="ignore")


settings = Settings()
