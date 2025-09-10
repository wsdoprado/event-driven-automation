from datetime import timedelta
from temporalio import workflow


from activities.operations import generate_value_a, generate_value_b, result_sum


@workflow.defn
class MakeSumOperationWorkflow:
    @workflow.run
    async def run(self) -> int:
        workflow.logger.info("Running workflow MakeSumOperationWorkflow")

        value_a = await workflow.execute_activity(
            generate_value_a,
            start_to_close_timeout=timedelta(seconds=10),
        )

        value_b = await workflow.execute_activity(
            generate_value_b,
            start_to_close_timeout=timedelta(seconds=10),
        )

        result = await workflow.execute_activity(
            result_sum,
            args=(value_a, value_b),
            start_to_close_timeout=timedelta(seconds=10),
        )

        return result



