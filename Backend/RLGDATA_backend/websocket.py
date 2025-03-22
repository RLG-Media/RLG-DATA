import logging
from flask import Blueprint, request
from flask_socketio import SocketIO, emit, join_room, leave_room

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create a Blueprint for WebSocket routes
ws_blueprint = Blueprint('ws', __name__)

# Initialize Flask-SocketIO
socketio = SocketIO()

### REAL-TIME UPDATES USING WEBSOCKETS ###

@socketio.on('connect')
def handle_connect():
    """
    Handle a new client connection.
    """
    logging.info(f"Client connected: {request.sid}")
    emit('message', {'data': 'Connected to RLG DATA WebSocket'})


@socketio.on('disconnect')
def handle_disconnect():
    """
    Handle client disconnection.
    """
    logging.info(f"Client disconnected: {request.sid}")


@socketio.on('join_project_room')
def handle_join_project_room(data):
    """
    Handle a user joining a project-specific WebSocket room.
    
    :param data: Data containing the project ID (e.g., {'project_id': 123})
    """
    project_id = data['project_id']
    join_room(str(project_id))
    logging.info(f"Client {request.sid} joined room for project {project_id}")
    emit('message', {'data': f'Joined project room {project_id}'}, room=str(project_id))


@socketio.on('leave_project_room')
def handle_leave_project_room(data):
    """
    Handle a user leaving a project-specific WebSocket room.
    
    :param data: Data containing the project ID (e.g., {'project_id': 123})
    """
    project_id = data['project_id']
    leave_room(str(project_id))
    logging.info(f"Client {request.sid} left room for project {project_id}")
    emit('message', {'data': f'Left project room {project_id}'}, room=str(project_id))


@socketio.on('send_message')
def handle_send_message(data):
    """
    Handle sending a message to a project-specific WebSocket room.
    
    :param data: Data containing the message and project ID (e.g., {'project_id': 123, 'message': 'Hello'})
    """
    project_id = data['project_id']
    message = data['message']
    logging.info(f"Message from client {request.sid} to project {project_id}: {message}")
    emit('message', {'data': message}, room=str(project_id))


### BROADCAST REAL-TIME EVENTS ###

def broadcast_realtime_update(project_id, update_data):
    """
    Broadcast a real-time update to all clients in a specific project room.
    
    :param project_id: The ID of the project to broadcast the update for
    :param update_data: The data to broadcast (e.g., new mention, report update)
    """
    logging.info(f"Broadcasting real-time update for project {project_id}: {update_data}")
    socketio.emit('realtime_update', {'data': update_data}, room=str(project_id))


### HANDLE BACKGROUND TASK UPDATES ###

def handle_background_task_update(project_id, task_status):
    """
    Handle updates from background tasks (e.g., scraping or report generation) and broadcast the result.
    
    :param project_id: The ID of the project
    :param task_status: The current status of the background task (e.g., 'completed', 'in progress')
    """
    update_data = {
        'project_id': project_id,
        'task_status': task_status
    }
    logging.info(f"Handling background task update for project {project_id}: {task_status}")
    broadcast_realtime_update(project_id, update_data)

