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
| `producer/` | FastAPI Producer microservice |
| `consumer/` | FastAPI Consumer microservice (includes `/metrics` and `/stats` endpoints) |
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

### 3️⃣ Test Producer
```bash
curl http://localhost:8000/produce
```

### 4️⃣ Check Consumer Output
```bash
curl http://localhost:8001/stats
```

### 5️⃣ Stop Everything
```bash
docker compose down
```