from pydantic import BaseModel, Field


class Device(BaseModel):
    dev_eui: str = Field(..., description="Device EUI", pattern=r"^[a-fA-F0-9]{16}$")
    device_name: str = Field(..., description="Device Name")
    application_name: str = Field(..., description="Application Name")
    # Using struct format string to decode data. e.g., ">ff" for 2 big-endian floats
    data_format: str = Field(..., description="Payload format string for struct.unpack")
    # e.g., ["temperature", "humidity"]
    data_fields: list[str] = Field(..., description="List of field names for decoded data")
