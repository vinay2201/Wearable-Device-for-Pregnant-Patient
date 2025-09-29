import os, time, json, random
from datetime import datetime, timezone
from dotenv import load_dotenv
from urllib.parse import urlparse
from paho.mqtt.client import Client

load_dotenv()
URL = os.getenv("MQTT_URL","mqtt://localhost:1883")
DEVICE_ID = os.getenv("DEVICE_ID","device-001")
INTERVAL = float(os.getenv("PUBLISH_INTERVAL","2"))

u = urlparse(URL)
client = Client(client_id=f"edge-sim-{DEVICE_ID}", protocol=5)
client.connect(u.hostname or "localhost", u.port or 1883)
client.loop_start()

def payload():
    # simplistic vital simulation with occasional spikes
    hr = random.gauss(85, 3)
    spo2 = max(88, min(100, random.gauss(98, 0.6)))
    temp = random.gauss(36.8, 0.15)
    env_temp = random.gauss(22.0, 0.8)
    motion = abs(random.gauss(0.12, 0.05))
    # occasional anomaly burst
    if random.random() < 0.05:
        hr += random.choice([20, -15])
        spo2 -= random.choice([5, 8])
    return dict(ts=datetime.now(timezone.utc).isoformat(), hr=round(hr,2), spo2=round(spo2,2),
                temp=round(temp,2), env_temp=round(env_temp,2), motion=round(motion,3))

try:
    while True:
        p = payload()
        topic = f"wearable/{DEVICE_ID}/telemetry"
        client.publish(topic, json.dumps(p), qos=1)
        print("→", topic, p)
        time.sleep(INTERVAL)
except KeyboardInterrupt:
    pass
finally:
    client.loop_stop()
