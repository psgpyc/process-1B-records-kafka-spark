# 🚀 process-1B-records-kafka-spark

### Ultra High-Throughput Streaming Pipeline Using Kafka + Schema Registry + Spark + Delta Lake

This project demonstrates how to build a production-grade streaming data pipeline capable of processing **1 billion records per hour (~277,777 records per second)** using cutting-edge open-source tools and cloud infrastructure.

---

## ⚙️ Stack Summary

| Layer              | Tool/Service                          |
|--------------------|----------------------------------------|
| Ingestion Engine   | Apache Kafka (KRaft mode, no Zookeeper) |
| Serialization      | Apache Avro + Confluent Schema Registry |
| Stream Processor   | Apache Spark Structured Streaming (Databricks) |
| Storage Layer      | Delta Lake on AWS S3 / cloud object store |
| Orchestration      | Apache Airflow (planned)                |
| Monitoring         | Prometheus + Grafana (planned)          |
| Dev Environment    | Docker Compose + Python + GitHub        |

---

## 💡 Project Goals

- Simulate **high-velocity data streams** in Avro format.
- Validate messages against **Avro schemas** with Schema Registry.
- **Ingest into Kafka** at hundreds of thousands of messages per second.
- Consume using **Spark Structured Streaming** on Databricks.
- Write results to **Delta Lake** with ACID guarantees.
- Enable **real-time analytics** on massive datasets.
- Showcase **production-like architecture**, **performance tuning**, and **scalability**.

---

## 🧱 Architecture Overview

\`\`\`
+--------------------+        +--------------------+         +--------------------+
| High-throughput    | -----> |   Kafka Topic      | ----->  |  Spark on Databricks|
| Python Producer    |  Avro  | (100+ partitions)  |         |  (Structured Stream)|
+--------------------+        +--------------------+         +---------+----------+
                                                               |
                                                               v
                                                  +------------------------+
                                                  |   Delta Lake on S3     |
                                                  +------------------------+
                                                               |
                                                               v
                                                  +------------------------+
                                                  |  Power BI / Tableau    |
                                                  +------------------------+
\`\`\`

---

## 📦 Project Structure

\`\`\`
process-1B-records-kafka-spark/
│
├── docker-compose.yml         # KRaft Kafka + Schema Registry
├── .gitignore
│
├── producer/                  # Avro-based producer (Python)
│   ├── producer.py
│   └── schemas/
│       └── user_event.avsc
│
├── databricks_jobs/           # Spark Structured Streaming scripts / notebooks
│
├── dashboards/                # BI dashboard files (Power BI / Tableau)
│
└── README.md
\`\`\`

---

## 🚀 Getting Started

### 1. 🐳 Run Kafka and Schema Registry

\`\`\`bash
docker-compose up -d
\`\`\`

Kafka will be available at \`localhost:9092\`, and Schema Registry at \`localhost:8081\`.

---

### 2. 🧪 Produce Data to Kafka

\`\`\`bash
cd producer
python producer.py
\`\`\`

This script generates hundreds of thousands of Avro-encoded events per second and sends them to a Kafka topic (\`avro-topic\`), with schema auto-registered in Schema Registry.

---

### 3. 🔥 Process with Spark (on Databricks)

- Import the job from \`databricks_jobs/\` into your Databricks workspace.
- Set up Kafka connection (public broker endpoint or port-forwarding).
- Start streaming the Kafka topic and write output to Delta Lake.

---

### 4. 📊 Analyze

- Connect your dashboard tool (e.g., Power BI, Tableau) to Delta tables.
- Build real-time KPIs like:
  - Processed events per second
  - Volume per region/category/device
  - Streaming lag / errors

---

## 🔍 Status

| Component                | Status     |
|--------------------------|------------|
| Kafka (KRaft)            | ✅ Running |
| Schema Registry          | ✅ Running |
| Avro Producer            | 🔄 In Progress |
| Spark Consumer           | 🔜 Next |
| Delta Lake Integration   | 🔜 Next |
| BI Dashboard             | 🔜 Planned |
| Monitoring Stack         | 🔜 Planned |
| FastAPI Admin Panel      | ❌ Future |

---

## 📜 License

MIT © [Paritosh Ghimire](https://github.com/psgpyc)
