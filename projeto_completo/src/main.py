import json, os, logging, asyncio

from fastapi import FastAPI, HTTPException, Request
from temporalio.client import Client
from workflows.device import DeviceWorkflow


# Instância do FastAPI
app = FastAPI(title="NetBox Webhook Receiver", version="1.0")

DEVICE_QUEUE = "DEVICE_QUEUE"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    filename="/var/log/projeto/fastapi.log",  
    filemode="a"
)
        
@app.post("/webhook/netbox")
async def receive_netbox_webhook(request: Request):
    try:
        logger = logging.getLogger("fastapi")
        
        logger.info("[INFO] FastAPI inicializado.")
        
        TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "temporal:7233")
        
        logger.info(f"[INFO] Esperando 10 segundos antes de conectar ao Temporal em: {TEMPORAL_ADDRESS}")
        await asyncio.sleep(10)  # aguarda 10 segundos
    
        TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")
        
        # Client para conexao no temporal
        temporal_client = await Client.connect(TEMPORAL_ADDRESS, namespace=TEMPORAL_NAMESPACE)
        
        # Recebe o corpo da requisição como JSON
        payload = await request.json()
        
        logger.info(f"[INFO] Webhook Recebido")
        
        # Extrair campos principais
        model = payload.get("model")
        event = payload.get("event")
        data = payload.get("data")
        #snapshots = payload.get("snapshots")
        
        if not model or not event or not data:
            raise HTTPException(status_code=400, detail="Payload incompleto.")
        
        result = await temporal_client.execute_workflow(
            DeviceWorkflow.run,
            id="operation-workflow-id",
            task_queue="worker-queue",
            args=[data],
        )

        print(f"Result: {result}")
    
    except Exception as e:
        print(f"Erro ao processar webhook: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar webhook.")