from temporalio import activity
import os, json, logging


# Carrega variáveis de ambiente
USER_DEVICE = os.getenv("USER_DEVICE")
PASSW_DEVICE = os.getenv("PASSW_DEVICE")

@activity.defn
async def get_config(device: dict) -> dict:
    results = {"data": None, "status": False}
    activity.logger.warning(f"activity - get config: {device}")

    try:
        from napalm import get_network_driver
        driver = get_network_driver("eos")

        device_mgmt = device["device_mgmt"]
        username = USER_DEVICE
        password = PASSW_DEVICE

        activity.logger.info(f"Conectando em {device_mgmt} com user {username}")

        conn = driver(device_mgmt, username, password)
        conn.open()

        facts = conn.get_facts()
        interfaces = conn.get_interfaces()

        conn.close()

        results["data"] = {"facts": facts, "interfaces": interfaces}
        results["status"] = True

    except Exception as e:
        activity.logger.error(f"Erro ao pegar config de {device}: {e}")
        raise Exception(f"Erro ao pegar config de {device}: {e}")

    return results

@activity.defn
async def change_hostname(device: dict, newhostname: str) -> dict:
    results = {"data": None, "status": False}
    activity.logger.warning(f"activity - change_hostname : {newhostname}")

    try:
        import pyeapi
        conn = pyeapi.connect(
            transport="https",
            host=device["device_mgmt"],
            username=USER_DEVICE,
            password=PASSW_DEVICE
        )
        # Cria o Node para interagir com o EOS
        node = pyeapi.client.Node(conn)

        # Entra no modo de configuração e muda o hostname
        node.config([f"hostname {newhostname}"])

        results = {"data": None, "status": True}
    
    except Exception as e:
        activity.logger.error(f"Erro ao trocar hostname {device}: {e}")
        raise Exception(f"Erro ao pegar config de {device}: {e}")

    return results
     
    
