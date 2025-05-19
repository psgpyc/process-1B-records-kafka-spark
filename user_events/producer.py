import os
import logging

from pprint import pprint
from helpers import get_base_config, get_schema, generate_user_event
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField, StringSerializer

def set_avro_serializer():
    schema_registry_client = SchemaRegistryClient(
        conf={
            "url": os.environ.get("SCHEMA_REGISTRY_URL"),
            "basic.auth.user.info": os.environ.get("SCHEMA_REGISTRY_BASIC_AUTH")
        }
    )

    avro_serializer = AvroSerializer(schema_registry_client=schema_registry_client, schema_str=get_schema())

    return avro_serializer

def delivery_report(err, msg):
    """
        This callback function is called once a message is delivered to Kafka.
        It logs the success or failure of the message delivery.
    """
    if err is not None:
        logging.error(f"Delivery failed for User record {msg.key()}: {err}")
        return
    logging.info(f'User record { msg.key()} successfully produced to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')

def main():
    configs = {
        **get_base_config(),
        'linger.ms': 10,
        'batch.size': 20 * 1024, # 20KB
        'batch.num.messages': 100,

        'queue.buffering.max.messages': 100_000,
        'queue.buffering.max.kbytes': 100 * 1024,

        'retries': 3,
        'enable.idempotence': True,
        'retry.backoff.ms': 500,

        'compression.type': 'snappy'   
    }

    producer = Producer(configs)
    string_serializer = StringSerializer()
    avro_serializer = set_avro_serializer()

    record = generate_user_event()

    try:
        producer.produce(
            topic="user_events",
            key=string_serializer(record.get("session_id")),
            value=avro_serializer(record, SerializationContext("user_events", MessageField.VALUE)),
            on_delivery=delivery_report)
        producer.flush()
    except Exception as e:
        logging.error(f"An error occured while trying to producing to the cluster.")

if __name__ == "__main__":
    logging.basicConfig(level="INFO")

    main()
