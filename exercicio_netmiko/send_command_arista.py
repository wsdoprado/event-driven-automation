from netmiko import ConnectHandler
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env.dev
load_dotenv("../.env.dev")

USER_DEVICE = os.getenv("USER_DEVICE")
PASSW_DEVICE = os.getenv("PASSW_DEVICE")

device = {
    "device_type": "arista_eos",
    "ip": "2001:db8:100::101",
    "username": f"{USER_DEVICE}",
    "password": f"{PASSW_DEVICE}",
}

conn = ConnectHandler(**device)
output = conn.send_command("show version")
print(output)
conn.disconnect()
