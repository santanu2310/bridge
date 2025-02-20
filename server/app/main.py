import contextlib
from collections.abc import AsyncIterator
from typing import TypedDict
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import router

from app.background_tasks import (
    watch_user_updates,
    handle_online_status_update,
    watch_message_updates,
    distribute_published_messages,
    watch_friend_requests,
)

from app.core.db import (
    AsyncDatabase,
    SyncDatabase,
    create_async_client,
    create_sync_client,
)
from app.core.config import AIOKafkaProducer, create_kafka_producer, settings


class State(TypedDict):
    async_db: AsyncDatabase
    sync_db: SyncDatabase
    kafka_producer: AIOKafkaProducer


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[State]:
    asyncio.create_task(watch_friend_requests())

    async with create_kafka_producer() as kafka_producer:
        async_cleint = create_async_client()
        sync_client = create_sync_client()

        print("Lifespan yield: resources ready")
        yield {
            "async_db": AsyncDatabase(async_cleint, settings.DATABASE_NAME),
            "sync_db": SyncDatabase(sync_client, settings.DATABASE_NAME),
            "kafka_producer": kafka_producer,
        }

        print("Lifespan shutdown: closing resources")
        async_cleint.close()
        sync_client.close()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    origins = ["http://localhost:8000", "http://localhost:5173"]

    app.include_router(router=router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()


# @app.on_event("startup")
# async def run_background_task():
#     asyncio.create_task(watch_friend_requests())
#     # asyncio.create_task(watch_user_updates())
#     # asyncio.create_task(handle_online_status_update())
#     # asyncio.create_task(watch_message_updates())
#     # asyncio.create_task(distribute_published_messages())


@app.on_event("startup")
async def run_background_task():
    print("Startup event triggered")
    asyncio.create_task(watch_friend_requests())
