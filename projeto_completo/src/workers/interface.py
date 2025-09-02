import asyncio, os, logging
from temporalio.worker import Worker
from temporalio.client import Client

from activities.device.arista_ceos import get_config, change_hostname, apply_interface_config
from activities.netbox.restapi import get_device_restapi
from activities.netbox.graphql import get_device_graphql
from workflows.interface import InterfaceWorkflow

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[
        logging.FileHandler(f"/var/log/projeto/worker-interface.log"),
        logging.StreamHandler()
    ]
)

TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "0.0.0.0:7233")

INTERFACE_QUEUE = "INTERFACE_QUEUE"

async def main():
    client = await Client.connect(TEMPORAL_ADDRESS)

    worker = Worker(
        client,
        task_queue=INTERFACE_QUEUE,
        workflows=[InterfaceWorkflow],
        activities=[
            get_config,
            change_hostname,
            apply_interface_config,
            get_device_restapi,
            get_device_graphql
        ],
        #max_concurrent_workflow_tasks=1,    
        #max_concurrent_activities=1,
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
