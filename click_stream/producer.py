"""
Kafka Avro Producer with Multiprocessing and DLQ Support

This module sets up a Kafka producer that generates and sends Avro-encoded clickstream records
to a Kafka topic. It supports multiple parallel producer processes, Avro serialization using
Confluent Schema Registry, and Dead Letter Queue (DLQ) handling for serialization and production errors.

Modules:
- confluent_kafka: Kafka client and schema registry support
- dotenv: Loads environment variables
- multiprocessing: For parallel producer processes
- signal: Handles graceful shutdown
- logging: For event and error logging

Functions:
- delivery_report(): Kafka delivery callback
- send_to_dlq(): Sends failed records to DLQ topic
- main(): Core logic for producing serialized messages to Kafka
- exit_gracefully(): Graceful shutdown routine
"""

import os
import sys
import time
import logging
import signal
from dotenv import load_dotenv
from multiprocessing import Process, Value, Lock


from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField, StringSerializer

from helpers import get_base_config, get_schema, get_schema_registry_conf, get_record, send_to_dlq


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
    Main producer function that runs in a loop:
    - Fetches a new record from the record generator
    - Serializes it using Avro with Schema Registry
    - Sends it to the configured Kafka topic
    - On failure (serialization or production), sends to DLQ

    Utilizes multiprocessing-safe counter and lock to coordinate metrics.
    """
    topic = os.environ.get("TOPIC_NAME")

    PRODUCER_CONFIG = {

          **get_base_config(),

          "linger.ms": 10,
          "batch.size": 15 * 1024, #15 KB
          "batch.num.messages": 100,

          "queue.buffering.max.kbytes": 100 * 1024, #100 kb
          "queue.buffering.max.messages": 850000,

          "retries": 3,
          "enable.idempotence": True,
          "max.in.flight.requests.per.connection": 5,
          "retry.backoff.ms": 500,


          "compression.type": "snappy"
     }

    # setting string serializer for key (session_id)
    string_serializer = StringSerializer()

    # setting up schema registry client
    schema_registry_client = SchemaRegistryClient(get_schema_registry_conf())

    # loading Avro schema for serialization
    schema = get_schema(schema_name="click_stream-v1.avsc")
    if schema is None:
        raise FileNotFoundError(f"Schema does not exist...")
    
    # setting up Avro serializer with schema registry client and schema string
    avro_serializer = AvroSerializer(schema_registry_client=schema_registry_client, schema_str=schema)

    # setup Kafka producer with config
    producer = Producer(PRODUCER_CONFIG)

    while True:       
        record = get_record()

        if record is None:
            logging.error("get_record() returned None. Skipping...")
            raise ValueError("Expected a record, but got None from get_record()")
        
        try:
            # serialize record using Avro serializer
            serialized_value = avro_serializer(record, SerializationContext(topic, MessageField.VALUE))
        except Exception as e:
            # handle serialization errors by logging and sending to DLQ
            logging.error(f"An error occuered while trying to serialize the record: {e}")  
            logging.info("Sending to DLQ topic")
            send_to_dlq(record=record, topic=os.environ.get("TOPIC_NAME_DLQ"), producer=producer)
            continue

        try:
            # produce serialized record to Kafka topic with string-serialized key
            producer.produce(
                        topic=topic, 
                        key=string_serializer(record["session_id"]),
                        value=serialized_value,
                        on_delivery=delivery_report
                    )    
            # poll to trigger delivery report callbacks (non-blocking)
            producer.poll(0) 

            # increment counter safely with lock for multiprocessing
            with lock:
                counter.value += 1  

        except BufferError:
            # buffer full, flush and retry producing
            logging.warning("buffer full. flushing.....")
            producer.flush()
            producer.produce(
                topic=topic, 
                key=string_serializer(record["session_id"]),
                value=serialized_value,
                on_delivery=delivery_report)
            
        except Exception as e:
            # handle any other production errors by logging and sending to DLQ
            logging.error(f"An error occured while producing the record..: {e}")

            send_to_dlq(record=record, topic=os.environ.get("TOPIC_NAME_DLQ"), producer=producer)
        

def exit_gracefully(counter, start_time):
    """
    Handles SIGINT for graceful shutdown.

    Prints total runtime and total records produced before exiting.

    Parameters:
    - counter (multiprocessing.Value): Shared counter for tracking events
    - start_time (float): Start timestamp of the process
    """
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total run time: {total_time:.2f} seconds")
    print(f"Total events generated: {counter.value}")
    sys.exit(0)          


if __name__ == "__main__":
       
    logging.basicConfig(level="INFO")
    load_dotenv()

    # setup for multi process synchronization lock
    lock = Lock()

    # setup: shared counter to monitor production of records across processes
    counter = Value('i', 0)
    start_time = time.time() 

    # handling shutdown (Ctrl + C) gracefully by registering signal handler
    def signal_handler(sig, frame):
        exit_gracefully(counter, start_time)

    signal.signal(signal.SIGINT, signal_handler) 

    processes =  []

    # spawn multiple producer processes as specified by environment variable
    for each_process in range(int(os.environ.get("NUM_PRODUCER_PROCESS"))):
        p = Process(target=main)
        processes.append(p)
        p.start()

    # wait for all processes to complete
    for each in processes:
        each.join()