from dataclasses import dataclass
import os
from dotenv import load_dotenv
load_dotenv()

@dataclass
class Settings:
    mqtt_url: str = os.getenv("MQTT_URL", "mqtt://localhost:1883")
    mqtt_username: str | None = os.getenv("MQTT_USERNAME") or None
    mqtt_password: str | None = os.getenv("MQTT_PASSWORD") or None

    mysql_url: str = os.getenv("MYSQL_URL", "mysql+mysqlconnector://root:example@localhost:3306/maternal")

    z_threshold: float = float(os.getenv("Z_THRESHOLD", "2.5"))
    window_minutes: int = int(os.getenv("WINDOW_MINUTES", "30"))
    cooldown_seconds: int = int(os.getenv("COOLDOWN_SECONDS", "120"))
    n_of_m: tuple[int,int] = tuple(map(int, (os.getenv("N_OF_M", "2,4").split(","))))

    log_level: str = os.getenv("LOG_LEVEL", "INFO")

SETTINGS = Settings()
