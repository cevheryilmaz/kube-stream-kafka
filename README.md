# 🌀 KubeStream: Kafka on Kubernetes (Demo)

This repository is a **Kafka-based event-driven demo application** running on **Kubernetes**, using **KRaft mode**.

The setup demonstrates:
- **Producer (FastAPI)** → **Kafka Topic** → **Consumer (FastAPI)**
- **Prometheus metrics** exposed from the consumer
- Optional **CI/CD pipeline** for automatic container build & deploy

---

## 📁 Repository Structure
| Path | Description |
|------|-------------|
| `producer/` | FastAPI Producer microservice (includes /produce, /health, and auto-producer thread) |
| `consumer/` | FastAPI Consumer microservice (includes /metrics, /stats, max/min/avg metrics) |
| `k8s/` | Kubernetes manifests (Deployments & Services for producer and consumer) |
| `.github/workflows/ci-cd.yml` | CI/CD pipeline (build & push to GHCR + deploy to Kubernetes) |

---

## 🧪 Local Testing (Docker Compose)

You can test the system locally using Docker Compose.  
Kafka runs in **single-node mode**.

### 1️⃣ docker-compose.yml

```yaml
services:
  kafka:
    image: confluentinc/cp-kafka:7.8.3
    container_name: kafka
    ports:
      - "9092:9092"
      - "9093:9093"
    environment:
      KAFKA_KRAFT_MODE: 'true'
      CLUSTER_ID: '1L6g7nGhU-eAKfL--X25wo'
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LOG_DIRS: /tmp/kraft-combined-logs
    networks:
      - kafka-net

  producer:
    build:
      context: ./producer
    ports:
      - "8000:8000"
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
      KAFKA_TOPIC: sensor-data
    depends_on:
      - kafka
    networks:
      - kafka-net

  consumer:
    build:
      context: ./consumer
    ports:
      - "8001:8001"
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
      KAFKA_TOPIC: sensor-data
    depends_on:
      - kafka
    networks:
      - kafka-net

  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka-ui
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9092
    depends_on:
      - kafka
    networks:
      - kafka-net

networks:
  kafka-net:
    driver: bridge
```

### 2️⃣ Run the Stack
```bash
docker compose up -d
```
### 🧩 Producer Service

Base URL: [http://localhost:8000](http://localhost:8000)

| Endpoint                       | Description                                   |
| ------------------------------ | --------------------------------------------- |
| `GET /`                        | Returns basic service info                    |
| `POST /produce?sensor_id=<id>` | Sends a single random sensor message to Kafka |
| `GET /produce/random/{n}`      | Sends `n` random sensor messages              |
| `GET /health`                  | Health check (Kafka connection & topic info)  |

### 📡 Consumer Service

Base URL: [http://localhost:8001](http://localhost:8001)

| Endpoint       | Description                                                                                  |
| -------------- | -------------------------------------------------------------------------------------------- |
| `GET /`        | Returns basic service info                                                                   |
| `GET /stats`   | Displays real-time stats (message count, avg/max/min temperature, last message, last update) |
| `GET /metrics` | Prometheus metrics (scrape-ready)                                                            |

### 📊 Kafka UI (Optional)

If you enabled the kafka-ui service in Docker Compose, visit:

👉 [http://localhost:8080](http://localhost:8080)

You can browse:

- **Topics** — e.g. `sensor-data`
- **Messages** — live data streaming from the producer
- **Consumer Groups and Offsets** — real-time consumption tracking

### 3️⃣ Test Producer
```bash
curl -X POST http://localhost:8000/produce?sensor_id=1
curl http://localhost:8000/produce/random/5
```

### 4️⃣ Check Consumer Output
```bash
curl http://localhost:8001/stats
curl http://localhost:8000/health
```

### 5️⃣ Stop Everything
```bash
docker compose down

```
