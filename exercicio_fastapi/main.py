from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel

# Instância do FastAPI
app = FastAPI(title="NetBox Webhook Receiver", version="1.0")


#Modelos de representação do Netbox
class DeviceType(BaseModel):
    id: int
    model: str

class Site(BaseModel):
    id: int
    name: str

class DeviceData(BaseModel):
    id: int
    name: str
    device_type: DeviceType
    site: Site
    description: Optional[str] = None

# Modelo principal do webhook
class NetBoxWebhook(BaseModel):
    event: str
    model: str
    timestamp: str
    username: Optional[str]
    request_id: Optional[str]
    data: DeviceData


@app.post("/webhook/netbox")
async def receive_netbox_webhook(payload: NetBoxWebhook):
    """
    Endpoint para receber webhooks do NetBox.

    Exemplo de payload esperado em json:
    {
        "model": "dcim.device",
        "event": "created",
        "data": { ... informações do objeto ... }
    }
    """

    print(f"Evento recebido: {payload.event}")
    print(f"Modelo afetado: {payload.model}")
    print(f"Usuário envolvido: {payload.username}")
    print(f"Dados do modelo: {payload.data}")