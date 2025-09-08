from xml.dom import minidom
from ncclient import manager
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env.dev
load_dotenv("../.env.dev")

USER_DEVICE = os.getenv("USER_DEVICE")
PASSW_DEVICE = os.getenv("PASSW_DEVICE")

DEVICE = {
    "host": "192.168.100.103",
    "port": 830,
    "username": f"{USER_DEVICE}",
    "password": f"{PASSW_DEVICE}",
    "hostkey_verify": False,
}


with manager.connect(**DEVICE) as m:
    print("=== Capabilities do dispositivo ===")
    for cap in m.server_capabilities:
        print(cap)
