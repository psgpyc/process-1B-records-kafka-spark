ADMIN_CONFIG = {
     "bootstrap.servers": "localhost:19092"
}

SCHEMA_REGISTRY_CONF = {
    "url": "http://localhost:8081"
}

PRODUCER_CONF = {
    'bootstrap.servers': 'localhost:19092, localhost:29092, localhost:39092',
    'batch.size': 512 * 1024, # 4200 messages each of size 110 bytes - for 10ms optimsied
    'linger.ms': 10,
    'queue.buffering.max.messages': 100_000,
    'queue.buffering.max.kbytes': 30 * 1024,
    
    'acks': 'all',      # kafka waits for acks from all in-sync replicas(ISRs) // 0,1,all(-1)
    'enable.idempotence': True, #ensures exactly once delivery when acks=all+retries // no duplicate message are writeen even when retries are enabled.
    'retry.backoff.ms': 500,  # Retry delay in milliseconds
    'delivery.timeout.ms': 30000,  # Max time to wait for message delivery
    'compression.type': 'snappy'   # gzip, snappy, lz4, zstd
}

TOPIC_NAME = "psgpyc-e"

SCHEMA_PATH = "schemas/user_events-v1.avsc"

def get_topic_list(client):
        return client.list_topics().topics.keys()

def get_schema(schema_path):
    with open(schema_path, 'r') as f:
        schema = f.read()
        return schema
    

