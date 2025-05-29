"""
Helper functions for Kafka configuration, schema loading, and generating fake clickstream events.
"""

import os
import json
import time
import random
from faker import Faker
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

fake = Faker()

def get_base_config():
    """
        Returns the Kafka producer configuration by reading necessary credentials and settings
        from environment variables.
    """
    return {
        "bootstrap.servers": os.environ.get("BOOTSTRAP_SERVERS"),
        "security.protocol": os.environ.get("SECURITY_PROTOCOL"),
        "sasl.mechanisms": os.environ.get("SASL_MECHANISMS"),
        "sasl.username": os.environ.get("SASL_USERNAME"),
        "sasl.password": os.environ.get("SASL_PASSWORD"),
        "client.id": os.environ.get("CLIENT_ID")
    }



def get_schema_registry_conf():
    """
        Returns the schema registry configuration by reading the URL and authentication info
        from environment variables.
    """
    return {
        "url": os.environ.get("SCHEMA_REGISTRY_URL"),
        "basic.auth.user.info": os.environ.get("SCHEMA_REGISTRY_BASIC_AUTH")
    }

def get_schema(schema_name=None):
    """
        Loads and returns the Avro schema content from a file.

        Args:
            schema_name (str): The filename of the schema to load (expected to be in the 'schema' directory).

        Returns:
            str or None: The schema content as a string if the file exists, otherwise None.

        The schema file is resolved relative to the current file's directory inside a 'schema' folder.
    """
    if schema_name is not None:
        # Resolve the path to the schema file located in the 'schema' directory relative to this file
        pwd = Path(__file__).parent
        schema_path = pwd / "schema" / schema_name
        if schema_path.exists():
            with open(schema_path, 'r') as sf:
                schema = sf.read()
                return schema
        else:
            return None

def get_record():
    """
        Generates a fake clickstream event record with randomized data fields.

        Returns:
            dict: A dictionary representing a clickstream event.
    """
    return {
        "event_id":  f"event_{random.randint(1, 99999)}",
        "user_id": f"user_{random.randint(1000, 9999)}",
        "session_id": f"{fake.uuid4()}",
        "url": fake.uri_path(),
        "event_type": random.choice(["click", "view", "purchase", "scroll"]),
        "device": random.choice(["mobile", "Desktop", "tablets"]),
        "referrer": fake.uri(),
        "timestamp": int(time.time() * 1000),
    }


def send_to_dlq(record, topic, producer=None):
    """
    Sends the given record to the specified Dead Letter Queue (DLQ) Kafka topic.

    Parameters:
    - record (dict): The record dictionary to send to DLQ.
    - topic (str): The Kafka topic name for the DLQ.
    - producer (confluent_kafka.Producer): Kafka producer instance used for sending.

    This function JSON-serializes the record and sends it to the DLQ topic.
    """
    try:
        value = json.dumps(record).encode('utf-8')
        producer.produce(
            topic=topic,
            value=value
        )
        producer.flush()
        logging.info(f"Sent record to DLQ topic..")
    except Exception as e:
        logging.error(f"Failed to send record to DLQ: {e}")
