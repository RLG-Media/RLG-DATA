import time
import threading
from queue import Queue
from typing import Callable, Any, Dict

class RealTimeDataProcessor:
    """
    A class to process real-time data efficiently with support for custom callbacks.
    """
    def __init__(self, buffer_size: int = 100):
        """
        Initializes the RealTimeDataProcessor.

        :param buffer_size: Maximum size of the data buffer.
        """
        self.data_queue = Queue(maxsize=buffer_size)
        self.callbacks = []
        self.is_running = False
        self.worker_thread = None

    def add_callback(self, callback: Callable[[Any], None]):
        """
        Registers a callback function to process data.

        :param callback: A callable function to handle processed data.
        """
        if callable(callback):
            self.callbacks.append(callback)
        else:
            raise ValueError("Callback must be a callable function.")

    def push_data(self, data: Any):
        """
        Pushes data to the processing queue.

        :param data: The data to be pushed into the queue.
        """
        if not self.data_queue.full():
            self.data_queue.put(data)
        else:
            print("Warning: Data queue is full. Discarding data.")

    def _process_data(self):
        """
        Internal method to process data from the queue.
        """
        while self.is_running:
            try:
                data = self.data_queue.get(timeout=1)
                self._execute_callbacks(data)
            except Exception:
                pass  # Handle timeout gracefully

    def _execute_callbacks(self, data: Any):
        """
        Executes all registered callbacks with the provided data.

        :param data: The data to be processed by the callbacks.
        """
        for callback in self.callbacks:
            try:
                callback(data)
            except Exception as e:
                print(f"Error executing callback: {e}")

    def start(self):
        """
        Starts the real-time data processing thread.
        """
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._process_data, daemon=True)
            self.worker_thread.start()
            print("Real-time data processor started.")

    def stop(self):
        """
        Stops the real-time data processing thread.
        """
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join()
            print("Real-time data processor stopped.")

    def status(self) -> Dict[str, Any]:
        """
        Provides the status of the processor.

        :return: A dictionary with the current status.
        """
        return {
            "is_running": self.is_running,
            "queue_size": self.data_queue.qsize(),
            "callbacks_count": len(self.callbacks),
        }


# Example usage
if __name__ == "__main__":
    def sample_callback(data):
        print(f"Processing data: {data}")

    processor = RealTimeDataProcessor(buffer_size=50)
    processor.add_callback(sample_callback)

    # Simulate pushing data
    processor.start()
    for i in range(100):
        processor.push_data({"id": i, "value": f"Data-{i}"})
        time.sleep(0.05)

    time.sleep(2)
    processor.stop()
    print("Processor status:", processor.status())
