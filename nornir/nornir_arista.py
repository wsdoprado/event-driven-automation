from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_utils.plugins.functions import print_result
from nornir_netbox.plugins.inventory import NetBoxInventory2
from nornir.core.task import Result, Task
from nornir_netmiko.tasks import netmiko_send_command
from dotenv import load_dotenv
import urllib3
import os

# ----------------------------------------------
# Carregar variáveis de ambiente do arquivo .env
# ----------------------------------------------
load_dotenv()  # lê variáveis como NETBOX_URL, NETBOX_TOKEN, USER_DEVICE, PASSW_DEVICE

# ----------------------------------------------
# Desabilita avisos de segurança SSL/TLS
# (não recomendado em produção)
# ----------------------------------------------
urllib3.disable_warnings()

NETBOX_URL = os.getenv("NETBOX_URL")     # URL do NetBox
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN") # Token de API do NetBox
USER_DEVICE = os.getenv("USER_DEVICE")   # Usuário SSH para os dispositivos
PASSW_DEVICE = os.getenv("PASSW_DEVICE") # Senha SSH para os dispositivos

# ----------------------------------------------
# Task: coletar versão do equipamento via Netmiko
# ----------------------------------------------
def get_version_netmiko(task: Task) -> Result:
    """
    Executa 'show version' no dispositivo usando Netmiko.

    Args:
        task (Task): host do Nornir

    Returns:
        Result: Resultado da execução do comando
    """
    
    # Configurações de SSH do host
    device = task.host 
    device.port = 22
    device.username = USER_DEVICE
    device.password = PASSW_DEVICE
    
    try:    
        # Envia comando 'show version' via Netmiko
        response = task.run(
            task=netmiko_send_command,
            command_string="show version"
        )
        return Result(
            host=task.host,
            result=response.result,
            failed=False
        )
    except Exception as e:
        return Result(
            host=task.host,
            result=f"❌ Error: {str(e)}",
            failed=True
        )
    
# ----------------------------------------------
# Task: coletar facts do equipamento via NAPALM
# ----------------------------------------------
def get_facts(task: Task) -> Result:
    """
    Coleta informações de facts (vendor, modelo, OS, interfaces) usando NAPALM.

    Args:
        task (Task): host do Nornir

    Returns:
        Result: Resultado da execução
    """
    device = task.host 
    device.port = 22
    device.username = USER_DEVICE
    device.password = PASSW_DEVICE
    device.platform = "arista_eos"
    
    try:    
        # Coleta os facts usando NAPALM
        response = task.run(
            task=napalm_get,
            getters=["facts"],
            username=USER_DEVICE,
            password=PASSW_DEVICE,
            optional_args={"transport": "ssh"}  # garante SSH
        )
        return Result(
            host=task.host,
            result=response.result,
            failed=False
        )
    except Exception as e:
        return Result(
            host=task.host,
            result=f"❌ Error: {str(e)}",
            failed=True
        )
    
# ----------------------------------------------
# Função principal
# Inicializa Nornir e executa tasks
# ----------------------------------------------    
def main():
    # Inicializa Nornir com Runner Threaded e inventário via NetBox
    nr = InitNornir(
        runner={
            "plugin": "threaded", 
            "options": {"num_workers": 10}  # Número de threads paralelas
        },
        inventory={
            "plugin": "NetBoxInventory2",
            "options": {
                "nb_url": NETBOX_URL,
                "nb_token": NETBOX_TOKEN,
                "filter_parameters": {
                    "platform": "eos" # Filtra dispositivos Arista EOS
                },
                "ssl_verify": False,
            }
        }
    )

    # Executa a task get_version_netmiko para todos os dispositivos
    results = nr.run(task=get_facts)
    # Para usar NAPALM, substitua por: results = nr.run(task=get_facts)
    
    # Itera sobre os resultados e imprime
    for host, multi_result in results.items():
        print(f"\n=== {host} ({multi_result[0].host.platform}) ===")
        print(multi_result[0].result)

# ----------------------------------------------
# Entry point do script
# ----------------------------------------------
if __name__ == "__main__":
    main()