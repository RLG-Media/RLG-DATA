# real_time_notifications.py

import time
import threading
import requests

class RealTimeNotifications:
    """
    RealTimeNotifications class to handle sending and receiving real-time notifications.
    """
    def __init__(self, notification_api_url, notification_service_key):
        """
        Initializes the RealTimeNotifications with API URL and service key.

        :param notification_api_url: Base URL for the notification service API.
        :param notification_service_key: Service key for authentication with the notification service.
        """
        self.notification_api_url = notification_api_url
        self.notification_service_key = notification_service_key
        self.subscribers = {}

    def _get_headers(self):
        """
        Generates the headers required for API requests.

        :return: A dictionary containing the headers including the service key.
        """
        return {
            'Authorization': f'Bearer {self.notification_service_key}',
            'Content-Type': 'application/json'
        }

    def _send_notification(self, endpoint, method='POST', data=None):
        """
        Sends a notification to the specified endpoint.

        :param endpoint: API endpoint relative to the notification service URL.
        :param method: HTTP method (POST, GET).
        :param data: Payload for the notification.
        :return: JSON response from the notification service.
        """
        url = f"{self.notification_api_url}{endpoint}"
        headers = self._get_headers()

        if method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'GET':
            response = requests.get(url, headers=headers, params=data)

        if response.status_code not in [200, 201]:
            raise Exception(f"Error {response.status_code}: {response.text}")
        return response.json()

    def subscribe(self, subscriber_id, callback_url):
        """
        Subscribes a user to receive real-time notifications.

        :param subscriber_id: Unique identifier for the subscriber.
        :param callback_url: URL where notifications should be sent.
        :return: Confirmation from the service.
        """
        self.subscribers[subscriber_id] = callback_url
        data = {'subscriber_id': subscriber_id, 'callback_url': callback_url}
        response = self._send_notification('/subscribe', data=data)
        return response

    def unsubscribe(self, subscriber_id):
        """
        Unsubscribes a user from receiving real-time notifications.

        :param subscriber_id: Unique identifier for the subscriber.
        :return: Confirmation from the service.
        """
        if subscriber_id in self.subscribers:
            del self.subscribers[subscriber_id]
            response = self._send_notification('/unsubscribe', data={'subscriber_id': subscriber_id})
            return response
        else:
            raise ValueError(f"No subscription found for subscriber_id: {subscriber_id}")

    def send_notification(self, message, subscribers_list=None):
        """
        Sends a real-time notification to subscribed users.

        :param message: The content/message of the notification.
        :param subscribers_list: Optional list of specific subscribers to notify.
        :return: Responses from all notified subscribers.
        """
        responses = []
        target_subscribers = subscribers_list if subscribers_list else self.subscribers.keys()
        for subscriber_id in target_subscribers:
            callback_url = self.subscribers[subscriber_id]
            notification_payload = {
                'subscriber_id': subscriber_id,
                'message': message
            }
            response = self._send_notification(callback_url, method='POST', data=notification_payload)
            responses.append(response)
        return responses

    def listen_for_notifications(self):
        """
        Listens for incoming notifications and handles them accordingly.
        This is intended to be run in a separate thread for real-time event handling.
        """
        while True:
            # Simulate listening to notifications (this should be replaced with actual real-time listener)
            time.sleep(10)
            print("Checking for new notifications...")  # Placeholder for actual notification check
            # You can add logic to process received notifications here

    def start_listener(self):
        """
        Starts the listener for incoming notifications in a separate thread.
        """
        listener_thread = threading.Thread(target=self.listen_for_notifications)
        listener_thread.daemon = True
        listener_thread.start()
        print("Listener started for real-time notifications.")
