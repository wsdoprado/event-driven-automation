import asyncio
from temporalio.client import Client
from workflows.workflow import MakeSumOperationWorkflow


async def main():
    client = await Client.connect("localhost:7233")

    result = await client.execute_workflow(
        MakeSumOperationWorkflow.run,
        id="operation-workflow-id",
        task_queue="worker-queue",
    )

    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
