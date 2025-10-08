from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
import logging
from typing import List

from . import device_manager
from .influx_client import influx_client
from .models import Device
from .mqtt_client import start_mqtt_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store MQTT client task
mqtt_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    使用 lifespan 上下文管理器来处理应用的启动和关闭事件
    """
    # Startup
    global mqtt_task
    mqtt_task = asyncio.create_task(start_mqtt_client(manager))
    logger.info("Started MQTT client task")
    
    yield  # 服务运行中
    
    # Shutdown
    if mqtt_task:
        mqtt_task.cancel()
        try:
            await mqtt_task
        except asyncio.CancelledError:
            pass
        logger.info("Cancelled MQTT client task")

# 创建 FastAPI 应用实例，使用 lifespan
app = FastAPI(lifespan=lifespan)

# Allow CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@app.get("/")
async def root():
    """Test endpoint to verify the API is running"""
    return {"status": "ok", "message": "LoRaWAN Web App Backend is running"}

# --- Device Management API ---

@app.post("/api/devices", response_model=Device)
def create_device(device: Device):
    return device_manager.save_device(device)

@app.get("/api/devices", response_model=List[Device])
def get_all_devices():
    devices = device_manager.get_devices()
    return list(devices.values())

@app.get("/api/devices/{dev_eui}", response_model=Device)
def get_device_by_eui(dev_eui: str):
    device = device_manager.get_device(dev_eui)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@app.delete("/api/devices/{dev_eui}", status_code=204)
def delete_device_by_eui(dev_eui: str):
    if not device_manager.delete_device(dev_eui):
        raise HTTPException(status_code=404, detail="Device not found")
    return

# --- Historical Data API ---

@app.get("/api/history/{dev_eui}")
def get_history(dev_eui: str, measurement: str, start: str = "-1h", stop: str = "now()"):
    """
    Get historical data for a device.
    - dev_eui: The device EUI.
    - measurement: The data field to query (e.g., 'temperature').
    - start: Start time (e.g., '-1h', '-7d', '2023-01-01T00:00:00Z').
    - stop: Stop time (defaults to now).
    """
    device = device_manager.get_device(dev_eui)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if measurement not in device.data_fields:
        raise HTTPException(status_code=400, detail=f"Invalid measurement for this device. Valid options: {device.data_fields}")
        
    data = influx_client.query_data(dev_eui, start, stop, measurement)
    return data

# --- Real-time Data WebSocket ---

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data streaming"""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected from WebSocket.")