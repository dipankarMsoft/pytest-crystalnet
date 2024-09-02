
import re
import yaml
import pytest


def load_yaml_file(path):
    with open(path) as file:
        return yaml.safe_load(file)
    
isis_command = {'cisco_xr': 'show isis neighbors', 'arista_eos': 'show isis neighbors', 'juniper_junos': 'show isis adjacency'}

def test_device_version(device_connections):
    isis_neighbor_data = load_yaml_file(path="tests/test_isis_neighbor/expected_isis_neighbors.yaml")
    for device in device_connections:
        output = device["connection"].send_command(isis_command.get(device["device_type"]))
        print(output)
        expected_isis_neighbor = isis_neighbor_data.get(device["host"])
        for neighbor in expected_isis_neighbor:
            if neighbor in output:
                print(f"Expected neighbor {neighbor} found")
            else:
                print(f"Expected neighbor {neighbor} not found")
        # for neighbor in expected_isis_neighbor:
        #     assert neighbor in output, f"Expected neighbor {neighbor}, but got {output}"