from fastapi import APIRouter

from app.api.user.router import router as user_router
from app.api.friends.router import router as friend_router
from app.api.conversation.router import router as conv_router
from app.api.message.router import router as message_router
from app.api.msg_socket.router import router as msg_socket_router
from app.api.sync_socket.router import router as sync_router


router = APIRouter()

router.include_router(router=user_router, prefix="/users")
router.include_router(router=friend_router, prefix="/friends")
router.include_router(router=conv_router, prefix="/conversations")
router.include_router(router=message_router, prefix="/messages")
router.include_router(router=msg_socket_router, prefix="/message/scoket")
router.include_router(router=sync_router, prefix="/sync")
