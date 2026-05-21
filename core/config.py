from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DB_URL: str = "postgresql+asyncpg://smarthome:smarthome@localhost:5432/smarthome"
    MQTT_HOST: str = "localhost"
    MQTT_PORT: int = 1883
    MQTT_USER: str = ""
    MQTT_PASS: str = ""
    AIO_USERNAME: str = "your_username"
    MQTT_TOPIC_TEMP: str = "smarthome.temperature"
    MQTT_TOPIC_HUM: str = "smarthome.humidity"
    MQTT_TOPIC_LIGHT: str = "smarthome.light"
    MQTT_TOPIC_IR: str = "smarthome.ir-motion"
    MQTT_TOPIC_CMD: str = "smarthome/commands"
    MQTT_TOPIC_SENSOR: str = "smarthome/sensors"
    GAS_ALERT_THRESHOLD: float = 300.0
    NODE_ID: int = 1
    TEMP_FAN_THRESHOLD: float = 26.0
    LIGHT_ON_THRESHOLD: float = 200.0
    ACTUATOR_PIN_MAP: dict[str, int] = Field(default_factory=lambda: {"fan": 10, "light": 13})


settings = Settings()
