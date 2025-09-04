from temporalio import activity
from dotenv import load_dotenv
import os, json, logging, requests, urllib3

load_dotenv()
urllib3.disable_warnings()

NETBOX_URL = os.getenv("NETBOX_URL")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")

HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': 'Token '+str(NETBOX_TOKEN)
}

@activity.defn
async def get_device_restapi(device_id: int) -> dict:    
    try:
        activity.logger.info(f"[INFO] url: {NETBOX_URL}")
        activity.logger.info(f"[INFO] token: {NETBOX_TOKEN}")
        url = f"{str(NETBOX_URL)}api/dcim/devices/{device_id}/"
        response = requests.get(url=url, headers=HEADERS, verify=False)
        activity.logger.info(f"Response: {response}")

        response.raise_for_status()  # Garante que status HTTP é 200

        json_data = response.json()
        device_name = json_data.get("name") 

        # IP de gerenciamento (verifica IPv4 ou IPv6)
        primary_ip4 = json_data.get("primary_ip4")
        primary_ip6 = json_data.get("primary_ip6")
        
        management_ip = None
        if primary_ip4 and "address" in primary_ip4:
            management_ip = primary_ip4["address"]
        elif primary_ip6 and "address" in primary_ip6:
            management_ip = primary_ip6["address"]
        management_ip = str(management_ip).split("/")[0]
        
        platform = json_data.get("platform").get("name")
        
        return {"device_name": device_name, "device_mgmt": management_ip, "platform": platform}

    except requests.exceptions.HTTPError as http_err:
        activity.logger.info(f"[ERROR] HTTP error occurred: {http_err}")
        raise
    except Exception as err:
        activity.logger.info(f"[ERROR] Other error occurred: {err}")
        raise