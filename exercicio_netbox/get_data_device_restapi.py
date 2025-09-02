import os, requests, urllib3
from dotenv import load_dotenv

"""
Código	                          Tipo	        Descrição
200     OK	                    Sucesso	    Requisição realizada corretamente.
201     Created	                Sucesso	    Recurso criado com sucesso (POST).
204     No Content	            Sucesso	    Requisição bem-sucedida, mas sem conteúdo.
400     Bad Request	            Cliente	    Requisição mal-formada (ex.: parâmetros inválidos).
401     Unauthorized	        Cliente	    Token ou credenciais ausentes ou inválidas.
403     Forbidden	            Cliente	    Usuário não tem permissão para acessar o recurso.
404     Not Found	            Cliente	    Recurso não encontrado.
405     Method Not Allowed	    Cliente	    Método HTTP não permitido para o endpoint.
409     Conflict	            Cliente	    Conflito de dados (ex.: criar recurso que já existe).
422     Unprocessable Entity	Cliente	    Dados enviados são inválidos ou incompletos.
500     Internal Server Error	Servidor	Erro interno da API.
502     Bad Gateway	            Servidor	API fora do ar ou indisponível 
503     Service Unavailable     Servidor    API fora do ar ou indisponível
"""


# Desabilita avisos de segurança SSL/TLS (não recomendado em produção)
urllib3.disable_warnings() #não mostra warnings de segurança relacionados a SSL/TLS

# URL do NetBox (ex.: http://localhost:8000)
NETBOX_URL=https://192.168.246.25/

# Token de API do NetBox
NETBOX_TOKEN="3e99f8519cf5467ee3f7b76c661240a317b4fd40"

# Headers padrão para requisições GraphQL/REST API
HEADERS = {
    "Authorization": f"Token {NETBOX_TOKEN}", # Autenticação via token
    "Content-Type": "application/json"        # Informar que o payload é JSON
}

# ----------------------------------------------
# Função para consultar devices via REST API
# ----------------------------------------------
def get_devices(params=None):
    """
    params: dict opcional para filtros, ex: {"site": "pop-sp", "role": "spine"}
    """
    url = f"{NETBOX_URL}/api/dcim/devices/"

    try:
        response = requests.get(url, headers=HEADERS, params=params, verify=False)
        
        #print(f"Status code: {response.status_code}")  
        #print(f"Headers: {response.headers}")  
        #print(f"Text String: {response.text}")  # retorna a resposta como string
        #print(type(response.text))
        data = response.json()  # converte o corpo da resposta em dict/list
        #print(data['results'])
        #print(type(data))
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao consumir API: {e}")
    return data['results']

# ----------------------------------------------
# Execução principal do script
# ----------------------------------------------
if __name__ == "__main__":
    devices = get_devices()
    #devices = get_devices(params={"site": "sp-site", "role": "pe"})
    #print(f"Total de devices encontrados: {len(devices)}\n")
    #print(type(devices))
    for device in devices:
        if device.get('primary_ip'):
            ip_address = device['primary_ip']['address']
            ip_address = ip_address.split("/")[0]  # pega só o IP sem máscara
        else:
            ip_address = "N/A"
     
        print(f"{device['name']} - Site: {device['site']['name']} - Role: {device['role']['name']} - Tenant: {device['tenant']['name']} - MGMT: {ip_address} - Platform: {device['platform']['name']}")