from flask import request
from enum import Enum
from src.utils.api_response import ApiResponse
from src.extensions import socketio
import redis

redis_conn = redis.Redis(host='localhost', port=6379, decode_responses=True)

class SocketEvent(str, Enum):
    CONNECT = 'connect'
    DISCONNECT = 'disconnect'
    REGISTER = 'register'
    ECHO = 'echo'
    ECHO_RESPONSE = 'echo_response'
    NOTIFICATION = 'notification'

class SocketService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._register_events()
        return cls._instance

    def _register_events(self):
        @socketio.on(SocketEvent.CONNECT.value)
        def on_connect():
            print(f"[SocketIO] 🔌 Connected: {request.sid}")

        @socketio.on(SocketEvent.DISCONNECT.value)
        def on_disconnect():
            # Search Redis for user with this SID
            for user_id in redis_conn.hkeys("connected_users"):
                if redis_conn.hget("connected_users", user_id) == request.sid:
                    redis_conn.hdel("connected_users", user_id)
                    print(f"[SocketIO] ❌ Disconnected: {user_id}")
                    break

        @socketio.on(SocketEvent.REGISTER.value)
        def on_register(data):
            user_id = data.get("user_id")
            if user_id:
                redis_conn.hset("connected_users", user_id, request.sid)
                print(f"[SocketIO] ✅ Registered {user_id} with SID {request.sid}")

        @socketio.on(SocketEvent.ECHO.value)
        def on_echo(data):
            socketio.emit(SocketEvent.ECHO_RESPONSE.value, {
                "message": data.get("message", "")
            }, to=request.sid)

    def emit_to_user(self, user_id: str, event: SocketEvent, payload: dict) -> ApiResponse:
        sid = redis_conn.hget("connected_users", user_id)
        if not sid:
            return ApiResponse.error("User not connected")

        socketio.emit(event.value, payload, to=sid)
        print(f"[SocketIO] 📤 Sent event '{event.value}' to {user_id}")
        return ApiResponse.success()

    def broadcast(self, event: SocketEvent, data: dict) -> ApiResponse:
        try:
            socketio.emit(event.value, data)
            print(f"[SocketIO] 📢 Broadcasted {event.value}")
            return ApiResponse.success()
        except Exception as e:
            print(f"[SocketIO] Broadcast error: {e}")
            return ApiResponse.error(str(e))

socket_service = SocketService()