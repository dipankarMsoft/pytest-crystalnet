
import re
import yaml
import pytest


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
    arista_eos_pattern = r'\S+\s+(\w+\.\w+)\s+\S+\s+(\S+)\s+\S+\s+(\w+)'
    cisco_xr_pattern = r'(\w+\.\w+)\s+(\w+)\s+\*\w+\*\s+(Up|Down)'

    for device in device_connections:
        output = device["connection"].send_command(isis_command.get(device["device_type"]))
        expected_isis_neighbor = isis_neighbor_data.get(device["host"])
        if device["device_type"] == "cisco_xr":
            matches = re.findall(cisco_xr_pattern, output)
            neighbor_dict = make_neighbor_dict_cisco_xr(matches)
            write_dict_to_yaml(neighbor_dict, f"{device['host']}_isis_neighbors.yaml")
        elif device["device_type"] == "arista_eos":
            matches = re.findall(arista_eos_pattern, output)
            neighbor_dict = make_neighbor_dict_arista_eos(matches)
            write_dict_to_yaml(neighbor_dict, f"{device['host']}_isis_neighbors.yaml")
        elif device["device_type"] == "juniper_junos":
            matches = re.findall(juniper_junos_pattern, output)
            neighbor_dict = make_neighbor_dict_juniper_junos(matches)
            write_dict_to_yaml(neighbor_dict, f"{device['host']}_isis_neighbors.yaml")
        print(neighbor_dict)
        for neighbor in expected_isis_neighbor:
            assert neighbor_dict.get(neighbor['state']) in ['Up','UP'], f"Expected neighbor {neighbor} state to be Up, but got {neighbor_dict.get(neighbor['state'])}"
