import logging
import os
from helpers import get_base_config, get_schema
from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

def set_avro_dserializer():
    schema_registry_client = SchemaRegistryClient(
        conf={
            "url": os.environ.get("SCHEMA_REGISTRY_URL"),
            "basic.auth.user.info": os.environ.get("SCHEMA_REGISTRY_BASIC_AUTH")
        }
    )

    avro_dserializer = AvroDeserializer(schema_registry_client=schema_registry_client, schema_str=get_schema())

    return avro_dserializer

def main():
    config = {
        **get_base_config(),

        "group.id": "user_event_group",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
        "auto.commit.interval.ms": 10_000,

        'max.poll.interval.ms': 300000,
        'session.timeout.ms': 10_000,
        'heartbeat.interval.ms': 3000

    }
    consumer = Consumer(config)

    consumer.subscribe(["user_events"])

    avro_dserializer = set_avro_dserializer()

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        try:
            msg = avro_dserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))
            logging.info(msg)
        except Exception as e:
            logging.error(f"An error occured while dserialising....{e}")

if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    main()
