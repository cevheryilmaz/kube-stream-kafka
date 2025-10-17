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
version: '3.8'

services:
  kafka:
    image: bitnami/kafka:3.7
    container_name: kafka
    ports:
      - "9092:9092"
    environment:
      - KAFKA_CFG_NODE_ID=1
      - KAFKA_CFG_PROCESS_ROLES=controller,broker
      - KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=1@kafka:9093
      - KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093
      - KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092
      - KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER
      - KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      - ALLOW_PLAINTEXT_LISTENER=yes

  producer:
    build: ./producer
    container_name: producer
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
    depends_on:
      - kafka
    ports:
      - "8000:8000"

  consumer:
    build: ./consumer
    container_name: consumer
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
    depends_on:
      - kafka
    ports:
      - "8001:8001"
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