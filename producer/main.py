import logging
import time
import json
import multiprocessing
from pathlib import Path
from pprint import pprint
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.admin import AdminClient, ConfigResource, ConfigEntry, NewTopic
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField

# Import functions from factory and config modules
from factory import generate_user_event
from config import get_topic_list,get_schema,ADMIN_CONFIG, TOPIC_NAME, SCHEMA_REGISTRY_CONF, PRODUCER_CONF


# Initialize the AdminClient to manage kafka topics and configurations.
client = AdminClient(ADMIN_CONFIG)

# Define the schema path for the Avro schema file.
schema_path = Path(__file__).parent / 'schemas' / 'user_events-v1.avsc'

NUM_PROCESS = 10

def pre_health_checks():
    """
        This function checks if the Kafka topic specified by TOPIC_NAME exists.
        If the topic doesn't exist, it attempts to create it.
    """
    if TOPIC_NAME not in get_topic_list(client):
        logging.warning("Topic not found. Entering creation logic......")
        topic = NewTopic(
            topic=TOPIC_NAME,
            num_partitions=20, 
            replication_factor=3)
        try:
            client.create_topics([topic])
            logging.info(f"topic[{TOPIC_NAME}] successfully created..")
        except Exception as e:
            logging.exception(f"An error occured while creating topic[{TOPIC_NAME}]: {e}")
    else:
        logging.info(f"Topic[{TOPIC_NAME}] already exists.. Entering kafka...")


# producer client

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
    """
        Main function to produce a user event message to the Kafka topic.
        It initializes the producer, serializes the message using Avro, and sends it to Kafka.
    """

     # create a client to interact with confluents schema registry
    schema_registry_client = SchemaRegistryClient(SCHEMA_REGISTRY_CONF)  

    # Retrieve the Avro schema definition from a file
    schema_str = get_schema(schema_path=schema_path)

    # Initialize the Avro serializer with the schema and schema registry client
    avro_serializer = AvroSerializer(
        schema_registry_client=schema_registry_client,
        schema_str=schema_str) 

    # Simple serializer to convert the session_id key to a byte format
    string_serializer = StringSerializer()

    producer = Producer(PRODUCER_CONF)
    
    # Initialize the Kafka producer with the provided configuration
    try:
        logging.info(f"Producing the record to topic[{TOPIC_NAME}]. ^C to exit")
        # Generate a sample user event to be sent to Kafka
        
        while True:
            record = generate_user_event()

            producer.produce(
                topic=TOPIC_NAME,
                key=string_serializer(record.get('session_id')), #serialize the key
                value=avro_serializer(record, SerializationContext(TOPIC_NAME, MessageField.VALUE)),   #serialize the value
                on_delivery=delivery_report)
            
            producer.poll(0)

    except Exception as e:
        logging.error(f"An error has occured inside producer client: {e}")

    finally:
        producer.flush()

    
if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)

    logging.info("Start..")

    pre_health_checks()

    processes = []

    for each_process in range(NUM_PROCESS):
        p = multiprocessing.Process(target=main)
        processes.append(p)
        p.start()

    for p in processes:
        p.join()


