from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError

# Importação especial para permitir chamadas a módulos externos dentro do workflow do Temporal
with workflow.unsafe.imports_passed_through():
    from activities.device.arista_ceos import get_config, change_hostname, apply_interface_config
    from activities.netbox.restapi import get_device_restapi
    from activities.netbox.graphql import get_device_graphql
    from activities.remote.telegram import send_message
    from utils import InterfaceData
    
# Constantes de timeout (em segundos)
TIMEOUT_ACTIVITY = 120  # Tempo limite para atividades genéricas
TIMEOUT_NETBOX = 120    # Tempo limite específico para operações no NetBox
TIMEOUT_DEVICE = 360    # Tempo limite para operações em dispositivos de rede

# Política padrão de retry para atividades no Temporal
RETRY_POLICY_DEFAULT = RetryPolicy(
    initial_interval=timedelta(seconds=10),     # Espera antes da primeira tentativa de retry
    backoff_coefficient=2.0,                    # Fator de multiplicação para o backoff exponencial (10s, 20s, 40s, etc.)
    maximum_interval=timedelta(seconds=120),    # Intervalo máximo entre tentativas
    maximum_attempts=50                         # Número máximo de tentativas (inclui a primeira execução)
)

# Função auxiliar para enviar mensagens via Telegram (atividade assíncrona no Temporal)
async def send_message_telegram(text: str) -> None:
    try:
        await workflow.execute_activity(
            send_message,                      # Atividade que realmente envia a mensagem
            text,                              # Texto da mensagem
            schedule_to_close_timeout=timedelta(seconds=TIMEOUT_ACTIVITY), # Timeout da execução
        )
    except Exception as e:
        # Caso falhe, levanta um erro que pode ser tratado pelo workflow
        raise ApplicationError(f"Falha ao enviar mensagem para o Telegram: {e}")

# Função auxiliar para encontrar as diferencas entre Netbox e Device
def compare_iface(nbx_iface: dict, dev_iface: dict) -> dict:
    diffs = {}
    if nbx_iface.get("iface_description") != dev_iface.get("iface_description"):
        diffs["description"] = {
            "nbx": nbx_iface.get("iface_description"),
            "device": dev_iface.get("iface_description")
        }

    if nbx_iface.get("iface_mtu") != dev_iface.get("iface_mtu"):
        diffs["mtu"] = {
            "nbx": nbx_iface.get("iface_mtu"),
            "device": dev_iface.get("iface_mtu")
        }

    if nbx_iface.get("iface_enabled") != dev_iface.get("iface_enabled"):
        diffs["enabled"] = {
            "nbx": nbx_iface.get("iface_enabled"),
            "device": dev_iface.get("iface_enabled")
        }

    return diffs

# Definição do workflow principal
@workflow.defn
class InterfaceWorkflow:
    @workflow.run
    async def run(self, data: InterfaceData) -> dict:
        
        # Salva o LOG no arquivo de logs
        workflow.logger.info(f"[INFO] Webhook received: {data}")
        
        #Envia Mensagem para o Telegram
        await send_message_telegram(f"Webhook received: {data}")
        
        # Extrai dados principais do webhook
        iface_name_nbx = data.name
        iface_description_nbx = data.description
        iface_mtu_nbx = data.mtu
        iface_enabled_nbx = data.enabled
        iface_device_id = data.device.id
        iface_device_name = data.device.name
        
        # Estrutura da interface no NetBox
        iface_nbx = {
            "iface_name": iface_name_nbx,
            "iface_description": iface_description_nbx,
            "iface_mtu": iface_mtu_nbx,
            "iface_enabled": iface_enabled_nbx,  
        }

        # Salva o LOG no arquivo de logs
        workflow.logger.info(f"[INFO] Coletando dados do device {iface_device_name} - NETBOX REST API")
        
        #Envia Mensagem para o Telegram
        await send_message_telegram(f"Coletando dados do device {iface_device_name} - NETBOX REST API")
        
        # Executa a atividade que coleta informacoes do device no netbox usando REST API
        results_device_nbx = await workflow.execute_activity(
            get_device_restapi,
            args=[iface_device_id],
            schedule_to_close_timeout=timedelta(seconds=TIMEOUT_DEVICE),
            retry_policy=RETRY_POLICY_DEFAULT,  
        )
        
        # Se o equipamento for da plataforma Arista EOS
        if results_device_nbx["platform"] == "eos":
            
            # Salva o LOG no arquivo de logs
            workflow.logger.info(f"[INFO] Coletando dados do host {results_device_nbx["device_name"]} - IP: {results_device_nbx["device_mgmt"]} - NAPALM")
            
            #Envia Mensagem para o Telegram
            await send_message_telegram(f"Coletando dados do host {results_device_nbx["device_name"]} - IP: {results_device_nbx["device_mgmt"]} - NAPALM")

            # Executa a atividade que coleta a configuração atual do device
            device_results = await workflow.execute_activity(
                    get_config,
                    args=[results_device_nbx],
                    schedule_to_close_timeout=timedelta(seconds=TIMEOUT_DEVICE),
                    retry_policy=RETRY_POLICY_DEFAULT,  
            )

            # Coleta o hostname retornado pelo device
            device_name = device_results['data']['facts']['hostname']
            
            # Caso o hostname do device seja igual ao registrado no NetBox
            if device_name == iface_device_name:
                # Caso a Interface do Netbox exista no Device
                if iface_name_nbx in device_results['data']['interfaces']:
                    
                    # Estrutura da Interface do Device - NAPALM 
                    iface_napalm = {
                        "iface_name": iface_name_nbx,
                        "iface_description": device_results['data']['interfaces'][iface_name_nbx]['description'],
                        "iface_mtu": device_results['data']['interfaces'][iface_name_nbx]['mtu'],
                        "iface_enabled": device_results['data']['interfaces'][iface_name_nbx]['is_enabled'],
                    }
            
                    # Compara interface NetBox x Device usando funcao auxiliar compare_iface
                    diff = compare_iface(iface_nbx, iface_napalm)

                    # Se, existir diferenca
                    if diff:
                        # Salva o LOG no arquivo de logs
                        workflow.logger.info(f"[INFO] Diferenças na interface {iface_nbx['iface_name']}: {diff}")
                        
                        #Envia Mensagem para o Telegram
                        await send_message_telegram(f"Diferenças na interface {iface_nbx['iface_name']}: {diff}")

                        # Salva o LOG no arquivo de logs
                        workflow.logger.info(f"[INFO] Iniciando troca de parametros no host: {results_device_nbx["device_name"]} e Interface: {iface_nbx['iface_name']}")
                        
                        #Envia Mensagem para o Telegram
                        await send_message_telegram(f"Iniciando troca de parametros no host: {results_device_nbx["device_name"]} e Interface: {iface_nbx['iface_name']}")
            
                        # Executa a atividade que altera a configuração atual do device
                        device_config_results = await workflow.execute_activity(
                                apply_interface_config,
                                args=[results_device_nbx,iface_nbx['iface_name'],diff],
                                schedule_to_close_timeout=timedelta(seconds=TIMEOUT_DEVICE),
                                retry_policy=RETRY_POLICY_DEFAULT,  
                        )
                        
                        # Se a atividade funcionou 
                        if device_config_results["status"] == True:
                            
                            # Salva o LOG no arquivo de logs
                            workflow.logger.info(f"[INFO] Troca de parametros na Interface finalizada.")  
                            
                            #Envia Mensagem para o Telegram
                            await send_message_telegram(f"Troca de parametros na Interface finalizada.")
                            
                        # Se a atividade nao funcionou 
                        else:
                            # Salva o LOG no arquivo de logs
                            workflow.logger.info(f"[INFO] Troca de parametros na Interface nao realizada. Verifique.")  
                            
                            #Envia Mensagem para o Telegram
                            await send_message_telegram(f"Troca de parametros na Interface nao realizada. Verifique.")
                            
                    # SE nao existir diferenca nas interfaces        
                    else:
                        # Salva o LOG no arquivo de logs
                        workflow.logger.info(f"[INFO] Nada a fazer. Interface {iface_nbx['iface_name']} consistente")    
                        
                        #Envia Mensagem para o Telegram
                        await send_message_telegram(f"Nada a fazer. Interface {iface_nbx['iface_name']} consistente")

        return {"status": True}

