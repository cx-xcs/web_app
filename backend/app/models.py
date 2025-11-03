from pydantic import BaseModel, Field


class Device(BaseModel):
    dev_eui: str = Field(..., pattern=r"^[a-fA-F0-9]{16}$")
    device_name: str
    application_name: str
    data_format: str  # struct 格式串，如 ">ff"
    data_fields: list[str]  # 字段名数组，如 ["temperature", "humidity"]
