import os
import logging
from dotenv import load_dotenv
from helpers import get_base_config, get_schema_str
from confluent_kafka import Consumer

from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

BASE_CONFIG = get_base_config()
load_dotenv()

def main():
    CONSUMER_CONF = {
        "group.id":  "base-group",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
        'auto.commit.interval.ms': 10_000,
        'max.poll.interval.ms': 300000,
        'session.timeout.ms': 10_000,
        'heartbeat.interval.ms': 3000
    }

    BASE_CONFIG.update(CONSUMER_CONF)
    SCHEMA_REGISTRY_CONF = {
        "url": os.environ.get("SCHEMA_REGISTRY_URL"),
        "basic.auth.user.info": os.environ.get("SCHEMA_REGISTRY_BASIC_AUTH")
    }

    consumer = Consumer(BASE_CONFIG)
    consumer.subscribe(['base-topic'])

    schema_registry_client = SchemaRegistryClient(SCHEMA_REGISTRY_CONF)

    # using schema evolution
    schema_str=get_schema_str(file_name="user_event-v2.avsc")
    avro_dserializer = AvroDeserializer(schema_registry_client=schema_registry_client)

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logging.error(f"An error occured: {msg.error()}")
            else:
                msg = avro_dserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))
                logging.info(msg)
    except Exception as e:
        logging.error(f"An error has occured: {e}")
        

if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    main()