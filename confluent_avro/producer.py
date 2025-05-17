import os
import logging
from dotenv import load_dotenv
from helpers import get_base_config, get_schema_str, generate_user_event

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField, StringSerializer

BASE_CONF = get_base_config()
print(BASE_CONF)

load_dotenv()

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

    PRODUCER_CONF = {
        "acks": -1, 
        "linger.ms": 10,
        "batch.size": 5 * 1024,
        "batch.num.messages":  100,

        "queue.buffering.max.messages": 1000,
        "queue.buffering.max.kbytes": 25 * 1024,

        "retries": 3,
        "enable.idempotence": True,
        "retry.backoff.ms": 500,

        "compression.type": "snappy"
    }

    BASE_CONF.update(PRODUCER_CONF)

    SCHEMA_REGISTRY_CONF = {
        "url": os.environ.get("SCHEMA_REGISTRY_URL"),
        "basic.auth.user.info":  os.environ.get("SCHEMA_REGISTRY_BASIC_AUTH")
    }
    schema_str = get_schema_str(file_name="user_event-v3.avsc")
    schema_registry_client = SchemaRegistryClient(SCHEMA_REGISTRY_CONF)

    string_serializer = StringSerializer()
    avro_serializer = AvroSerializer(schema_registry_client=schema_registry_client, schema_str=schema_str)

    producer = Producer(BASE_CONF)
    while True:
        try:
            record = generate_user_event()
            producer.produce(
                topic="base-topic",
                key=string_serializer(record["session_id"]),
                value=avro_serializer(record, SerializationContext("base-topic", field=MessageField.VALUE)),
                on_delivery=delivery_report
                )
            producer.flush()
        # except BufferError:
        #     producer.flush()

        except KeyboardInterrupt:
            logging.info("Stopping....")
        except Exception as e:
            logging.error(f"An error occured: {e}")
        


if __name__ == "__main__":
    logging.basicConfig(level="INFO")



    main()