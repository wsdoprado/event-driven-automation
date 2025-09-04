from typing import Optional
from pydantic import BaseModel


#Modelos de representação do Netbox
class DeviceType(BaseModel):
    id: int
    model: str

class Site(BaseModel):
    id: int
    name: str

class Platform(BaseModel):
    id: int
    name: str

class IPAddress(BaseModel):
    id: int
    address: str

class DeviceData(BaseModel):
    id: int
    name: str
    platform: Optional[Platform] = None
    primary_ip4: Optional[IPAddress] = None
    device_type: Optional[DeviceType] = None
    site: Optional[Site] = None
    description: Optional[str] = None

class InterfaceData(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    mtu: Optional[int] = None
    enabled: Optional[bool] = None
    device: DeviceData

# Modelo principal do webhook
class NetBoxWebhook(BaseModel):
    event: str
    model: str
    timestamp: str
    username: Optional[str]
    request_id: Optional[str]
    data: InterfaceData | DeviceData