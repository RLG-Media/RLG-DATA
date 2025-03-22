from flask import Blueprint, jsonify, request
from celery.result import AsyncResult
from datetime import datetime
from celery import current_app as celery_app

# Define the Blueprint for task monitoring routes
task_monitoring = Blueprint('task_monitoring', __name__)

# Endpoint to get the status of a specific task
@task_monitoring.route('/task_status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """
    Retrieves the status and result of a specific task.
    :param task_id: ID of the task to query
    :return: JSON object with task status and result
    """
    task_result = AsyncResult(task_id)
    response = {
        'task_id': task_id,
        'status': task_result.status,
        'result': task_result.result if task_result.ready() else None,
        'date_checked': datetime.utcnow()
    }
    return jsonify(response)

# Endpoint to list all tasks with their statuses
@task_monitoring.route('/list_tasks', methods=['GET'])
def list_all_tasks():
    """
    Lists all tasks with their current status.
    :return: JSON array of all task statuses
    """
    i = celery_app.control.inspect()
    active_tasks = i.active()
    reserved_tasks = i.reserved()
    scheduled_tasks = i.scheduled()
    
    tasks = {
        'active': active_tasks,
        'reserved': reserved_tasks,
        'scheduled': scheduled_tasks
    }

    response = {
        'tasks': tasks,
        'date_checked': datetime.utcnow()
    }
    return jsonify(response)

# Endpoint to get the result of a completed task
@task_monitoring.route('/task_result/<task_id>', methods=['GET'])
def get_task_result(task_id):
    """
    Retrieves the result of a completed task.
    :param task_id: ID of the task
    :return: JSON object with task result if available
    """
    task_result = AsyncResult(task_id)
    if task_result.ready():
        response = {
            'task_id': task_id,
            'status': task_result.status,
            'result': task_result.result,
            'completed_at': datetime.utcnow()
        }
    else:
        response = {
            'task_id': task_id,
            'status': task_result.status,
            'message': 'Task is not completed yet.',
            'checked_at': datetime.utcnow()
        }
    return jsonify(response)

# Endpoint to cancel a specific task
@task_monitoring.route('/cancel_task/<task_id>', methods=['POST'])
def cancel_task(task_id):
    """
    Cancels a specific task if it is in progress or pending.
    :param task_id: ID of the task to cancel
    :return: JSON response indicating success or failure of cancellation
    """
    task_result = AsyncResult(task_id)
    if task_result.status in ['PENDING', 'STARTED']:
        celery_app.control.revoke(task_id, terminate=True)
        response = {
            'task_id': task_id,
            'status': 'CANCELLED',
            'message': 'Task has been cancelled.',
            'cancelled_at': datetime.utcnow()
        }
    else:
        response = {
            'task_id': task_id,
            'status': task_result.status,
            'message': 'Task cannot be cancelled.',
            'checked_at': datetime.utcnow()
        }
    return jsonify(response)

# Register the Blueprint in your main application or app factory
# app.register_blueprint(task_monitoring, url_prefix='/monitor')
