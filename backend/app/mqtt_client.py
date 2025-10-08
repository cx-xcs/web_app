import asyncio
import logging
import json
import base64
import struct

import aiomqtt

from .settings import settings
from . import device_manager
from .influx_client import influx_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_mqtt_client(ws_manager):
    """
    连接到 EMQX，订阅主题，并处理收到的消息。
    会自动重连。
    """
    logger.info("MQTT client starting, connecting to %s:%s", settings.mqtt_hostname, settings.mqtt_port)

    while True:
        try:
            async with aiomqtt.Client(
                hostname=settings.mqtt_hostname,
                port=int(settings.mqtt_port),
                username=settings.mqtt_username or None,
                password=settings.mqtt_password or None,
            ) as client:
                logger.info("Connected to MQTT broker")
                
                await client.subscribe(settings.mqtt_topic)
                logger.info(f"Subscribed to topic: {settings.mqtt_topic}")
                
                async for message in client.messages:
                    try:
                        payload_str = message.payload.decode()
                        logger.debug(f"Received message on topic '{message.topic}': {payload_str}")
                        
                        # 1. 解析 JSON payload
                        data = json.loads(payload_str)
                        dev_eui = data.get("devEUI")
                        if not dev_eui:
                            logger.warning("Message without devEUI received. Skipping.")
                            continue

                        # 2. 查找设备配置
                        device = device_manager.get_device(dev_eui)
                        if not device:
                            logger.warning(f"No configuration found for device {dev_eui}. Skipping.")
                            continue

                        # 3. 解码 base64 数据
                        raw_data = base64.b64decode(data["data"])
                        
                        # 4. 使用设备的格式字符串解包二进制数据
                        unpacked_data = struct.unpack(device.data_format, raw_data)
                        
                        # 5. 创建解码后的数据字典
                        decoded_payload = dict(zip(device.data_fields, unpacked_data))
                        
                        logger.info(f"Decoded data for {dev_eui}: {decoded_payload}")

                        # 6. 写入 InfluxDB
                        influx_client.write_data(
                            dev_eui=dev_eui,
                            device_name=device.device_name,
                            data=decoded_payload
                        )

                        # 7. 广播到 WebSocket 客户端
                        realtime_data = {
                            "dev_eui": dev_eui,
                            "device_name": device.device_name,
                            "timestamp": data.get("timestamp"),
                            "data": decoded_payload
                        }
                        await ws_manager.broadcast(json.dumps(realtime_data))

                    except json.JSONDecodeError:
                        logger.error("Failed to decode JSON from message payload.")
                    except base64.binascii.Error:
                        logger.error("Failed to decode base64 data.")
                    except struct.error as e:
                        logger.error(f"Failed to unpack data for {dev_eui}: {e}. Check data_format.")
                    except Exception as e:
                        logger.error(f"An unexpected error occurred: {e}")

        except aiomqtt.MqttError as error:
            logger.error(f"MQTT error: '{error}'. Reconnecting in 5 seconds.")
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            logger.info("MQTT client task cancelled.")
            break
        except Exception as e:
            logger.error(f"Unexpected error in MQTT loop: {e}")
            await asyncio.sleep(5)
