from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError

# Importação especial para permitir chamadas a módulos externos dentro do workflow do Temporal
with workflow.unsafe.imports_passed_through():
    from activities.device.arista_ceos import get_config, change_hostname_pyeapi, change_hostname_netconf
    from activities.remote.telegram import send_message
    from utils import DeviceData, TIMEOUT_ACTIVITY, TIMEOUT_DEVICE

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
            start_to_close_timeout=timedelta(seconds=TIMEOUT_ACTIVITY), # Timeout da execução
        )
    except Exception as e:
        # Caso falhe, levanta um erro que pode ser tratado pelo workflow
        raise ApplicationError(f"Falha ao enviar mensagem para o Telegram: {e}")

# Definição do workflow principal
@workflow.defn
class DeviceWorkflow:
    @workflow.run
    async def run(self, data: DeviceData) -> dict:
        # Salva o LOG no arquivo de logs
        workflow.logger.info(f"[INFO] Webhook received: {data}")
        
        #Envia Mensagem para o Telegram
        await send_message_telegram(f"Webhook received: {data}")
        
        # Extrai informações principais do device enviadas pelo webhook
        device_name_nbx = data.name
        device_platform = data.platform.name
        device_mgmt = data.primary_ip6.address
        device_mgmt = device_mgmt.split("/")[0]
        
        # Estrutura com os dados do device
        device = {
            "device_name": device_name_nbx, 
            "device_platform": device_platform, 
            "device_mgmt": device_mgmt
        }
        
        # Se o equipamento for da plataforma Arista EOS
        if device_platform == "eos":
            
            # Salva o LOG no arquivo de logs
            workflow.logger.info(f"[INFO] Coletando configuracoes do host: {device["device_name"]} - IP: {device["device_mgmt"]}")
            
            #Envia Mensagem para o Telegram
            await send_message_telegram(f"Coletando configuracoes do host: {device["device_name"]} - IP: {device["device_mgmt"]}")
            
            # Executa a atividade que coleta a configuração atual do device
            device_results = await workflow.execute_activity(
                    get_config,
                    args=[device],
                    start_to_close_timeout=timedelta(seconds=TIMEOUT_DEVICE),
                    retry_policy=RETRY_POLICY_DEFAULT,  
            )
            
            # Coleta o hostname retornado pelo device
            device_name = device_results['data']['facts']['hostname']
            
            # Caso o hostname do device seja diferente do registrado no NetBox
            if device_name != device_name_nbx:
                # Salva o LOG no arquivo de logs
                workflow.logger.info(f"[INFO] Iniciando troca de hostname de: {device_name} para {device_name_nbx}")  
                
                #Envia Mensagem para o Telegram
                await send_message_telegram(f"Iniciando troca de hostname de: {device_name} para {device_name_nbx}")
                
                # Executa a atividade de troca de hostname
                results_change_hostname = await workflow.execute_activity(
                    #change_hostname_pyeapi,
                    change_hostname_netconf,
                    args=[device,device_name_nbx],
                    start_to_close_timeout=timedelta(seconds=TIMEOUT_DEVICE),
                    retry_policy=RETRY_POLICY_DEFAULT,  
                )
                
                # Executa a atividade de troca de hostname
                if results_change_hostname["status"] == True:
                    # Salva o LOG no arquivo de logs
                    workflow.logger.info(f"[INFO] Troca de hostname finalizada.")  
                    
                    #Envia Mensagem para o Telegram
                    await send_message_telegram(f"Troca de hostname finalizada.")
                else:
                    # Salva o LOG no arquivo de logs
                    workflow.logger.info(f"[INFO] Troca de hostname nao realizada. Verifique.")  
                    
                    #Envia Mensagem para o Telegram
                    await send_message_telegram(f"Troca de hostname nao realizada. Verifique.")
            
            # Caso o hostname já esteja correto, nada é feito    
            else:
                # Salva o LOG no arquivo de logs
                workflow.logger.info(f"[INFO] Nada a fazer. hostname iguais: device: {device_name} netbox: {device_name_nbx}")    
                
                #Envia Mensagem para o Telegram
                await send_message_telegram(f"Nada a fazer. hostname iguais: device: {device_name} netbox: {device_name_nbx}")
                
        # Retorna os dados do dispositivo processado
        return {"status": True}

