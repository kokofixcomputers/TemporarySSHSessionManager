import docker
from docker.types import IPAMConfig, IPAMPool

def setup_network(subnet='192.168.52.0/24', gateway='192.168.52.254'):
    client = docker.from_env()
    network_name = "stm"

    # Define IPAM configuration
    ipam_pool = IPAMPool(subnet=subnet, gateway=gateway)
    ipam_config = IPAMConfig(pool_configs=[ipam_pool])


    # Check if the network already exists
    existing_networks = client.networks.list(names=[network_name])

    if not existing_networks:
        # Create the network if it does not exist
        network = client.networks.create(network_name, driver="bridge", ipam=ipam_config)
    else:
        print(f'Network {network_name} already exists.')