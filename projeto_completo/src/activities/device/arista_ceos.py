from temporalio import activity
from napalm import get_network_driver
import os, json, logging
import pyeapi

# Carrega variáveis de ambiente
USER_DEVICE = os.getenv("USER_DEVICE")
PASSW_DEVICE = os.getenv("PASSW_DEVICE")

@activity.defn
async def get_config(device: dict) -> dict:
    results = {"data": None, "status": False}
    activity.logger.warning(f"activity - get config: {device}")

    try:
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
     
    
@activity.defn
async def apply_interface_config(device: dict, iface: str, diff: dict) -> dict:
    results = {"data": None, "status": False}
    activity.logger.warning(f"activity - get config: {device}")

    try:
        conn = pyeapi.connect(
            transport="https",
            host=device["device_mgmt"],
            username=USER_DEVICE,
            password=PASSW_DEVICE
        )
        # Cria o Node para interagir com o EOS
        node = pyeapi.client.Node(conn)
        
        activity.logger.info(f"Conectando em {device["device_mgmt"]} com user {USER_DEVICE}")

        config_cmds = []
        
        # só gera os comandos se houver diffs
        if "description" in diff:
            desc = diff["description"]["nbx"]
            config_cmds.append(f"interface {iface}")
            if desc != '':
                config_cmds.append(f"description {desc}")
            else:
                config_cmds.append(f"no description")
        
        if "mtu" in diff:
            if iface != "Management0":
                mtu = diff["mtu"]["nbx"]
                config_cmds.append(f"interface {iface}")
                if mtu == None or int(mtu) < 1500:
                    config_cmds.append(f"mtu 1500")
                else:
                    config_cmds.append(f"mtu {mtu}")
            else:
                activity.logger.info(f"[INFO] nao tem validacao para porta de gerencia {iface}") 
                
        if "enabled" in diff:
            if iface != "Management0":
                status = diff["enabled"]["nbx"]
                config_cmds.append(f"interface {iface}")
                if status:
                    config_cmds.append("no shutdown")
                else:
                    config_cmds.append("shutdown")
            else:
                activity.logger.info(f"[INFO] nao tem validacao para porta de gerencia {iface}")     
                  
        if config_cmds:
                    # Entra no modo de configuração e muda o hostname
            node.config(config_cmds)

            results = {"data": None, "status": True}
        
            activity.logger.info(f"config_cmds {config_cmds}")        

        #conn.close()

        #results["data"] = {"facts": facts, "interfaces": interfaces}
        #results["status"] = True

    except Exception as e:
        activity.logger.error(f"Erro ao apply_interface_config de {device}: {e}")
        raise Exception(f"Erro ao apply_interface_config de {device}: {e}")

    return results