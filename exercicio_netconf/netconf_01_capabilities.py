from xml.dom import minidom
from ncclient import manager

DEVICE = {
    "host": "192.168.100.103",
    "port": 830,
    "username": "admin",
    "password": "admin",
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
