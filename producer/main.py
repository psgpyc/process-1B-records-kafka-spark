import logging
from pathlib import Path
from factory import generate_user_event
from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.admin import AdminClient, ConfigResource, ConfigEntry, NewTopic
from config import ADMIN_CONFIG, TOPIC_NAME, SCHEMA_REGISTRY_CONF, SCHEMA_PATH, PRODUCER_CONF

client = AdminClient(ADMIN_CONFIG)

def get_topic_list():
    return client.list_topics().topics.keys()


if TOPIC_NAME not in get_topic_list():
    logging.info("Topic not found. Entering creation logic......")
    topic = NewTopic(
        topic=TOPIC_NAME,
        num_partitions=10, 
        replication_factor=3)
    try:
        client.create_topics([topic])
        logging.info(f"topic[{TOPIC_NAME}] successfully created..")
    except Exception as e:
        logging.exception(f"An error occured while creating topic[{TOPIC_NAME}]: {e}")
else:
    logging.info(f"Topic[{TOPIC_NAME}] already exists.. Entering kafka...")




# producer client
def get_schema(file_name='user_events-v1.avsc'):
    schema_path = Path(__file__).parent / 'schemas' / file_name
    with open(schema_path, 'r') as f:
        schema = f.read()
        return schema
    
def delivery_report(err, msg):
    if err is not None:
        logging.error(f"Delivery failed for User record {msg.key()}: {err}")
        return
    logging.info(f'User record { msg.key()} successfully produced to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')


def main():
    schema_registry_client = SchemaRegistryClient(SCHEMA_REGISTRY_CONF)  
    schema_str = get_schema()
    record = generate_user_event()
    avro_serializer = AvroSerializer(
        schema_registry_client=schema_registry_client,
        schema_str=schema_str) 

    string_serializer = StringSerializer()
    
    producer = Producer(PRODUCER_CONF)

    logging.info(f"Producing the record to topic[{TOPIC_NAME}]. ^C to exit")

    try:
        producer.produce(
            topic=TOPIC_NAME,
            key=string_serializer(record.get('session_id')),
            value=avro_serializer(record, SerializationContext(TOPIC_NAME, MessageField.VALUE)),
            on_delivery=delivery_report)
    except Exception as e:
        logging.error(f"An error has occured: {e}")

    logging.info("\nFlushing records...")
    producer.flush()


if __name__ == '__main__':

    

    logging.basicConfig(level=logging.INFO)

    logging.info("Start..")

    main()
