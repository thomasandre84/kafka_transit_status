"""Producer base-class providing common utilites and functionality"""
import logging
import time


from confluent_kafka import avro
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.avro import AvroProducer

logger = logging.getLogger(__name__)

BROKER_URL = "PLAINTEXT://localhost:9092"
REGISTRY_URL = "http://localhost:8081"

class Producer:
    """Defines and provides common functionality amongst Producers"""

    # Tracks existing topics across all Producer instances
    existing_topics = set([])

    def __init__(
        self,
        topic_name,
        key_schema,
        value_schema=None,
        num_partitions=1,
        num_replicas=1,
    ):
        """Initializes a Producer object with basic settings"""
        self.topic_name = topic_name
        self.key_schema = key_schema
        self.value_schema = value_schema
        self.num_partitions = num_partitions
        self.num_replicas = num_replicas

        #
        #
        # Configure the broker properties below. Make sure to reference the project README
        # and use the Host URL for Kafka and Schema Registry!
        #
        #
        self.broker_properties = {
            "bootstrap.servers": BROKER_URL,
            "schema.registry.url": REGISTRY_URL
        }

        self.topic = NewTopic(topic=self.topic_name, num_partitions=self.num_partitions,
                              replication_factor=self.num_replicas)
        # If the topic does not already exist, try to create it
        if self.topic_name not in Producer.existing_topics:
            self.create_topic()
            Producer.existing_topics.add(self.topic_name)

        # Configure the AvroProducer
        self.producer = AvroProducer(
            self.broker_properties,
            default_value_schema=self.value_schema,
            default_key_schema=self.key_schema
        )

    def create_topic(self):
        """Creates the producer topic if it does not already exist"""
        #
        #
        # Write code that creates the topic for this producer if it does not already exist on
        # the Kafka Broker.
        #
        #
        client = AdminClient({"bootstrap.servers": BROKER_URL})
        futures = client.create_topics(
                [self.topic]
            )
        for _, future in futures.items():
            try:
                future.result()
                logger.info(f"topic creation kafka integration for Topic {self.topic_name}")
            except Exception as e:
                logger.warning(f"Could not Create Topic {self.topic_name}")



    def time_millis(self):
        return int(round(time.time() * 1000))

    def close(self):
        """Prepares the producer for exit by cleaning up the producer"""
        #
        #
        # Write cleanup code for the Producer here
        #
        #
        client = AdminClient({"bootstrap.servers": BROKER_URL})
        client.delete_topics([self.topic])
        logger.info(f"producer closed for Topic {self.topic_name}")

    def time_millis(self):
        """Use this function to get the key for Kafka Events"""
        return int(round(time.time() * 1000))
