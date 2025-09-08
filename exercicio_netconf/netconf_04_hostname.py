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

new_hostname = "Core-Router-adilson"

config_payload = f"""
<config>
  <system xmlns="http://openconfig.net/yang/system">
    <config>
      <hostname>{new_hostname}</hostname>
    </config>
  </system>
</config>
"""

with manager.connect(**DEVICE) as m:
    m.edit_config(target="running", config=config_payload)
    print(f"Hostname alterado para {new_hostname}")
