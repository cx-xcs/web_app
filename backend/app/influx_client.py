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

    def write_data(self, dev_eui: str, device_name: str, data: dict, timestamp=None):
        """
        Writes decoded sensor data to InfluxDB.
        'data' is a dictionary of field names to values, e.g., {"temperature": 25.5, "humidity": 60.1}
        'timestamp' is optional Unix timestamp (seconds or milliseconds) or datetime object
        """
        try:
            point = Point("sensor_data") \
                .tag("dev_eui", dev_eui) \
                .tag("device_name", device_name)
            
            # 设置时间戳（如果提供）
            if timestamp is not None:
                from datetime import datetime, timezone
                # 如果是数字，假设是 Unix 时间戳
                if isinstance(timestamp, (int, float)):
                    # 判断是秒还是毫秒（如果大于某个值，认为是毫秒）
                    if timestamp > 10**10:  # 大于2286年，认为是毫秒
                        dt = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
                    else:
                        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                    point = point.time(dt)
                elif isinstance(timestamp, datetime):
                    point = point.time(timestamp)
            
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

    def query_latest_data(self, dev_eui: str):
        """查询设备的最新数据（所有字段）"""
        from . import device_manager
        device = device_manager.get_device(dev_eui)
        if not device:
            return None
        
        query = f'''
        from(bucket: "{settings.influxdb_bucket}")
        |> range(start: -7d)
        |> filter(fn: (r) => r["_measurement"] == "sensor_data")
        |> filter(fn: (r) => r["dev_eui"] == "{dev_eui}")
        |> group(columns: ["_field"])
        |> last()
        '''
        
        try:
            result = self.query_api.query(query, org=settings.influxdb_org)
            
            if not result:
                return None
            
            # 构造返回数据
            data = {"dev_eui": dev_eui, "device_name": device.device_name}
            timestamp = None
            
            for table in result:
                for record in table.records:
                    field_name = record.get_field()
                    value = record.get_value()
                    data[field_name] = value
                    
                    # 获取时间戳
                    if timestamp is None:
                        timestamp = record.get_time()
            
            if timestamp:
                data["timestamp"] = timestamp.isoformat()
            
            return data if len(data) > 2 else None  # 至少有 dev_eui, device_name 和一个字段
            
        except Exception as e:
            logger.error(f"Error querying latest data for {dev_eui}: {e}")
            return None


influx_client = InfluxClient()
