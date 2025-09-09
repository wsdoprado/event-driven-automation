import os, requests, urllib3
from dotenv import load_dotenv
import pynetbox

# Carregar variáveis de ambiente do arquivo .env.dev
load_dotenv("../.env.dev")

NETBOX_URL = os.getenv("NETBOX_URL")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")

# Desabilita avisos de segurança SSL/TLS (não recomendado em produção)
urllib3.disable_warnings() #não mostra warnings de segurança relacionados a SSL/TLS

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
    {"name": "Arista", "slug": "arista"}
]

manufacturer_ids = {}
for m in manufacturers:
    manufacturer = nb.dcim.manufacturers.get(slug=m["slug"])
    if manufacturer:
        print(f"✅ Fabricante já existe: {manufacturer.name} (ID {manufacturer.id})")
    else:
        manufacturer = nb.dcim.manufacturers.create(**m)
        print(f"🆕 Fabricante criado: {manufacturer.name} (ID {manufacturer.id})")
    manufacturer_ids[m["slug"]] = manufacturer.id

# Criar plataformas
platforms = [
    {"name": "eos", "slug": "eos"}
]

platform_ids = {}
for p in platforms:
    platform = nb.dcim.platforms.get(slug=p["slug"])
    if platform:
        print(f"✅ Plataforma já existe: {platform.name} (ID {platform.id})")
    else:
        platform = nb.dcim.platforms.create(**p)
        print(f"🆕 Plataforma criada: {platform.name} (ID {platform.id})")
    platform_ids[p["slug"]] = platform.id

# Criar regioes
regions = [
    {"name": "Sao Paulo", "slug": "sp"},
    {"name": "Rio de Janeiro", "slug": "rj"},
    {"name": "Fortaleza", "slug": "ce"},
    {"name": "Belo Horizonte", "slug": "mg"},
    {"name": "Salvador", "slug": "ba"}
]

# Criar regiões
for r in regions:
    region = nb.dcim.regions.get(slug=r["slug"])
    if region:
        print(f"✅ Região já existe: {region.name} (ID {region.id})")
    else:
        region = nb.dcim.regions.create(**r)
        print(f"🆕 Região criada: {region.name} (ID {region.id})")

# Criar sites em cada região
sites = [
    {"name": "POP-SP", "slug": "pop-sp", "region": "sp"},
    {"name": "POP-RJ", "slug": "pop-rj", "region": "rj"},
    {"name": "POP-CE", "slug": "pop-ce", "region": "ce"},
    {"name": "POP-MG", "slug": "pop-mg", "region": "mg"},
    {"name": "POP-BA", "slug": "pop-ba", "region": "ba"}
]

# Criar sites
for site_data in sites:
    region = nb.dcim.regions.get(slug=site_data["region"])
    if region:
        site = nb.dcim.sites.get(slug=site_data["slug"])
        if site:
            print(f"✅ Site já existe: {site.name} (ID {site.id})")
        else:
            site = nb.dcim.sites.create(
                name=site_data["name"],
                slug=site_data["slug"],
                region=region.id
            )
            print(f"🆕 Site criado: {site.name} (ID {site.id})")
    else:
        print(f"❌ Região {site_data['region']} não encontrada. Site {site_data['name']} não criado.")
     
# Criar roles: P, PE e L2
roles = [
    {"name": "Spine", "slug": "spine", "color": "ff0000"},
    {"name": "Leaf", "slug": "leaf", "color": "0000ff"}
]        

role_ids = {}
for r in roles:
    role = nb.dcim.device_roles.get(slug=r["slug"])
    if role:
        print(f"✅ Role já existe: {role.name} (ID {role.id})")
    else:
        role = nb.dcim.device_roles.create(**r)
        print(f"🆕 Role criado: {role.name} (ID {role.id})")
    role_ids[r["slug"]] = role.id

# Criar tenants: Producao e Laboratorio
tenants = [
    {"name": "producao", "slug": "producao"},
    {"name": "laboratorio", "slug": "laboratorio"},
]

tenant_ids = {}
for t in tenants:
    tenant = nb.tenancy.tenants.get(slug=t["slug"])
    if tenant:
        print(f"✅ Tenant já existe: {tenant.name} (ID {tenant.id})")
    else:
        tenant = nb.tenancy.tenants.create(**t)
        print(f"🆕 Tenant criado: {tenant.name} (ID {tenant.id})")
    tenant_ids[t["slug"]] = tenant.id
                
# Criar tipos de dispositivos com interfaces
device_types = [
    {
        "manufacturer": manufacturer_ids["arista"],
        "model": "Arista CEOS",
        "slug": "arista-ceos",
        "u_height": 1,
        "interfaces": [
            {"name": "Ethernet1", "type": "1000base-t", "mtu": "9214"},
            {"name": "Ethernet2", "type": "1000base-t", "mtu": "9214"},
            {"name": "Ethernet3", "type": "1000base-t", "mtu": "9214"},
            {"name": "Management0", "type": "1000base-t", "mtu": "9214", "mgmt_only": True}
        ]
    }
]

# Criar tipos de dispositivos com interfaces
for dt in device_types:
    device_type = nb.dcim.device_types.get(slug=dt["slug"])
    if device_type:
        print(f"✅ Device Type já existe: {device_type.model} (ID {device_type.id})")
    else:
        device_type = nb.dcim.device_types.create(
            manufacturer=dt["manufacturer"],
            model=dt["model"],
            slug=dt["slug"],
            u_height=dt["u_height"],
        )
        print(f"🆕 Device Type criado: {device_type.model} (ID {device_type.id})")

    # Criar interface templates (se não existirem ainda)
    for iface in dt["interfaces"]:
        existing_ifaces = nb.dcim.interface_templates.filter(
            device_type_id=device_type.id,
            name=iface["name"]
        )
        if existing_ifaces:
            print(f"   ✅ Interface template já existe: {iface['name']}")
        else:
            iface_template = nb.dcim.interface_templates.create(
                device_type=device_type.id,
                name=iface["name"],
                type=iface["type"],
                mgmt_only=iface.get("mgmt_only", False)
            )
            print(f"   🆕 Interface template criada: {iface_template.name}")

# Devices + IPs de gerência
devices_to_create = [
    {"name": "spine-01", "slug": "arista-ceos", "site": "pop-sp", "role": "spine", "mgmt_ip": "192.168.100.101/24", "mgmt_ip6": "2001:db8:100::101/64", "tenant": "producao", "platform": "eos"},
    {"name": "spine-02", "slug": "arista-ceos", "site": "pop-rj", "role": "spine", "mgmt_ip": "192.168.100.102/24", "mgmt_ip6": "2001:db8:100::102/64", "tenant": "producao", "platform": "eos"},
    {"name": "leaf-01", "slug": "arista-ceos", "site": "pop-ce", "role": "leaf", "mgmt_ip": "192.168.100.103/24", "mgmt_ip6": "2001:db8:100::103/64", "tenant": "producao", "platform": "eos"},
    {"name": "leaf-02", "slug": "arista-ceos", "site": "pop-mg", "role": "leaf", "mgmt_ip": "192.168.100.104/24", "mgmt_ip6": "2001:db8:100::104/64", "tenant": "producao", "platform": "eos"},
    {"name": "leaf-03", "slug": "arista-ceos", "site": "pop-ba", "role": "leaf", "mgmt_ip": "192.168.100.105/24", "mgmt_ip6": "2001:db8:100::105/64", "tenant": "producao", "platform": "eos"}
]

for dev in devices_to_create:
    site = nb.dcim.sites.get(slug=dev["site"])
    device_type = nb.dcim.device_types.get(slug=dev["slug"])
    platform = nb.dcim.platforms.get(slug=dev["platform"])
    role_id = role_ids[dev["role"]]
    tenant_id = tenant_ids[dev["tenant"]]

    if not site or not device_type:
        print(f"❌ Erro: Site {dev['site']} ou DeviceType {dev['slug']} não encontrado.")
        continue

    # Criar ou buscar device
    device = nb.dcim.devices.get(name=dev["name"])
    if device:
        print(f"✅ Device já existe: {device.name} (ID {device.id})")
    else:
        device = nb.dcim.devices.create(
            name=dev["name"],
            device_type=device_type.id,
            site=site.id,
            platform=platform.id if platform else None,
            status="active",
            role=role_id,
            tenant=tenant_id
        )
        print(f"🆕 Device criado: {device.name} (ID {device.id})")

    # Determinar interface de gerenciamento
    mgmt_iface_name = "Management0"
    mgmt_iface = nb.dcim.interfaces.get(device_id=device.id, name=mgmt_iface_name)
    if not mgmt_iface:
        print(f"❌ Interface de gerenciamento {mgmt_iface_name} não encontrada no device {device.name}")
        continue

    # Criar ou buscar IP de gerenciamento v4
    ip4 = None
    if dev.get("mgmt_ip"):
        ip4 = nb.ipam.ip_addresses.get(address=dev["mgmt_ip"])
        if not ip4:
            ip4 = nb.ipam.ip_addresses.create(
                address=dev["mgmt_ip"],
                assigned_object_type="dcim.interface",
                assigned_object_id=mgmt_iface.id,
                status="active"
            )
            print(f"🆕 IPv4 {ip4.address} associado a {device.name}:{mgmt_iface.name}")
        else:
            print(f"✅ IPv4 {ip4.address} já existe")
     
    # Criar ou buscar IP de gerenciamento v6
    ip6 = None
    if dev.get("mgmt_ip6"):
        ip6 = nb.ipam.ip_addresses.get(address=dev["mgmt_ip6"])
        if not ip6:
            ip6 = nb.ipam.ip_addresses.create(
                address=dev["mgmt_ip6"],
                assigned_object_type="dcim.interface",
                assigned_object_id=mgmt_iface.id,
                status="active"
            )
            print(f"🆕 IPv6 {ip6.address} associado a {device.name}:{mgmt_iface.name}")
        else:
            print(f"✅ IPv6 {ip6.address} já existe")
                    
    # Marcar como IP principal do device
    update_data = {}
    if ip4:
        update_data["primary_ip4"] = ip4.id
    if ip6:
        update_data["primary_ip6"] = ip6.id
    if update_data:
        device.update(update_data)
        print(f"✅ Device {device.name} atualizado com IPs principais: {update_data}")
