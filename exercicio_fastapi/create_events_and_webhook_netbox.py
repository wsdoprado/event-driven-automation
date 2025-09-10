import os, urllib3
import pynetbox
from dotenv import load_dotenv


# Carregar variáveis de ambiente do arquivo .env.dev
load_dotenv("../.env.dev")

NETBOX_URL = os.getenv("NETBOX_URL")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")
API_URL = os.getenv("API_URL")
API_URL = f"{API_URL}/webhook/netbox"

# Desabilita avisos de segurança SSL/TLS (não recomendado em produção)
urllib3.disable_warnings() #não mostra warnings de segurança relacionados a SSL/TLS

# Conecta ao Netbox
nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)

webhook_name = "FastAPIWebhook"
existing_webhook = nb.extras.webhooks.get(name=webhook_name)

# Verifica se o webhook já existe
if existing_webhook:
    print(f"Webhook '{webhook_name}' já existe (id={existing_webhook.id})")
    webhook = existing_webhook
else:
    webhook = nb.extras.webhooks.create(
        {
            "name": webhook_name,
            "payload_url": API_URL,
            "http_method": "POST",
            "enabled": True,
            "ssl_verification": False,
        }
    )
    print(f"Webhook criado '{webhook.name}' (id={webhook.id})")

# Cria os eventos (Device e Interface)
events_to_create = [
    {
        "name": "DeviceEvento",
        "object_types": ["dcim.device"],  # Device model
        "event_types": ["object_created", "object_updated", "object_deleted"],
        "action_type": "webhook",
        "action_object_type": "extras.webhook",
        "action_object_id": webhook.id,
    },
    {
        "name": "InterfaceEvento",
        "object_types": ["dcim.interface"],  # Interface model
        "event_types": ["object_created", "object_updated", "object_deleted"],
        "action_type": "webhook",
        "action_object_type": "extras.webhook",
        "action_object_id": webhook.id,
    },
]

for ev in events_to_create:
    existing = nb.extras.event_rules.get(name=ev["name"])
    if existing:
        print(f"Evento '{ev['name']}' já existe (id={existing.id})")
    else:
        event = nb.extras.event_rules.create(ev)
        print(f"Evento criado '{ev['name']}' (id={event.id})")
