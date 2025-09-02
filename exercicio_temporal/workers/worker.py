import asyncio
from temporalio.worker import Worker
from temporalio.client import Client


from activities.operations import generate_value_a, generate_value_b, result_sum
from workflows.workflow import MakeSumOperationWorkflow

import logging
logging.basicConfig(level=logging.INFO)


async def main():
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="worker-queue",
        workflows=[MakeSumOperationWorkflow],
        activities=[
            generate_value_a,
            generate_value_b,
            result_sum
        ],
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
