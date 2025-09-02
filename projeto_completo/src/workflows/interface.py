from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities.device.arista_ceos import get_config, change_hostname, apply_interface_config
    from activities.netbox.restapi import get_device_restapi
    from activities.netbox.graphql import get_device_graphql
    
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

def compare_iface(nbx_iface: dict, dev_iface: dict) -> dict:
    diffs = {}
    if nbx_iface.get("iface_description") != dev_iface.get("iface_description"):
        diffs["description"] = {
            "nbx": nbx_iface.get("iface_description"),
            "device": dev_iface.get("iface_description")
        }

    if nbx_iface.get("iface_mtu") != dev_iface.get("iface_mtu"):
        diffs["mtu"] = {
            "nbx": nbx_iface.get("iface_mtu"),
            "device": dev_iface.get("iface_mtu")
        }

    if nbx_iface.get("iface_enabled") != dev_iface.get("iface_enabled"):
        diffs["enabled"] = {
            "nbx": nbx_iface.get("iface_enabled"),
            "device": dev_iface.get("iface_enabled")
        }

    return diffs

@workflow.defn
class InterfaceWorkflow:
    @workflow.run
    async def run(self, webhook: dict) -> dict:
        data = webhook
        #workflow.logger.info(f"data interface: {data}")
        iface_name_nbx = data['name']
        iface_description_nbx = data['description']
        iface_mtu_nbx = data['mtu']
        iface_enabled_nbx = data['enabled']
        iface_device_id = data['device']['id']
        iface_device_name = data['device']['name']
        
        # Estrutura NetBox
        iface_nbx = {
            "iface_name": iface_name_nbx,
            "iface_description": iface_description_nbx,
            "iface_mtu": iface_mtu_nbx,
            "iface_enabled": iface_enabled_nbx,  
        }

        workflow.logger.info(f"interface no workflow: {iface_nbx}")
        
        results_device_nbx = await workflow.execute_activity(
            get_device_restapi,
            args=[iface_device_id],
            schedule_to_close_timeout=timedelta(seconds=TIMEOUT_DEVICE),
            retry_policy=RETRY_POLICY_DEFAULT,  
        )
        workflow.logger.info(f"device nbx rest: {results_device_nbx}")   
        
        if results_device_nbx["platform"] == "eos":
            
            device_results = await workflow.execute_activity(
                    get_config,
                    args=[results_device_nbx],
                    schedule_to_close_timeout=timedelta(seconds=TIMEOUT_DEVICE),
                    retry_policy=RETRY_POLICY_DEFAULT,  
            )
            workflow.logger.info(f"get_config: {device_results}")  
            
            device_name = device_results['data']['facts']['hostname']
            
            if device_name == iface_device_name:
                if device_results['data']['interfaces'][iface_name_nbx]:
                    
                    # Estrutura NAPALM - Device
                    iface_napalm = {
                        "iface_name": iface_name_nbx,
                        "iface_description": device_results['data']['interfaces'][iface_name_nbx]['description'],
                        "iface_mtu": device_results['data']['interfaces'][iface_name_nbx]['mtu'],
                        "iface_enabled": device_results['data']['interfaces'][iface_name_nbx]['is_enabled'],
                    }
                    workflow.logger.info(f"interface nbx: {iface_nbx}")
                    workflow.logger.info(f"interface device: {iface_napalm}")      
                    
                    diff = compare_iface(iface_nbx, iface_napalm)

                    if diff:
                        workflow.logger.info(f"Diferenças na interface {iface_nbx['iface_name']}: {diff}")
                        device_config_results = await workflow.execute_activity(
                                apply_interface_config,
                                args=[results_device_nbx,iface_nbx['iface_name'],diff],
                                schedule_to_close_timeout=timedelta(seconds=TIMEOUT_DEVICE),
                                retry_policy=RETRY_POLICY_DEFAULT,  
                        )
                        workflow.logger.info(f"apply_interface_config: {device_config_results}") 
                    else:
                        workflow.logger.info(f"Interface {iface_nbx['iface_name']} consistente")
        return {}

