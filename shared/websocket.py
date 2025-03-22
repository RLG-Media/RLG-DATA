from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
import logging
from shared.error_handling import APIError

# Initialize Flask and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure logging for debugging purposes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("websocket")

# Dictionary to track connected users
active_users = {}


@socketio.on("connect")
def handle_connect():
    """
    Handle new client connection.
    """
    user_id = request.args.get("user_id")
    if not user_id:
        logger.warning("Connection attempt without user_id.")
        disconnect()
        return
    
    active_users[user_id] = request.sid
    logger.info(f"User {user_id} connected. SID: {request.sid}")
    emit("connected", {"message": f"Welcome user {user_id}!"}, to=request.sid)


@socketio.on("disconnect")
def handle_disconnect():
    """
    Handle client disconnection.
    """
    user_id = next((uid for uid, sid in active_users.items() if sid == request.sid), None)
    if user_id:
        del active_users[user_id]
        logger.info(f"User {user_id} disconnected.")
    else:
        logger.warning(f"Disconnected session without an associated user.")


@socketio.on("join_room")
def handle_join_room(data):
    """
    Handles a client joining a specific room.

    Args:
        data (dict): Contains 'room' and optional 'user_id'.
    """
    room = data.get("room")
    user_id = data.get("user_id")
    
    if not room:
        emit("error", {"error": "Room name is required."}, to=request.sid)
        return

    join_room(room)
    logger.info(f"User {user_id} joined room {room}.")
    emit("room_joined", {"message": f"User {user_id} joined room {room}."}, room=room)


@socketio.on("leave_room")
def handle_leave_room(data):
    """
    Handles a client leaving a specific room.

    Args:
        data (dict): Contains 'room' and optional 'user_id'.
    """
    room = data.get("room")
    user_id = data.get("user_id")

    if not room:
        emit("error", {"error": "Room name is required."}, to=request.sid)
        return

    leave_room(room)
    logger.info(f"User {user_id} left room {room}.")
    emit("room_left", {"message": f"User {user_id} left room {room}."}, room=room)


@socketio.on("send_message")
def handle_send_message(data):
    """
    Handle broadcasting a message to a room.

    Args:
        data (dict): Contains 'message', 'room', and optional 'user_id'.
    """
    message = data.get("message")
    room = data.get("room")
    user_id = data.get("user_id")

    if not message or not room:
        emit("error", {"error": "Message and room are required."}, to=request.sid)
        return

    logger.info(f"User {user_id} sent a message to room {room}: {message}")
    emit("new_message", {"user_id": user_id, "message": message}, room=room)


@socketio.on("private_message")
def handle_private_message(data):
    """
    Handles sending a private message to a specific user.

    Args:
        data (dict): Contains 'recipient_id', 'message', and optional 'sender_id'.
    """
    recipient_id = data.get("recipient_id")
    message = data.get("message")
    sender_id = data.get("sender_id")

    if not recipient_id or not message:
        emit("error", {"error": "Recipient ID and message are required."}, to=request.sid)
        return

    recipient_sid = active_users.get(recipient_id)
    if not recipient_sid:
        emit("error", {"error": f"User {recipient_id} is not online."}, to=request.sid)
        return

    logger.info(f"User {sender_id} sent a private message to {recipient_id}: {message}")
    emit("private_message", {"sender_id": sender_id, "message": message}, to=recipient_sid)


@socketio.on_error()
def handle_error(e):
    """
    General error handler for WebSocket events.
    """
    logger.error(f"An error occurred: {str(e)}")
    emit("error", {"error": "An unexpected error occurred."})


@socketio.on_error_default
def default_error_handler(e):
    """
    Catch-all error handler for undefined events.
    """
    logger.error(f"Unhandled error: {str(e)}")
    emit("error", {"error": "An unexpected error occurred."})


# Utility Functions
def broadcast_event(event, data):
    """
    Broadcast a custom event to all connected clients.

    Args:
        event (str): The name of the event.
        data (dict): The data to send.
    """
    socketio.emit(event, data)
    logger.info(f"Broadcast event '{event}' with data: {data}")


def emit_to_user(user_id, event, data):
    """
    Send an event to a specific user.

    Args:
        user_id (str): The ID of the recipient user.
        event (str): The name of the event.
        data (dict): The data to send.
    """
    recipient_sid = active_users.get(user_id)
    if recipient_sid:
        socketio.emit(event, data, to=recipient_sid)
        logger.info(f"Emitted event '{event}' to user {user_id}: {data}")


# If running standalone
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
