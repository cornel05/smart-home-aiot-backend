from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DB_URL: str = "postgresql+asyncpg://smarthome:smarthome@localhost:5432/smarthome"
    MQTT_HOST: str = "localhost"
    MQTT_PORT: int = 1883
    MQTT_USER: str = ""
    MQTT_PASS: str = ""
    MQTT_TOPIC_SENSOR: str = "smarthome/sensors"
    MQTT_TOPIC_CMD: str = "smarthome/commands"
    NODE_ID: int = 1
    GAS_ALERT_THRESHOLD: float = 300.0
    TEMP_FAN_THRESHOLD: float = 26.0


settings = Settings()
