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