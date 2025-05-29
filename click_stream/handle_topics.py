"""Module to handle Kafka topic creation and existence checks."""

import os
import logging

from dotenv import load_dotenv
from helpers import get_base_config
from confluent_kafka.admin import AdminClient, NewTopic

def check_topic_exists(client, topic_name=None):
    """
    Check if a Kafka topic exists.

    Args:
        client (AdminClient): Kafka AdminClient instance.
        topic_name (str, optional): The name of the topic to check.

    Returns:
        bool: True if the topic exists, False otherwise.
    """
    if topic_name is not None:
        topic_list = client.list_topics()
        if topic_name in topic_list.topics.keys():
            return True
    return False
            

def main(client, topic_name):
    """
    Create a Kafka topic if it does not already exist.

    Args:
        client (AdminClient): Kafka AdminClient instance.
        topic_name (str): The name of the topic to create.
    """
    exists = check_topic_exists(client=client, topic_name=topic_name)
    if not exists:
        # Define the new topic configuration
        topic = NewTopic(
            topic=topic_name,
            num_partitions=12,
            replication_factor=3,
            config = {
                "cleanup.policy": "delete",
                "retention.ms": 86400000,

                "segment.ms": 3600000,
                "segment.bytes": 536870912, #537 MB

                "min.insync.replicas": 2,
                "unclean.leader.election.enable": False,

                "compression.type": "producer"
            }
        )

        # Attempt to create the topic using the AdminClient
        futures = client.create_topics([topic])

        for topic_name, future in futures.items():
            try:
                future.result()
                logging.info(f"Topic[{topic_name}] successfully created..")
            except Exception as e:
                logging.error(f"An error occured while creating the topic: [{topic_name}]:  {e}")
    else:
        logging.info(f"Topic: [{topic_name}] already exists")

if __name__ == "__main__":
    # Load environment variables and initialize Kafka AdminClient
    load_dotenv()

    TOPIC_NAME = os.environ.get("TOPIC_NAME")

    logging.basicConfig(level="INFO")

    CLIENT = AdminClient(get_base_config())

    main(client= CLIENT, topic_name = TOPIC_NAME)
