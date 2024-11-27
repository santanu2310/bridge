import asyncio
from bson import ObjectId
from fastapi import APIRouter, Depends, WebSocket
from ..schemas import SyncSocketMessage, UserOut
from ..deps import get_user_from_access_token

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connection: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connection[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connection:
            del self.active_connection[user_id]

    def is_online(self, user_id: str):
        return user_id in self.active_connection

    async def send_personal_message(self, user_id: str, message: SyncSocketMessage):
        self.active_connection[user_id].send_text(message.model_dump_json())


connections = ConnectionManager()


@router.websocket("/socket")
async def websocket_endpoint(
    websocket: WebSocket, user: UserOut = Depends(get_user_from_access_token)
):
    await connections.connect(user.id, websocket)

    try:
        while True:
            await websocket.send_text("ping")
            await asyncio.sleep(30)

    except WebSocketDisconnect:
        connections.disconnect(user.id)
    return


async def send_message(user_ids: [ObjectId], message: SyncSocketMessage):
    try:
        for user_id in user_ids:
            if connections.is_online(str(user_id)):
                connections.send_personal_message(str(user_id), message)
    except Exception as e:
        print(e)
