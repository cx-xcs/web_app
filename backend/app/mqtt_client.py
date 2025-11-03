import asyncio
import logging
import json
import base64
import struct

import aiomqtt

from .settings import settings
from . import device_manager
from .influx_client import influx_client

logger = logging.getLogger(__name__)

async def start_mqtt_client(ws_manager):
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
                        data = json.loads(message.payload.decode())
                        dev_eui = data.get("devEUI")
                        if not dev_eui:
                            logger.warning("Message without devEUI received. Skipping.")
                            continue

                        # 跳过 JOIN 消息或其他没有数据的消息
                        if "data" not in data:
                            continue

                        device = device_manager.get_device(dev_eui)
                        if not device:
                            logger.warning("No configuration for %s. Skipping.", dev_eui)
                            continue

                        decoded = dict(zip(
                            device.data_fields,
                            struct.unpack(device.data_format, base64.b64decode(data["data"]))
                        ))

                        # 传递时间戳（如果有）
                        timestamp = data.get("timestamp")
                        influx_client.write_data(dev_eui=dev_eui, device_name=device.device_name, data=decoded, timestamp=timestamp)
                        logger.info(f"Data received and stored for {dev_eui}: {device.device_name}")

                        realtime = {"dev_eui": dev_eui, "device_name": device.device_name, "timestamp": data.get("timestamp"), "data": decoded}
                        await ws_manager.broadcast(json.dumps(realtime))

                    except Exception as e:
                        logger.error("Process message error: %s", e)
        except aiomqtt.MqttError as error:
            logger.error("MQTT error: '%s'. Reconnecting in 5s.", error)
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            logger.info("MQTT client task cancelled.")
            break
        except Exception as e:
            logger.error("Unexpected error in MQTT loop: %s", e)
            await asyncio.sleep(5)
