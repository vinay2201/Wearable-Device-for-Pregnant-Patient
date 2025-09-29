from urllib.parse import urlparse
from paho.mqtt.client import Client
from .config import SETTINGS

def make_client(client_id: str):
    url = urlparse(SETTINGS.mqtt_url)
    c = Client(client_id=client_id, protocol=5)
    if SETTINGS.mqtt_username:
        c.username_pw_set(SETTINGS.mqtt_username, SETTINGS.mqtt_password or None)
    host = url.hostname or "localhost"
    port = url.port or 1883
    c.connect(host, port, keepalive=60)
    return c
