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
async def get_device_graphql(device_id: int) -> dict:    
    """
    Atividade do Temporal para buscar informações de um device no NetBox usando GraphQL.

    Args:
        device_id (int): ID do device no NetBox.

    Returns:
        dict: Informações extraídas do device:
            - device_name (str): Nome do dispositivo
            - device_mgmt (str): IP de gerenciamento (IPv4 ou IPv6)
            - platform (str): Plataforma associada
        None: Se a query GraphQL retornar erro.
    """
    try:
        # Monta filtro dinâmico com base no device_id
        filters = f"(id: {device_id})"
        
        # Query GraphQL completa para buscar devices + detalhes de interfaces
        GRAPHQL_QUERY = f"""
        query {{
        device{filters} {{
            id
            name
            primary_ip4 {{
                address
            }}
            primary_ip6 {{
                address
            }}
            platform {{
                name
            }}
        }}
        }}
        """

        # Endpoint GraphQL do NetBox
        url = f"{NETBOX_URL}/graphql/"

        # Monta o payload JSON com a query
        payload = {"query": GRAPHQL_QUERY}

        # Executa a requisição POST
        response = requests.post(url, headers=HEADERS, json=payload, verify=False)
        response.raise_for_status() # Levanta erro se status code != 200
        
        # Coleta os Dados em JSON
        json_data = response.json()
        
        #result = response.json()    # Converte a resposta em JSON
        
        # Verifica se houve erros retornados pelo GraphQL
        if "errors" in json_data:
            activity.logger.info(f"[ERROR] Erros na query GraphQL: {json_data["errors"]}")
            return None
        
        
        device_name = json_data["data"]["device"].get("name") 

        # IP de gerenciamento (verifica IPv4 ou IPv6)
        primary_ip4 = json_data["data"]["device"].get("primary_ip4")
        primary_ip6 = json_data["data"]["device"].get("primary_ip6")
        
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