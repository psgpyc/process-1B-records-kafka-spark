from pprint import pprint
import logging
from helpers import get_base_config
from confluent_kafka.admin import AdminClient, NewTopic

BASE_CONFIG = get_base_config()

def main():

    client = AdminClient(BASE_CONFIG)

    topic = NewTopic(
        topic="base-topic",
        num_partitions = 12,
        replication_factor=3,
        config= {
            'cleanup.policy':'delete',
            'retention.ms': 86400000,

            'segment.ms': 7200000, # 2 hours
            'segment.bytes': 536870912, # 512 MB

            'max.message.bytes':  20 * 1024, # 20 kilobytes

            'min.insync.replicas': 2,
            'unclean.leader.election.enable': False,

            'compression.type': 'producer'
        }
    )

    future = client.create_topics([topic])

    for k,v in future.items():
        try:
            v.result()
            logging.info(f"Topic {k} successfully created")

        except Exception as e:
            logging.error(f"An error occured: {e}")

if __name__ == "__main__":
    logging.basicConfig(level='INFO')

    main()