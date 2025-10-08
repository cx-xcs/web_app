import json
from pathlib import Path
from typing import Optional

from .models import Device

# Use a simple JSON file to store device configurations
DEVICES_FILE = Path(__file__).parent.parent / "devices.json"


def get_devices() -> dict[str, Device]:
    """Loads all devices from the JSON file."""
    if not DEVICES_FILE.exists():
        return {}
    with open(DEVICES_FILE, "r") as f:
        data = json.load(f)
    return {dev_eui: Device(**device_data) for dev_eui, device_data in data.items()}


def get_device(dev_eui: str) -> Optional[Device]:
    """Gets a single device by its EUI."""
    devices = get_devices()
    return devices.get(dev_eui)


def save_device(device: Device) -> Device:
    """Saves a device to the JSON file."""
    devices = get_devices()
    devices[device.dev_eui] = device
    with open(DEVICES_FILE, "w") as f:
        # Pydantic's model_dump is used to get a dict from the model instance
        json.dump(
            {eui: dev.model_dump() for eui, dev in devices.items()}, f, indent=4
        )
    return device


def delete_device(dev_eui: str) -> bool:
    """Deletes a device from the JSON file."""
    devices = get_devices()
    if dev_eui in devices:
        del devices[dev_eui]
        with open(DEVICES_FILE, "w") as f:
            json.dump(
                {eui: dev.model_dump() for eui, dev in devices.items()}, f, indent=4
            )
        return True
    return False
