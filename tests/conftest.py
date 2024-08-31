import pytest
from src.device_connector import load_device_config, connect_to_device

@pytest.fixture(scope="module")
def device_connections():
    devices = load_device_config('src/config.yaml')
    connections = []
    for device in devices:
        connection = connect_to_device(device)
        connections.append(connection)
    yield connections
    for connection in connections:
        connection.disconnect()