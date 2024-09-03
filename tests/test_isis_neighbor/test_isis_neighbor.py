
import re
import yaml
import pytest
import time
from jinja2 import Template


def load_yaml_file(path):
    with open(path) as file:
        return yaml.safe_load(file)
    
isis_command = {'cisco_xr': 'show isis neighbors', 'arista_eos': 'show isis neighbors', 'juniper_junos': 'show isis adjacency'}

def make_neighbor_dict_juniper_junos(matches):
    neighbor_dict = {}
    for match in matches:
        system_id = match[1]
        state = match[2]
        if_name = match[0]
        neighbor_dict[system_id] = {'if_name': if_name, 'state': state}
    return neighbor_dict

def make_neighbor_dict_arista_eos(matches):
    neighbor_dict = {}
    for match in matches:
        system_id = match[0]
        if_name = match[1]
        state = match[2]
        neighbor_dict[system_id] = {'if_name': if_name, 'state': state}
    return neighbor_dict

def make_neighbor_dict_cisco_xr(matches):
    neighbor_dict = {}
    for match in matches:
        system_id = match[0]
        if_name = match[1]
        state = match[2]
        neighbor_dict[system_id] = {'if_name': if_name, 'state': state}
    return neighbor_dict

# Convert the dictionary to YAML and write it to a file
def write_dict_to_yaml(dictionary, path):
    with open(path, 'w') as file:
        yaml.dump(dictionary, file)

def test_isis_adj_data(device_connections):
    isis_neighbor_data = load_yaml_file(path="tests/test_isis_neighbor/expected_isis_neighbors.yaml")
    juniper_junos_pattern = r'(\S+\.\S+)\s+(\w+\.\w+)\s+\S+\s+(\w+)'
    arista_eos_pattern = r'1\s+default\s+(\w+\.\w+)\s+\S+\s+(\S+)\s+P2P\s+(\w+)'
    cisco_xr_pattern = r'(\w+\.\w+)\s+(\w+)\s+\*\w+\*\s+(Up|Down)'

    for device in device_connections:
        output = device["connection"].send_command(isis_command.get(device["device_type"]))
        print(f'****** {device["host"]}******')
        print(output)
        expected_isis_neighbor = isis_neighbor_data.get(device["host"])
        if device["device_type"] == "cisco_xr":
            matches = re.findall(cisco_xr_pattern, output)
            neighbor_dict = make_neighbor_dict_cisco_xr(matches)
            # write_dict_to_yaml(neighbor_dict, f"{device['host']}_isis_neighbors.yaml")
        elif device["device_type"] == "arista_eos":
            matches = re.findall(arista_eos_pattern, output)
            print(matches)
            neighbor_dict = make_neighbor_dict_arista_eos(matches)
        elif device["device_type"] == "juniper_junos":
            matches = re.findall(juniper_junos_pattern, output)
            neighbor_dict = make_neighbor_dict_juniper_junos(matches)
        # print(neighbor_dict)
        for neighbor in expected_isis_neighbor:
            assert neighbor_dict[neighbor]['state'] in ['Up','UP'], f"Expected neighbor {neighbor} state to be Up, but got {neighbor_dict.get(neighbor['state'])}"

def configure_isis_auth(device_connections,action_to_apply):
    for device in device_connections:
        # print(device)
        isis_neighbor_data = load_yaml_file(path=f"tests/test_isis_neighbor/isis_data/{device['host']}_isis_neighbors.yaml")
        print(f'****** {device["host"]}******')
        # print(isis_neighbor_data)
        template = Template(open(f"tests/test_isis_neighbor/templates/{device['device_type']}_isis_auth_template.j2").read())
        config = template.render(isis_neighbor_data=isis_neighbor_data, database_auth='abcd', adj_auth='abcd', action=action_to_apply)
        print("**** config to be applied ****")
        print(config)
        if device["device_type"] == "juniper_junos":
            device["connection"].send_config_set(config.splitlines())
            device["connection"].commit()  # Use the commit method with a comment
            device["connection"].exit_config_mode()
            print("**** verify the config on the device ****")
            print(device["connection"].send_command("show configuration | display set | match isis "))
        elif device["device_type"] == "arista_eos":
            device["connection"].send_config_set(config.splitlines())
            device["connection"].save_config()  # Save the configuration to persist the changes
            print("**** verify the config on the device ****")
            print(device["connection"].send_command("show run sec isis | include auth"))
        elif device["device_type"] == "cisco_xr":
            device["connection"].send_config_set(config.splitlines())
            device["connection"].commit()
            print("**** verify the config on the device ****")
            print(device["connection"].send_command("show run formal | include ISIS"))

def test_isis_adj_with_auth(device_connections):
    configure_isis_auth(device_connections,action_to_apply='set')
    time.sleep(20)
    test_isis_adj_data(device_connections)

def test_isis_adj_without_auth(device_connections):
    configure_isis_auth(device_connections,action_to_apply='delete')
    time.sleep(10)
    test_isis_adj_data(device_connections)
