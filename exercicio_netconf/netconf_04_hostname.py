from ncclient import manager

DEVICE = {
    "host": "192.168.100.103",
    "port": 830,
    "username": "admin",
    "password": "admin",
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
