from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(Path(__file__).resolve().parents[1] / ".env"), env_file_encoding="utf-8")

    mqtt_hostname: str = Field("localhost", env="MQTT_HOSTNAME")
    mqtt_port: int = Field(1883, env="MQTT_PORT")
    mqtt_username: str | None = Field(None, env="MQTT_USERNAME")
    mqtt_password: str | None = Field(None, env="MQTT_PASSWORD")
    mqtt_topic: str = Field("application/+/device/+/rx", env="MQTT_TOPIC")

    influxdb_url: str = Field("http://localhost:8086", env="INFLUXDB_URL")
    influxdb_token: str = Field("", env="INFLUXDB_TOKEN")
    influxdb_org: str = Field("", env="INFLUXDB_ORG")
    influxdb_bucket: str = Field("sensor_data", env="INFLUXDB_BUCKET")


settings = Settings()
