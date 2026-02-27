from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TG_BOT_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # pyright: ignore[reportCallIssue]
