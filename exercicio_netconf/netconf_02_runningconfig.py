from ncclient import manager
from xml.dom import minidom

DEVICE = {
    "host": "192.168.100.103",
    "port": 830,
    "username": "admin",
    "password": "admin",
    "hostkey_verify": False,
}

with manager.connect(**DEVICE) as m:
    # Pega toda a configuração em execução (running)
    running_config = m.get_config(source="running")
    
    # Formata o XML para ficar legível
    xml_parsed = minidom.parseString(running_config.xml)
    pretty_xml = xml_parsed.toprettyxml(indent="  ")
    
    print(pretty_xml)
