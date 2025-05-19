import logging
from helpers import get_base_config, get_schema
from confluent_kafka.admin import AdminClient, NewTopic


def check_topics_exists(name):
    topics = client.list_topics()
    if name in topics.topics.keys():
        return True
    return False

def create_new_topic(name, client):
    topic_exists = check_topics_exists(name)
    if not topic_exists:
        topic = NewTopic(
            topic=name,
            num_partitions=12,
            replication_factor=3,
            config = {
                'unclean.leader.election.enable': False,
                "cleanup.policy": "delete",
                "retention.ms": 8640000,

                "segment.ms": 7200000,
                "segment.bytes": 536870912, 

                "min.insync.replicas": 2,
                "compression": "producer"

            }
        )

        future = client.create_topics([topic])
        for topic_name, topic_ in future.items():
            try:
                topic_.result()
                logging.info(f"Topic[{topic_name}]  successfully created..")
            except Exception as e:
                logging.info(f"An error occured while creating the topic: {e}")
    else:
        logging.info(f"Topic[{name}] already exists...")




def main(client):

    create_new_topic(name="user_events", client=client)


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    # setup client connection with the brokers
    client = AdminClient(get_base_config())

    main(client)

    print(get_schema())