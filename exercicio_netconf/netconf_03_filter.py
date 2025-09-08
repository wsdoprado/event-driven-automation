from ncclient import manager
from xml.dom import minidom
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
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/>
    </filter>
    """

    running_interfaces = m.get_config(source="running", filter=filter_xml)
    
    # Formata o XML para ficar legível
    xml_parsed = minidom.parseString(running_interfaces.xml)
    pretty_xml = xml_parsed.toprettyxml(indent="  ")
    
    print(pretty_xml)
