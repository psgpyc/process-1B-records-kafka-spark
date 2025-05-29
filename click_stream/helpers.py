import os
import time
import random
from faker import Faker
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

fake = Faker()

def get_base_config():
    """
        Returns base configs to connect with confluent cloud brokers
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
    return {
        "url": os.environ.get("SCHEMA_REGISTRY_URL"),
        "basic.auth.user.info": os.environ.get("SCHEMA_REGISTRY_BASIC_AUTH")
    }



def get_schema(schema_name=None):
    """
            {
                "event_id": "evt_92348",
                "user_id": "user_124",
                "session_id": "sess_89323",
                "url": "/product/123",
                "event_type": "click",
                "device": "mobile",
                "referrer": "facebook.com",
                "timestamp": "2025-05-29T08:10:23Z"
            }   
    """
    if schema_name is not None:
        pwd = Path(__file__).parent
        schema_path = pwd / "schema" / schema_name
        if schema_path.exists():
            with open(schema_path, 'r') as sf:
                schema = sf.read()
                return schema
        else:
            return None


def get_record():
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
