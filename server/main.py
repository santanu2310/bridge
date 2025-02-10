import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.router import (
    messages,
    user,
    friends,
    sync_sockets,
    conversation,
    message_handlers,
)
from app.background_tasks import (
    watch_user_updates,
    handle_online_status_update,
    watch_message_updates,
    distribute_published_messages,
)

app = FastAPI()

origins = ["http://localhost:8000", "http://localhost:5173"]

app.include_router(messages.router)
app.include_router(message_handlers.router, prefix="/messages")
app.include_router(sync_sockets.router, prefix="/sync")
app.include_router(user.router, prefix="/user")
app.include_router(friends.router, prefix="/friends")
app.include_router(conversation.router, prefix="/conversation")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def run_background_task():
    asyncio.create_task(watch_user_updates())
    asyncio.create_task(handle_online_status_update())
    asyncio.create_task(watch_message_updates())
    asyncio.create_task(distribute_published_messages())
