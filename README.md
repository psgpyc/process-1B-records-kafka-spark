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
<pre>
```text
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
```
</pre>
---

## 📦 Project Structure

<pre>
```
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
```
</pre>


## Status

| Component                | Status     |
|--------------------------|------------|
| Kafka (KRaft)            | Running |
| Schema Registry          | Running |
| Avro Producer            | In Progress |
| Spark Consumer           | Next |
| Delta Lake Integration   | Next |
| BI Dashboard             | Planned |
| Monitoring Stack         | Planned |
| FastAPI Admin Panel      | Future |

---

## 📜 License

MIT © [Paritosh Ghimire](https://github.com/psgpyc)
