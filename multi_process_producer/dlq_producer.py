from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField
import time
from helpers import get_base_config, get_schema_str


def produce_to_dlq_topic(msg, schema_registry_client, error, producer, dlq_topic = "base-topic.dlq"):

    dlq_serializer = AvroSerializer(schema_registry_client=schema_registry_client, schema_str=get_schema_str(file_name="dlq_schema-v1.avsc"))

    payload = {
        "error": str(error),
        "raw_payload": str(msg.value()),
        "topic": msg.topic(),
        "partition": msg.partition(),
        "offset": msg.offset(),
        "timestamp": int(time.time() * 1000)
    }

    try:

        producer.produce(
            topic=dlq_topic,
            value=dlq_serializer(payload, SerializationContext(dlq_topic, MessageField.VALUE))
        )

        producer.flush()

        return True
    
    except Exception as e:
        print(f"An error has occured...: {e}")

    






