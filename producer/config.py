ADMIN_CONFIG = {
     "bootstrap.servers": "localhost:19092"
}

SCHEMA_REGISTRY_CONF = {
    "url": "http://localhost:8081"
}

PRODUCER_CONF = {
    'bootstrap.servers': 'localhost:19092',
    'acks': 'all',      # kafka waits for acks from all in-sync replicas(ISRs) // 0,1,all(-1)
    'enable.idempotence': True, #ensures exactly once delivery when acks=all+retries // no duplicate message are writeen even when retries are enabled.
    'retries': 5,
    'linger.ms': 3,
    'batch.size': 32 * 1024, #32KB
    'compression.type': 'snappy'   # gzip, snappy, lz4, zstd
}

TOPIC_NAME = "user-events"

SCHEMA_PATH = "schemas/user_events-v1.avsc"