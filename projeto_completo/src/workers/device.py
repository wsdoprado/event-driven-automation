import asyncio, os, logging
from temporalio.worker import Worker
from temporalio.client import Client


#from activities.operations import get_config, change_hostname
from activities.device.arista_ceos import get_config, change_hostname
from workflows.device import DeviceWorkflow

import logging
logging.basicConfig(level=logging.INFO)

TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "0.0.0.0:7233")

async def main():
    client = await Client.connect(TEMPORAL_ADDRESS)

    worker = Worker(
        client,
        task_queue="worker-queue",
        workflows=[DeviceWorkflow],
        activities=[
            get_config,
            change_hostname
        ],
        max_concurrent_workflow_tasks=1,    # Apenas 1 workflow task por vez
        max_concurrent_activities=1,
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
