import json
from pathlib import Path

from faker import Faker
from pprint import pprint
import time
import random

fake = Faker()


def generate_user_event():
    return {
        "timestamp": int(time.time() * 1000),
        "user_id": random.randint(1000, 9999),
        "session_id": fake.uuid4(),
        "event_type": random.choice(["click", "view", "purchase", "scroll"]),
        "page": fake.uri_path(),
        "referrer": fake.uri(),
        "user_agent": fake.user_agent(),
        "user_process":"bypass-process",
        "route": "bypass"
    }


def get_base_config():
    pwd = Path(__file__).parent
    config_file = pwd / 'base.properties'
    config = {}
    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if len(line):
                line_split = line.split("=")
                config[line_split[0].strip()] = line_split[1].strip()
    return config

def get_schema_str(file_name="user_event-v1.avsc"):
    pwd = Path(__file__).parent
    schema_file_path = pwd / 'schema' / file_name
    with open(schema_file_path, 'r') as f:
        schemafile = f.read()
        return schemafile

    