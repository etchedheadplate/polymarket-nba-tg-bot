from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TG_BOT_TOKEN: str

    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_VHOST: str = "/"

    EXCHANGE_NAME: str = "polymarket.nba"
    QUEUE_TG_BOT: str = "tg_bot"
    QUEUE_ORACLE: str = "oracle"
    QUEUE_REPORT: str = "report"
    RK_REQUEST: str = "request"
    RK_RESPONSE: str = "response"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # pyright: ignore[reportCallIssue]
