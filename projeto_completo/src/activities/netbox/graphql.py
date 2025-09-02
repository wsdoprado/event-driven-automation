from temporalio import activity
from dotenv import load_dotenv
import os, json, logging, requests, urllib3

load_dotenv()
urllib3.disable_warnings()

NETBOX_URL = os.getenv("NETBOX_URL")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")

HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': 'Token '+str(NETBOX_TOKEN)
}

@activity.defn
async def get_device_graphql(device_id: int) -> dict:    
    try:
        # Monta o filtro dinamicamente caso device_id seja fornecido
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
        result = response.json()    # Converte a resposta em JSON
        
        
        # Verifica se houve erros retornados pelo GraphQL
        if "errors" in result:
            activity.logger.info(f"[ERROR] Erros na query GraphQL: {result["errors"]}")
            return None
        
        #activity.logger.info(f"[INFO] GraphQL: {result["data"]}")
        
        device_name = result["data"]["device"].get("name") 

        # IP de gerenciamento (verifica IPv4 ou IPv6)
        primary_ip4 = result["data"]["device"].get("primary_ip4")
        primary_ip6 = result["data"]["device"].get("primary_ip6")
        
        management_ip = None
        if primary_ip4 and "address" in primary_ip4:
            management_ip = primary_ip4["address"]
        elif primary_ip6 and "address" in primary_ip6:
            management_ip = primary_ip6["address"]
        management_ip = str(management_ip).split("/")[0]
        
        platform = result["data"]["device"].get("platform").get("name")
        return {"device_name": device_name, "device_mgmt": management_ip, "platform": platform}
    
        #return result["data"] # Retorna apenas o bloco 'data'
    
    except requests.exceptions.HTTPError as http_err:
        activity.logger.info(f"[ERROR] HTTP error occurred: {http_err}")
        raise
    except Exception as err:
        activity.logger.info(f"[ERROR] Other error occurred: {err}")
        raise