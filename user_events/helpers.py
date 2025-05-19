import os
import time
import random
from faker import Faker
from pathlib import Path
from dotenv import load_dotenv

fake = Faker()
load_dotenv()

def get_base_config():
    """
        This functions returns required bas condifuration to connect to confluent cloud.

        returns: DICT
    """
    return {
        "bootstrap.servers": os.environ.get("BOOTSTRAP_SERVERS"),
        "security.protocol": os.environ.get("SECURITY_PROTOCOL"),
        "sasl.mechanisms": os.environ.get("SASL_MECHANISMS"),
        "sasl.username": os.environ.get("SASL_USERNAME"),
        "sasl.password": os.environ.get("SASL_PASSWORD"),
        "client.id": os.environ.get("CLIENT_ID")
    }


def get_schema(file_name="user_event-v1.avsc"):
    pwd = Path(__file__)
    file_path = pwd.parent / 'schemas' / file_name
    if file_path.exists():
        with open(file_path, 'r') as f:
            schema_str = f.read()
            return schema_str
    else:
        raise FileNotFoundError
    
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