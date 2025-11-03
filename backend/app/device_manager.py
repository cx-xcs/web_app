import json
from pathlib import Path
from typing import Optional, Dict

from .models import Device

DEVICES_FILE = Path(__file__).resolve().parents[1] / "devices.json"


def _read() -> Dict[str, Device]:
    if DEVICES_FILE.exists():
        with open(DEVICES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {eui: Device(**payload) for eui, payload in data.items()}
    return {}


def _write(devices: Dict[str, Device]) -> None:
    with open(DEVICES_FILE, "w", encoding="utf-8") as f:
        json.dump({eui: dev.model_dump() for eui, dev in devices.items()}, f, indent=2, ensure_ascii=False)


def get_devices() -> Dict[str, Device]:
    return _read()


def get_device(dev_eui: str) -> Optional[Device]:
    return _read().get(dev_eui)


def save_device(device: Device) -> Device:
    devices = _read()
    devices[device.dev_eui] = device
    _write(devices)
    return device


def delete_device(dev_eui: str) -> bool:
    devices = _read()
    if dev_eui in devices:
        del devices[dev_eui]
        _write(devices)
        return True
    return False
