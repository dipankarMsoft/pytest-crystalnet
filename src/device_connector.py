import yaml
from netmiko import ConnectHandler

def load_device_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config['devices']

def connect_to_device(device):
    connection = ConnectHandler(**device)
    device['connection'] = connection
    return device