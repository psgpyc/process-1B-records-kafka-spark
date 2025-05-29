import logging

import os
from dotenv import load_dotenv
from helpers import get_base_config
from confluent_kafka.admin import AdminClient, NewTopic

def check_topic_exists(client, topic_name=None):
    if topic_name is not None:
        topic_list = client.list_topics()
        if topic_name in topic_list.topics.keys():
            return True
    return False
            

def main(client, topic_name):
    exists = check_topic_exists(client=client, topic_name=topic_name)
    if not exists:
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

    load_dotenv()

    TOPIC_NAME = os.environ.get("TOPIC_NAME")

    logging.basicConfig(level="INFO")

    CLIENT = AdminClient(get_base_config())

    main(client= CLIENT, topic_name = TOPIC_NAME)
