from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy
#from activities.operations import get_config, change_hostname
from activities.device.arista_ceos import get_config, change_hostname

# Constants Timeout
TIMEOUT_ACTIVITY = 120
TIMEOUT_NETBOX = 120
TIMEOUT_DEVICE = 360

# Default retry policy for Temporal activities
RETRY_POLICY_DEFAULT = RetryPolicy(
    initial_interval=timedelta(seconds=10),     # Time to wait before the first retry attempt
    backoff_coefficient=2.0,                    # Multiplier for exponential backoff (e.g., 10s, 20s, 40s, etc.)
    maximum_interval=timedelta(seconds=120),    # Maximum wait time between retries
    maximum_attempts=50                         # Total number of attempts including the first try
)

@workflow.defn
class DeviceWorkflow:
    @workflow.run
    async def run(self, webhook: dict) -> dict:
        data = webhook
        #workflow.logger.info(f"data: {data}")
        device_name_nbx = data['name']
        device_platform = data['platform']['name']
        device_mgmt = data['primary_ip4']['address']
        device_mgmt = device_mgmt.split("/")[0]
        device = {"device_name": device_name_nbx, "device_platform": device_platform, "device_mgmt": device_mgmt}
        workflow.logger.info(f"device no workflow: {device}")
        if device_platform == "eos":
            device_results = await workflow.execute_activity(
                    get_config,
                    args=[device],
                    schedule_to_close_timeout=timedelta(seconds=TIMEOUT_DEVICE),
                    retry_policy=RETRY_POLICY_DEFAULT,  
            )
            
            ##Validando hostname
            device_name = device_results['data']['facts']['hostname']
            
            if device_name != device_name_nbx:
                workflow.logger.info(f"hostname diferente: device: {device_name} netbox:{device_name_nbx}")
                results_change_hostname = await workflow.execute_activity(
                    change_hostname,
                    args=[device,device_name_nbx],
                    schedule_to_close_timeout=timedelta(seconds=TIMEOUT_DEVICE),
                    retry_policy=RETRY_POLICY_DEFAULT,  
                )
                workflow.logger.info(f"troca de hostname: {results_change_hostname}")   
            else:
                workflow.logger.info(f"hostaname iguais: device: {device_name} netbox:{device_name_nbx}")    
            #workflow.logger.info(f"result: {results}")
        return device

