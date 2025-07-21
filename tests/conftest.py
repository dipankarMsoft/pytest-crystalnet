import pytest
import os
from src.device_connector import load_device_config, connect_to_device
from concurrent.futures import ThreadPoolExecutor

@pytest.fixture(scope="module")
def device_connections():
    devices = load_device_config('src/config.yaml')
    connections = []
    user_name = os.getenv('USERNAME')
    pass_word = os.getenv('PASSWORD')
    # Store auth variables in a dictionary for later use
    auth_vars = {
        "xr_database_auth_old": os.getenv('XR_DATABASE_AUTH_OLD'),
        "xr_database_auth_new": os.getenv('XR_DATABASE_AUTH_NEW'),
        "eos_database_auth_old": os.getenv('EOS_DATABASE_AUTH_OLD'),
        "eos_database_auth_new": os.getenv('EOS_DATABASE_AUTH_NEW'),
        "jnpr_database_auth_old": os.getenv('JNPR_DATABASE_AUTH_OLD'),
        "jnpr_database_auth_new": os.getenv('JNPR_DATABASE_AUTH_NEW'),
    }
    # Attach auth_vars to the fixture object for access in other methods
    device_connections.auth_vars = auth_vars
    
    with ThreadPoolExecutor() as executor:
        futures = []
        for device in devices:
            device['username'] = user_name
            device['password'] = pass_word
            futures.append(executor.submit(connect_to_device, device))
        
        for future in futures:
            connection = future.result()
        for device in devices:
            device.pop("password")
            device.pop("username")
            connections.append(device)
    
    yield connections
    
    for device in connections:
        device["connection"].disconnect()