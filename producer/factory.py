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
        "user_agent": fake.user_agent()
    }



