import json
import logging
from typing import Callable, Dict, Any
from kafka import KafkaConsumer, KafkaProducer
from threading import Thread
from nlp_analysis_services import SentimentAnalysisService
from misinformation_detection_services import MisinformationDetectionService
from data_normalization_services import DataNormalizationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("data_stream_processor.log")
    ]
)

class DataStreamProcessor:
    def __init__(self, 
                 kafka_brokers: str,
                 input_topic: str,
                 output_topic: str,
                 group_id: str,
                 services: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]]):
        """
        Initialize the DataStreamProcessor.

        Args:
            kafka_brokers (str): Comma-separated Kafka broker addresses.
            input_topic (str): The Kafka topic to consume messages from.
            output_topic (str): The Kafka topic to publish processed messages to.
            group_id (str): The Kafka consumer group ID.
            services (Dict[str, Callable]): Dictionary of processing services to apply to the data.
        """
        self.kafka_consumer = KafkaConsumer(
            input_topic,
            bootstrap_servers=kafka_brokers,
            group_id=group_id,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=kafka_brokers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        self.output_topic = output_topic
        self.services = services

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single message using the configured services.

        Args:
            message (Dict[str, Any]): The input message.

        Returns:
            Dict[str, Any]: The processed message.
        """
        logging.info("Processing message: %s", message)
        for service_name, service in self.services.items():
            try:
                message = service(message)
                logging.info("Applied %s service.", service_name)
            except Exception as e:
                logging.error("Error in service '%s': %s", service_name, str(e))
                message["errors"] = message.get("errors", []) + [f"{service_name}: {str(e)}"]
        return message

    def run(self):
        """
        Start consuming messages, process them, and publish the results.
        """
        logging.info("Starting DataStreamProcessor...")

        def consume_and_process():
            for msg in self.kafka_consumer:
                message = msg.value
                processed_message = self.process_message(message)
                self.kafka_producer.send(self.output_topic, processed_message)
                logging.info("Message processed and sent to output topic.")

        thread = Thread(target=consume_and_process)
        thread.start()
        logging.info("DataStreamProcessor is running.")

# Example usage
if __name__ == "__main__":
    kafka_brokers = "localhost:9092"
    input_topic = "raw_data"
    output_topic = "processed_data"
    group_id = "data_processor_group"

    services = {
        "sentiment_analysis": SentimentAnalysisService().analyze,
        "misinformation_detection": MisinformationDetectionService().detect,
        "data_normalization": DataNormalizationService().normalize
    }

    processor = DataStreamProcessor(
        kafka_brokers=kafka_brokers,
        input_topic=input_topic,
        output_topic=output_topic,
        group_id=group_id,
        services=services
    )
    processor.run()
