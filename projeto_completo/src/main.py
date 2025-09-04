"""
FastAPI Webhook Receiver para NetBox integrado ao Temporal

Este serviço recebe webhooks enviados pelo NetBox quando há mudanças
em dispositivos ou interfaces e aciona workflows no Temporal para
sincronizar a configuração nos dispositivos de rede.

Fluxo principal:
1. Receber webhook JSON do NetBox (device/interface).
2. Validar payload e extrair dados relevantes (via Pydantic).
3. Acionar workflow no Temporal (DeviceWorkflow ou InterfaceWorkflow).
4. Retornar status da execução ao cliente.
"""

import os
import logging
import asyncio
from fastapi import FastAPI, HTTPException, Request
from temporalio.client import Client
from utils import NetBoxWebhook

# Importação dos workflows
from workflows.device import DeviceWorkflow
from workflows.interface import InterfaceWorkflow


# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    filename="/var/log/projeto/fastapi.log",  
    filemode="a"
)

# Instância do FastAPI
app = FastAPI(
    title="NetBox Webhook Receiver", 
    version="1.0"
)

# Constantes das filas do Temporal
DEVICE_QUEUE = "DEVICE_QUEUE"
INTERFACE_QUEUE = "INTERFACE_QUEUE"

TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "temporal:7233")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")

@app.post("/webhook/netbox")
async def receive_netbox_webhook(payload: NetBoxWebhook):
    """
    Endpoint que recebe webhooks do NetBox e inicia workflows no Temporal.

    Payload esperado:
    {
        "model": "device" | "interface",
        "event": "created" | "updated" | "deleted",
        "data": {...},            # Dados principais do objeto
        "snapshots": {...}        # (opcional) Estado anterior
    }
    """
    logger = logging.getLogger("fastapi")
    logger.info("[INFO] FastAPI inicializado.")
    logger.info(f"[INFO] Esperando 10 segundos antes de conectar ao Temporal em: {TEMPORAL_ADDRESS}")

    await asyncio.sleep(10)  # aguarda 10 segundos

    # Client para conexao no temporal
    temporal_client = await Client.connect(TEMPORAL_ADDRESS, namespace=TEMPORAL_NAMESPACE)

    logger.info(f"[INFO] Webhook Recebido")

    # Extrair campos principais
    model = payload.model
    # event = payload.event
    data = payload.data

    # Disparo do workflow DeviceWorkflow
    if model == "device":
        await temporal_client.execute_workflow(
            DeviceWorkflow.run,
            id="workflow-device-id",
            task_queue=DEVICE_QUEUE,
            args=[data],
        )

    # Disparo do workflow InterfaceWorkflow
    if model == "interface":
        await temporal_client.execute_workflow(
            InterfaceWorkflow.run,
            id="workflow-interface-id",
            task_queue=INTERFACE_QUEUE,
            args=[data],
        )