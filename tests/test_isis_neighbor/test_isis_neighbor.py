
import re
import yaml
import pytest


def load_yaml_file(path):
    with open(path) as file:
        return yaml.safe_load(file)
    
isis_command = {'cisco_xr': 'show isis neighbors', 'arista_eos': 'show isis neighbors', 'juniper_junos': 'show isis adjacency'}

def make_neighbor_dict(matches):
    neighbor_dict = {}
    for match in matches:
        system_id = match[0]
        state = match[1]
        neighbor_dict[system_id] = state
    return neighbor_dict
def test_isis_adj_data(device_connections):
    isis_neighbor_data = load_yaml_file(path="tests/test_isis_neighbor/expected_isis_neighbors.yaml")
    cisco_xr_pattern = r'(\w+\.\w+)\s+\w+\s+\*\w+\*\s+(Up|Down)'
    arista_eos_pattern = r'\S+\s+(\w+\.\w+)\s+\S+\s+\S+\s+\S+\s+(\w+)'
    juniper_junos_pattern = r'\S+\.\S+\s+(\w+\.\w+)\s+\S+\s+(\w+)'
    for device in device_connections:
        output = device["connection"].send_command(isis_command.get(device["device_type"]))
        expected_isis_neighbor = isis_neighbor_data.get(device["host"])
        if device["device_type"] == "cisco_xr":
            matches = re.findall(cisco_xr_pattern, output)
            neighbor_dict = make_neighbor_dict(matches)
        elif device["device_type"] == "arista_eos":
            matches = re.findall(arista_eos_pattern, output)
            neighbor_dict = make_neighbor_dict(matches)
        elif device["device_type"] == "juniper_junos":
            matches = re.findall(juniper_junos_pattern, output)
            neighbor_dict = make_neighbor_dict(matches)
        for neighbor in expected_isis_neighbor:
            assert neighbor_dict.get(neighbor) in ['Up','UP'], f"Expected neighbor {neighbor} state to be Up, but got {neighbor_dict.get(neighbor)}"
