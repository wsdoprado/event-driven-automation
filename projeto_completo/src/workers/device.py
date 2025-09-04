import asyncio, os, logging
from temporalio.worker import Worker
from temporalio.client import Client

# Atividades externas que o worker pode executar
from activities.device.arista_ceos import get_config, change_hostname
from activities.remote.telegram import send_message

# Workflow associado a este worker
from workflows.device import DeviceWorkflow

# Configuração de logging: registra em arquivo e também no console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[
        logging.FileHandler(f"/var/log/projeto/worker-device.log"),
        logging.StreamHandler()
    ]
)

# Endereço do servidor Temporal (padrão: localhost:7233 se não definido)
TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "0.0.0.0:7233")

# Nome da fila de tarefas que este worker irá consumir
DEVICE_QUEUE = "DEVICE_QUEUE"

async def main():
    """
    Função principal que inicializa o worker do Temporal.
    
    - Conecta ao servidor Temporal.
    - Registra workflows e atividades relacionadas a dispositivos.
    - Inicia o loop de execução para processar tarefas da fila.
    """
    
    # Conexão com o servidor Temporal
    client = await Client.connect(TEMPORAL_ADDRESS)

    # Criação do worker responsável pelo processamento das tarefas
    worker = Worker(
        client,
        task_queue=DEVICE_QUEUE,         # Fila de execução
        workflows=[DeviceWorkflow],      # Workflow associado
        activities=[
            get_config,                  # Atividade: obter configuração do dispositivo
            change_hostname,             # Atividade: alterar hostname do dispositivo
            send_message                 # Atividade: enviar notificação (Telegram)
        ],
    )

    # Executa o worker e aguarda indefinidamente
    await worker.run()


if __name__ == "__main__":
    # Inicializa o loop assíncrono para rodar o worker
    asyncio.run(main())
