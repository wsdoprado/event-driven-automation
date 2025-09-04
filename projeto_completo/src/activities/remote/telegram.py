import requests
import asyncio
import os
from temporalio import activity

# Carrega variáveis de ambiente
CHAT_ID = os.getenv("CHAT_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")

@activity.defn
async def send_message(message: str) -> dict:
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message}

        # Executa requests.post em uma thread separada
        response = await asyncio.to_thread(requests.post, url, data=data)
        response.raise_for_status()

        return {"data": "", "status": True}

    except requests.exceptions.HTTPError as http_err:
        activity.logger.info(f"[ERROR] HTTP error occurred: {http_err}")
        raise
    except Exception as err:
        activity.logger.info(f"[ERROR] Other error occurred: {err}")
        raise
