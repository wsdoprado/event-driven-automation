from ncclient import manager
from xml.dom import minidom
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env.dev
load_dotenv("../.env.dev")

USER_DEVICE = os.getenv("USER_DEVICE")
PASSW_DEVICE = os.getenv("PASSW_DEVICE")

DEVICE = {
    "host": "2001:db8:100::101",
    "port": 830,
    "username": f"{USER_DEVICE}",
    "password": f"{PASSW_DEVICE}",
    "hostkey_verify": False,
}

with manager.connect(**DEVICE) as m:
    # Pega toda a configuração em execução (running)
    running_config = m.get_config(source="running")
    
    # Formata o XML para ficar legível
    xml_parsed = minidom.parseString(running_config.xml)
    pretty_xml = xml_parsed.toprettyxml(indent="  ")
    
    print(pretty_xml)
