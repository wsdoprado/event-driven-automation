import json
from fastapi import FastAPI, HTTPException, Request

# Instância do FastAPI
app = FastAPI(title="NetBox Webhook Receiver", version="1.0")


@app.post("/webhook/netbox")
async def receive_netbox_webhook(request: Request):
    """
    Endpoint para receber webhooks do NetBox.

    Exemplo de payload esperado:
    {
        "model": "dcim.device",
        "event": "created",
        "data": { ... informações do objeto ... }
    }
    """
    try:
        # Recebe o corpo da requisição como JSON
        payload = await request.json()
        print(f"Webhook Recebido ")

        # Extrair campos principais
        model = payload.get("model")
        event = payload.get("event")
        data = payload.get("data")

        print(f"Data: {json.dumps(data, indent=2)}")
        # Validação básica
        if not model or not event or not data:
            raise HTTPException(status_code=400, detail="Payload incompleto.")

    except Exception as e:
        print(f"Erro ao processar webhook: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar webhook.")