from temporalio import activity

import os, json, logging, requests, urllib3

# Desabilita avisos de SSL (usado porque verify=False está ativo nas chamadas requests)
urllib3.disable_warnings()

# Variáveis de ambiente para acessar o NetBox
NETBOX_URL = os.getenv("NETBOX_URL")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")

# Cabeçalhos usados em todas as chamadas à API do NetBox
HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': 'Token '+str(NETBOX_TOKEN)
}

@activity.defn
async def get_device_restapi(device_id: int) -> dict:
    """
    Atividade do Temporal para buscar informações de um device no NetBox.

    Args:
        device_id (int): ID do device no NetBox.

    Returns:
        dict: Informações do device, contendo:
            - device_name (str): Nome do equipamento
            - device_mgmt (str): Endereço IP de gerenciamento (IPv4 ou IPv6)
            - platform (str): Plataforma associada ao equipamento
    """


    try:
        # Monta a URL da requisição
        url = f"{str(NETBOX_URL)}api/dcim/devices/{device_id}/"
        
        # Requisição GET ao NetBox
        response = requests.get(url=url, headers=HEADERS, verify=False)
        response.raise_for_status()  # Lança exceção se HTTP status não for 200

        # Coleta os Dados em JSON
        json_data = response.json()
        
        # Nome do dispositivo
        device_name = json_data.get("name") 

        # IP de gerenciamento (verifica IPv4 ou IPv6)
        primary_ip4 = json_data.get("primary_ip4")
        primary_ip6 = json_data.get("primary_ip6")
        
        management_ip = None

        if primary_ip6 and "address" in primary_ip6:
            management_ip = primary_ip6["address"]
        elif primary_ip4 and "address" in primary_ip4:
            management_ip = primary_ip4["address"]
            
        if management_ip:
            # Remove a máscara de rede (ex.: transforma 192.168.100.100/32 em 192.168.100.100)
            management_ip = management_ip.split("/")[0]
            
        # Plataforma associada (ex.: IOS-XR, Arista EOS, etc.)
        platform = None
        if json_data.get("platform"):
            platform = json_data["platform"].get("name")

        return {
            "device_name": device_name,
            "device_mgmt": management_ip,
            "platform": platform,
        }

    except requests.exceptions.HTTPError as http_err:
        activity.logger.info(f"[ERROR] HTTP error occurred: {http_err}")
        raise
    except Exception as err:
        activity.logger.info(f"[ERROR] Other error occurred: {err}")
        raise