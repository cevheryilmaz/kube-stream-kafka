# producer/app.py
from fastapi import FastAPI
from kafka import KafkaProducer, errors
import json
import random
import time
import os

app = FastAPI(title="kube-stream-producer")

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "sensor-data")

# Producer
for _ in range(10):  # 10 times
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BOOTSTRAP],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            linger_ms=10
        )
        print(f"Connected to Kafka at {KAFKA_BOOTSTRAP}")
        break
    except errors.NoBrokersAvailable:
        print("Kafka not ready, retrying in 5s...")
        time.sleep(5)
else:
    raise RuntimeError(f"Could not connect to Kafka at {KAFKA_BOOTSTRAP}")


@app.get("/")
def root():
    return {"service": "producer", "topic": TOPIC}

@app.post("/produce")
def produce_one(sensor_id: int = 1):
    """Tek bir veri üretir ve topic'e gönderir."""
    payload = {
        "sensor_id": sensor_id,
        "temperature": round(random.uniform(20.0, 35.0), 2),
        "timestamp": time.time()
    }
    producer.send(TOPIC, value=payload)
    producer.flush()
    return {"status": "sent", "data": payload}

@app.get("/produce/random/{n}")
def produce_many(n: int):
    """n adet rastgele mesaj üretir (örnek test endpoint'i)."""
    sent = []
    for i in range(n):
        payload = {
            "sensor_id": random.randint(1, 5),
            "temperature": round(random.uniform(20.0, 35.0), 2),
            "timestamp": time.time()
        }
        producer.send(TOPIC, value=payload)
        sent.append(payload)
    producer.flush()
    return {"status": "sent", "count": len(sent), "data": sent}
