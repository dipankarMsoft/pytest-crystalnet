import pytest
import os
from src.device_connector import load_device_config, connect_to_device

@pytest.fixture(scope="module")
def device_connections():
    devices = load_device_config('src/config.yaml')
    connections = []
    user_name = os.getenv('USERNAME')
    pass_word = os.getenv('PASSWORD')
    for device in devices:
        device['username'] = user_name
        device['password'] = pass_word
        device["connection"] = connect_to_device(device)
        device.pop("password")
        device.pop("username")
        connections.append(device)
    yield connections
    for device in connections:
        device["connection"].disconnect()