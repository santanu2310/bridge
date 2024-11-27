from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from starlette.websockets import WebSocket, WebSocketDisconnect
import asyncio

from app.router import messages, user, friends, sync_sockets
from app.background_tasks import watch_user_updates

app = FastAPI()

origins = ["http://localhost:8000", "http://localhost:5173"]

app.include_router(messages.router)
app.include_router(sync_sockets.router, prefix="/sync")
app.include_router(user.router, prefix="/user")
app.include_router(friends.router, prefix="/friends")
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
