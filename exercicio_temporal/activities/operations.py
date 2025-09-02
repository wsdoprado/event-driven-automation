from temporalio import activity
from random import randint


@activity.defn
async def generate_value_a() -> int:
    value_a = randint(0, 10)
    activity.logger.info(f"Running activity generate_value_a with value: {value_a}")

    return value_a


@activity.defn
async def generate_value_b() -> int:
    value_b = randint(10, 20)
    activity.logger.info(f"Running activity generate_value_b with value: {value_b}")

    return value_b


@activity.defn
async def result_sum(value_a: int, value_b: int) -> int:
    result = value_a + value_b
    activity.logger.info(f"Running activity result_sum with result: {result}")

    return result