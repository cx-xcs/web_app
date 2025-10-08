import logging
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from .settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InfluxClient:
    def __init__(self):
        self.client = InfluxDBClient(
            url=settings.influxdb_url,
            token=settings.influxdb_token,
            org=settings.influxdb_org
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
        logger.info("InfluxDB client initialized.")

    def write_data(self, dev_eui: str, device_name: str, data: dict):
        """
        Writes decoded sensor data to InfluxDB.
        'data' is a dictionary of field names to values, e.g., {"temperature": 25.5, "humidity": 60.1}
        """
        try:
            point = Point("sensor_data") \
                .tag("dev_eui", dev_eui) \
                .tag("device_name", device_name)
            
            for field, value in data.items():
                point = point.field(field, value)

            self.write_api.write(bucket=settings.influxdb_bucket, record=point)
            logger.info(f"Successfully wrote data for {dev_eui}: {data}")
        except Exception as e:
            logger.error(f"Error writing to InfluxDB for {dev_eui}: {e}")

    def query_data(self, dev_eui: str, start: str, stop: str, measurement: str):
        """Queries historical data from InfluxDB."""
        query = f'''
        from(bucket: "{settings.influxdb_bucket}")
        |> range(start: {start}, stop: {stop})
        |> filter(fn: (r) => r["_measurement"] == "sensor_data")
        |> filter(fn: (r) => r["dev_eui"] == "{dev_eui}")
        |> filter(fn: (r) => r["_field"] == "{measurement}")
        |> yield(name: "mean")
        '''
        try:
            result = self.query_api.query(query, org=settings.influxdb_org)
            results = []
            for table in result:
                for record in table.records:
                    results.append({"time": record.get_time(), "value": record.get_value()})
            return results
        except Exception as e:
            logger.error(f"Error querying InfluxDB for {dev_eui}: {e}")
            return []


influx_client = InfluxClient()
