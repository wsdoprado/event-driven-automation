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
    filter_xml = """
    <filter>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface/>
      </interfaces>
    </filter>
    """
    interfaces = m.get(filter=filter_xml)

# Parse e formata
xml_parsed = minidom.parseString(interfaces.xml)
pretty_xml = xml_parsed.toprettyxml(indent="  ")  # Indentação com 2 espaços

print(pretty_xml)
