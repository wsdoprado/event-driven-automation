import os, requests, urllib3
from dotenv import load_dotenv
import pynetbox

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

urllib3.disable_warnings()

NETBOX_URL = os.getenv("NETBOX_URL")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")

if not NETBOX_URL or not NETBOX_TOKEN:
    raise ValueError("Por favor, configure as variáveis NETBOX_URL e NETBOX_TOKEN no .env")

# Criar uma sessão personalizada
session = requests.Session()
session.verify = False  # Desabilitar a verificação SSL

# Conectar à API do NetBox
nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN, )

nb.http_session = session

# Criar fabricantes
manufacturers = [
    {"name": "Cisco", "slug": "cisco"},
    {"name": "Arista", "slug": "arista"}
]

manufacturer_ids = {}
for m in manufacturers:
x    manufacturer = nb.dcim.manufacturers.create(**m)
    manufacturer_ids[m['slug']] = manufacturer.id

# Criar plataformas
platforms = [
    {"name": "Cisco IOS", "slug": "cisco-ios"},
    {"name": "Arista EOS", "slug": "arista-eos"}
]

platform_ids = {}
for p in platforms:
    platform = nb.dcim.platforms.create(**p)
    platform_ids[p['slug']] = platform.id

# Criar tipos de dispositivos com interfaces
device_types = [
    {
        "manufacturer": manufacturer_ids["cisco"],
        "model": "Cisco IOS",
        "slug": "cisco-ios",
        "u_height": 1,
        "interfaces": [
            {"name": "Ethernet0/1", "type": "1000base-t"},
            {"name": "Ethernet0/2", "type": "1000base-t"},
            {"name": "Ethernet0/3", "type": "1000base-t"},
            {"name": "Ethernet0/0", "type": "1000base-t", "mgmt_only": True}
        ]
    },
    {
        "manufacturer": manufacturer_ids["arista"],
        "model": "Arista CEOS",
        "slug": "arista-ceos",
        "u_height": 1,
        "interfaces": [
            {"name": "Ethernet1", "type": "1000base-t"},
            {"name": "Ethernet2", "type": "1000base-t"},
            {"name": "Ethernet3", "type": "1000base-t"},
            {"name": "Ethernet4", "type": "1000base-t"},
            {"name": "Management0", "type": "1000base-t", "mgmt_only": True}
        ]
    }
]

for dt in device_types:
    nb.dcim.device_types.create(
        manufacturer=dt["manufacturer"],
        model=dt["model"],
        slug=dt["slug"],
        u_height=dt["u_height"],
        interfaces=dt["interfaces"]
    )

# Criar regioes
regions = [
    {"name": "Sao Paulo", "slug": "sp"},
    {"name": "Rio de Janeiro", "slug": "rj"},
    {"name": "Fortaleza", "slug": "ce"},
    {"name": "Belo Horizonte", "slug": "mg"}
]

for r in regions:
    nb.dcim.regions.create(**r)

# Criar sites em cada região
sites = [
    {"name": "Sao Paulo", "slug": "sp-site", "region": "sp"},
    {"name": "Rio de Janeiro", "slug": "rj-site", "region": "rj"},
    {"name": "Fortaleza", "slug": "ce-site", "region": "ce"},
    {"name": "Belo Horizonte", "slug": "mg-site", "region": "mg"}
]

for site_data in sites:
    region = nb.dcim.regions.get(slug=site_data["region"])
    if region:
        site = nb.dcim.sites.create(
            name=site_data["name"],
            slug=site_data["slug"],
            region=region.id
        )
        print(f"Site criado: {site.name} (ID {site.id})")
    else:
        print(f"Regiao {site_data['region']} nao encontrada. Site {site_data['name']} nao criado.")
