from celery import Celery  # type: ignore
from pydantic_settings import BaseSettings, SettingsConfigDict
from aiokafka import AIOKafkaProducer  # type: ignore


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="/.env", env_file_encoding="utf-8")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # JWT secrets
    JWT_ACCESS_SECRET_KEY: str = ""
    JWT_REFRESH_SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"

    # Kafka
    KAFKA_CONNECTION: str = "localhost:9092"

    # AWS
    AWS_ACCESS_KEY: str = ""
    AWS_SECRET_KEY: str = ""
    BUCKET_NAME: str = ""

    # Mongodb
    MONGOD_URL: str = (
        "mongodb://127.0.0.1:27017,localhost:27018,localhost:27019/?replicaSet=rs0"
    )
    DATABASE_NAME: str = "bridge"

    CELERY_BROKER_URL: str = "redis://localhost:6379"


settings = Settings()


def create_kafka_producer() -> AIOKafkaProducer:
    return AIOKafkaProducer(bootstrap_servers=settings.KAFKA_CONNECTION)


def create_celery_client() -> Celery:
    return Celery("takss", broker=settings.CELERY_BROKER_URL)


__all__ = [
    "settings",
    "AIOKafkaProducer",
    "create_kafka_producer",
    "create_celery_client",
]
