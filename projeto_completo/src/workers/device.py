import asyncio, os, logging
from temporalio.worker import Worker
from temporalio.client import Client

from activities.device.arista_ceos import get_config, change_hostname
from activities.remote.telegram import send_message
from workflows.device import DeviceWorkflow

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[
        logging.FileHandler(f"/var/log/projeto/worker-device.log"),
        logging.StreamHandler()
    ]
)

TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "0.0.0.0:7233")

DEVICE_QUEUE = "DEVICE_QUEUE"

async def main():
    client = await Client.connect(TEMPORAL_ADDRESS)

    worker = Worker(
        client,
        task_queue=DEVICE_QUEUE,
        workflows=[DeviceWorkflow],
        activities=[
            get_config,
            change_hostname,
            send_message
        ],
        #max_concurrent_workflow_tasks=1,    
        #max_concurrent_activities=1,
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
