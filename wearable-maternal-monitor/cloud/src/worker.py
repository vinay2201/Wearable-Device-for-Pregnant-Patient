from __future__ import annotations
import json, time, threading
from datetime import datetime, timezone
import pandas as pd
from sqlalchemy import text
from .config import SETTINGS
from .db import engine
from .mqtt_utils import make_client
from .analytics import zscore_flags, cluster_distance, FEATURES

TOPIC_IN = "wearable/+/telemetry"

def insert_telemetry(user_id: str, ts: datetime, payload: dict):
    cols = ["hr","spo2","temp","env_temp","motion"]
    values = [payload.get(c) for c in cols]
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO telemetry (user_id, ts, hr, spo2, temp, env_temp, motion)
            VALUES (:user_id, :ts, :hr, :spo2, :temp, :env_temp, :motion)
        """), dict(user_id=user_id, ts=ts, hr=values[0], spo2=values[1], temp=values[2], env_temp=values[3], motion=values[4]))

def load_user_window(user_id: str, minutes: int = 60):
    with engine.begin() as conn:
        df = pd.read_sql(text("""
            SELECT ts, hr, spo2, temp, env_temp, motion FROM telemetry
            WHERE user_id=:uid AND ts >= (NOW() - INTERVAL :mins MINUTE)
            ORDER BY ts ASC
        """), conn, params={"uid": user_id, "mins": minutes})
    df["ts"] = pd.to_datetime(df["ts"])
    df.set_index("ts", inplace=True)
    return df

def publish_alert(mqtt, user_id: str, kind: str, detail: dict):
    ts = datetime.now(timezone.utc).isoformat()
    payload = {"userId": user_id, "type": kind, "ts": ts, "detail": detail}
    mqtt.publish(f"wearable/{user_id}/alerts", json.dumps(payload), qos=1)
    mqtt.publish("wearable/broadcast/alerts", json.dumps(payload), qos=0)
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO alerts (user_id, ts, type, detail)
            VALUES (:uid, NOW(), :type, CAST(:detail AS JSON))
        """), {"uid": user_id, "type": kind, "detail": json.dumps(detail)})

def handle_message(mqtt, topic: str, payload: bytes):
    try:
        parts = topic.split('/')
        user_id = parts[1]
        data = json.loads(payload.decode('utf-8'))
        ts = datetime.fromisoformat(data.get("ts")) if data.get("ts") else datetime.utcnow()
        insert_telemetry(user_id, ts, data)
        # window for personalization
        df = load_user_window(user_id, minutes=max(SETTINGS.window_minutes, 60))
        if len(df) < 30:  # warm-up
            return
        flags = zscore_flags(df, SETTINGS.z_threshold)
        nflag = int(flags.iloc[-1])
        n, m = SETTINGS.n_of_m
        z_anom = nflag >= n
        dist = cluster_distance(df).iloc[-1]
        cluster_anom = dist >= 2.0  # ~2 sigma distance from usual cluster
        # Combined decision w/ cooldown
        decision = (1 if z_anom else 0) + (1 if cluster_anom else 0) >= 1
        if decision:
            publish_alert(mqtt, user_id, "combined", {
                "z_flags": nflag, "cluster_dist": float(dist), "threshold": SETTINGS.z_threshold,
                "features": FEATURES
            })
    except Exception as e:
        print("[worker] error:", e)

def main():
    from urllib.parse import urlparse
    mqtt = make_client("cloud-worker")
    mqtt.loop_start()

    def on_message(client, userdata, msg):
        handle_message(client, msg.topic, msg.payload)

    mqtt.on_message = on_message
    mqtt.subscribe(TOPIC_IN, qos=1)

    print("[worker] running. Subscribed to", TOPIC_IN)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        mqtt.loop_stop()

if __name__ == "__main__":
    main()
