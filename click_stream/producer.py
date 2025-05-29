import os
import logging
import time
import json
from multiprocessing import Process
from dotenv import load_dotenv

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField, StringSerializer

from helpers import get_base_config, get_schema, get_schema_registry_conf, get_record


def delivery_report(err, msg):
    """
        This callback function is called once a message is delivered to Kafka.
        It logs the success or failure of the message delivery.
    """
    if err is not None:
        logging.error(f"Delivery failed for User record {msg.key()}: {err}")
        return
    logging.info(f'User record { msg.key()} successfully produced to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')


def send_to_dlq(record, topic, producer):
    try:
        value = json.dumps(record).encode('utf-8')
        producer.produce(
            topic=topic,
            key=str(record.get("session_id")),
            value=value
        )
        producer.flush()
        
        logging.info(f"Sent record to DLQ topic..")
    except Exception as e:
        logging.error(f"Failed to send record to DLQ: {e}")



def main():
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

    # setting string serializer for key
    string_serializer = StringSerializer()

    # setting up schema registry client
    schema_registry_client = SchemaRegistryClient(get_schema_registry_conf())

    schema = get_schema(schema_name="click_stream-v1.avsc")
    if schema is None:
        raise FileNotFoundError(f"Schema does not exist...")
    
         #  setting up avro serializer
    avro_serializer = AvroSerializer(schema_registry_client=schema_registry_client, schema_str=schema)

    # setup producer
    producer = Producer(PRODUCER_CONFIG)

    while True:       
        record = get_record()

        if record is None:
            logging.error("get_record() returned None. Skipping...")
            raise ValueError("Expected a record, but got None from get_record()")
        
        try:
            serialized_value = avro_serializer(record, SerializationContext(topic, MessageField.VALUE))
        except Exception as e:
            logging.error(f"An error occuered while trying to serialize the record: {e}")  
            logging.info("Sending to DLQ topic")
            send_to_dlq(record=record, topic=os.environ.get("TOPIC_NAME_DLQ"), producer=producer)
            continue

        try:
            producer.produce(
                        topic=topic, 
                        key=string_serializer(record["session_id"]),
                        value=serialized_value,
                        on_delivery=delivery_report
                    )    
            producer.poll(0)   

        except BufferError:
            logging.warning("buffer full. flushing.....")
            producer.flush()
            producer.produce(
                topic=topic, 
                key=string_serializer(record["session_id"]),
                value=serialized_value,
                on_delivery=delivery_report)
            
        except Exception as e:
            logging.error(f"An error occured while producing the record..: {e}")
            send_to_dlq(record=record, topic=os.environ.get("TOPIC_NAME_DLQ"), producer=producer)
        
            


if __name__ == "__main__":
       
    logging.basicConfig(level="INFO")
    load_dotenv()
    PROCESS_COUNT = os.environ.get("NUM_PRODUCER_PROCESS")
    
    processes =  []

    for each_process in range(int(PROCESS_COUNT)):
        p = Process(target=main)
        processes.append(p)
        p.start()

    for each in processes:
        each.join()

        
        
   