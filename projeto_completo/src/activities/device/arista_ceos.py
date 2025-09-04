from temporalio import activity
from napalm import get_network_driver
from ncclient import manager
import os, logging
import pyeapi

# Variáveis de ambiente para acessar Device
USER_DEVICE = os.getenv("USER_DEVICE")
PASSW_DEVICE = os.getenv("PASSW_DEVICE")

@activity.defn
async def get_config(device: dict) -> dict:
    """
    Obtém informações de configuração do dispositivo usando NAPALM.

    Args:
        device (dict): Dicionário com dados do device (inclui 'device_mgmt').

    Returns:
        dict: Estrutura com:
            - data: facts e interfaces do equipamento
            - status: True se sucesso, False caso contrário
    """
    results = {"data": None, "status": False}

    try:
        # Define o driver EOS (Arista) para conexão
        driver = get_network_driver("eos")

        device_mgmt = device["device_mgmt"]
        username = USER_DEVICE
        password = PASSW_DEVICE

        # Conexão via NAPALM
        conn = driver(device_mgmt, username, password)
        conn.open()

        # Coleta informações gerais (facts) e interfaces
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
async def change_hostname_pyeapi(device: dict, newhostname: str) -> dict:
    """
    Altera o hostname de um device Arista via API (pyeapi).

    Args:
        device (dict): Dicionário com dados do device (inclui 'device_mgmt').
        newhostname (str): Novo hostname a ser configurado.

    Returns:
        dict: Estrutura com:
            - data: None
            - status: True se sucesso, False caso contrário
    """
    results = {"data": None, "status": False}

    try:
        # Conexão com o equipamento via eAPI
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
async def change_hostname_netconf(device: dict, newhostname: str) -> dict:
    """
    Altera o hostname de um device Arista via NETCONF.

    Args:
        device (dict): Dicionário com dados do device (inclui 'device_mgmt').
        newhostname (str): Novo hostname a ser configurado.

    Returns:
        dict: Estrutura com:
            - data: None
            - status: True se sucesso, False caso contrário
    """
    results = {"data": None, "status": False}

    try:
        DEVICE = {
            "host": device["device_mgmt"],
            "port": 830,
            "username": USER_DEVICE,
            "password": PASSW_DEVICE,
            "hostkey_verify": False,
        }

        config_payload = f"""
        <config>
            <system xmlns="http://openconfig.net/yang/system">
                <config>
                <hostname>{newhostname}</hostname>
                </config>
            </system>
        </config>
        """

        with manager.connect(**DEVICE) as m:
            m.edit_config(target="running", config=config_payload)
            print(f"Hostname alterado para {newhostname}")


        results = {"data": None, "status": True}
    
    except Exception as e:
        activity.logger.error(f"Erro ao trocar hostname {device}: {e}")
        raise Exception(f"Erro ao pegar config de {device}: {e}")

    return results     
    
@activity.defn
async def apply_interface_config(device: dict, iface: str, diff: dict) -> dict:
    """
    Aplica mudanças de configuração em uma interface de um device Arista.

    Args:
        device (dict): Dicionário com dados do device (inclui 'device_mgmt').
        iface (str): Nome da interface a ser alterada.
        diff (dict): Estrutura contendo diferenças (NetBox vs. Device).
            Exemplo:
            {
                "description": {"nbx": "uplink-to-core"},
                "mtu": {"nbx": 9000},
                "enabled": {"nbx": True}
            }

    Returns:
        dict: Estrutura com:
            - data: None
            - status: True se sucesso, False caso contrário
    """
    results = {"data": None, "status": False}

    try:
        # Conexão com o equipamento via eAPI
        conn = pyeapi.connect(
            transport="https",
            host=device["device_mgmt"],
            username=USER_DEVICE,
            password=PASSW_DEVICE
        )
        # Cria o Node para interagir com o EOS
        node = pyeapi.client.Node(conn)
        
        config_cmds = []
        
        # Diferença em description
        if "description" in diff:
            desc = diff["description"]["nbx"]
            config_cmds.append(f"interface {iface}")
            if desc != '':
                config_cmds.append(f"description {desc}")
            else:
                config_cmds.append(f"no description")
        
        # Diferença em MTU
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
        
        # Diferença em estado (enabled/disabled)
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
        
        # Se houver comandos, aplica na interface            
        if config_cmds:
            # Entra no modo de configuração e muda o hostname
            node.config(config_cmds)

            results = {"data": None, "status": True}
        
            activity.logger.info(f"config_cmds {config_cmds}")        

    except Exception as e:
        activity.logger.error(f"Erro ao apply_interface_config de {device}: {e}")
        raise Exception(f"Erro ao apply_interface_config de {device}: {e}")

    return results