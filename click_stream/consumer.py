"""
Kafka Avro Consumer with DLQ Support

This module sets up a Kafka consumer that consumes Avro-encoded messages,
deserializes them using a schema registry, and handles deserialization errors
by sending failed records to a Dead Letter Queue (DLQ) Kafka topic.

Modules:
- confluent_kafka: Kafka client and schema registry support
- dotenv: Environment variable loader
- logging: Logging for error and info messages
- json: Used for serializing DLQ payloads

Functions:
- send_to_dlq(): Sends failed records to a DLQ topic
- set_up_avro_dser(): Initializes and returns an AvroDeserializer
- main(): Entry point for running the consumer
"""
import os
import json
import logging
from dotenv import load_dotenv

from helpers import get_base_config, get_schema_registry_conf, get_schema, send_to_dlq

from confluent_kafka import Consumer, Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField


def set_up_avro_dser(schema_file_name=None):
    """
    Sets up the Avro deserializer using the schema registry.

    Parameters:
    - schema_file_name (str, optional): The name of the Avro schema file to load.

    Returns:
    - AvroDeserializer: Deserializer configured with the provided schema.
    """
    schema_registry_conf = get_schema_registry_conf()
    schema_str = None

    if schema_registry_conf is None:
        raise ValueError("Cannot load schema registry config.")
    
    if schema_file_name is not None:
        schema_str = get_schema(schema_name=schema_file_name)
        if schema_str is None:
            raise FileNotFoundError("Schema file does not exists...")
    
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    avro_dserializer = AvroDeserializer(schema_registry_client=schema_registry_client, schema_str=schema_str)

    return avro_dserializer


def main():
    """
    Main function that initializes the Kafka consumer and producer, subscribes
    to the topic, and continuously polls for messages.

    On successful message receipt, the Avro deserializer is used.
    If deserialization fails, the message is sent to a DLQ.
    """
    topic = os.environ.get("TOPIC_NAME")

    CONSUMER_CONFIG = {
        **get_base_config(),

        "group.id": f"{topic}_group",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
        "auto.commit.interval.ms": 10_000,
        'heartbeat.interval.ms': 3000,  # consumer pings broker every 3sec to prove its alive
        'session.timeout.ms': 10_000, # broker assumes the consumer has failed and redistributes partitions to another consumer after 10sec
        "request.timeout.ms": 30_000, # max time the consumer waits for a resposne from the broker

        # maximum delay between poll() calls before the consumer is considered dead. Useful if processing takes long.
        "max.poll.interval.ms": 300_000,  # 5 minutes (default is 5 min)

        # bytes to fetch per partition per request
        "fetch.max.bytes": 10 * 1024 * 1024,  # 10 MB

        "fetch.min.bytes": 1_048_576,  # 1 MB

        # memory the consumer will use to buffer fetched records.
        "queued.max.messages.kbytes": 20480  # 20 MB
    }

    consumer = Consumer(CONSUMER_CONFIG)

    producer = Producer(get_base_config())

    consumer.subscribe([topic])

    avro_dserializer = set_up_avro_dser()

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        try:
            msg = avro_dserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))
            logging.info(msg)
        except Exception as e:
            logging.error(f"An error occured while trying to dserialize the object..: {e}")
            logging.info("Sending to dlq...")

            # preparing dlq payload

            dlq_payload = {
                "error": str(e),
                "source": "consumer",
                "raw_value": msg.value().hex(),  # use .hex() to safely send binary
                "topic": msg.topic(),
                "partition": msg.partition(),
                "offset": msg.offset(),
                "key": msg.key().decode('utf-8') if msg.key() else None,
                "timestamp": msg.timestamp()
            }

            try:
                send_to_dlq(record=dlq_payload, topic=os.environ.get("TOPIC_NAME_DLQ"), producer=producer)
            except Exception as e:
                logging.error(f"An error occured while trying to send to dlq topic..{e}")


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    load_dotenv()

    main()