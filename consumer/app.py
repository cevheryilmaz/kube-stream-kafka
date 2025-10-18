# consumer/app.py
from fastapi import FastAPI
from fastapi import Response
from kafka import KafkaConsumer
import json
import os
import threading
import time
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="kube-stream-consumer")

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "sensor-data")
GROUP_ID = os.getenv("KAFKA_GROUP", "kube-stream-consumers")

# Prometheus metrics
MSG_COUNT = Counter("sensor_messages_consumed_total", "Total sensor messages consumed")
AVG_TEMP = Gauge("sensor_avg_temperature", "Average temperature across consumed messages")
MAX_TEMP = Gauge("sensor_max_temperature", "Maximum temperature seen so far")
MIN_TEMP = Gauge("sensor_min_temperature", "Minimum temperature seen so far")

stats = {
    "count": 0,
    "avg_temp": 0.0,
    "max_temp": None,
    "min_temp": None,
    "last_message": None,
    "last_update": None
}

def start_consumer():
    import traceback
    while True:
        try:
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=[KAFKA_BOOTSTRAP],
                group_id=GROUP_ID,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",
                enable_auto_commit=True
            )
            print("✅ Kafka consumer started")
            for msg in consumer:
                val = msg.value
                temp = float(val.get("temperature", 0.0))
                stats["count"] += 1
                prev_avg = stats["avg_temp"]
                stats["avg_temp"] = ((prev_avg * (stats["count"] - 1)) + temp) / stats["count"]
                stats["max_temp"] = temp if stats["max_temp"] is None else max(stats["max_temp"], temp)
                stats["min_temp"] = temp if stats["min_temp"] is None else min(stats["min_temp"], temp)
                stats["last_message"] = val
                stats["last_update"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                MSG_COUNT.inc()
                AVG_TEMP.set(stats["avg_temp"])
                MAX_TEMP.set(stats["max_temp"])
                MIN_TEMP.set(stats["min_temp"])
        except Exception as e:
            print("⚠️ Kafka consumer error:", e)
            traceback.print_exc()
            time.sleep(5)  # retry after 5s

# Start background thread on import
thread = threading.Thread(target=start_consumer, daemon=True)
thread.start()

@app.get("/")
def root():
    return {"service": "consumer", "topic": TOPIC}

@app.get("/stats")
def get_stats():
    return {
        "count": stats["count"],
        "avg_temp": stats["avg_temp"],
        "max_temp": stats["max_temp"],
        "min_temp": stats["min_temp"],
        "last_message": stats["last_message"],
        "last_update": stats["last_update"]
    }

@app.get("/metrics")
def metrics():
    # Expose prometheus metrics endpoint
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)