
import re
import yaml
import pytest

device_pattern = {'cisco_xr': 'Version\s+:\s(\S+)\s', 'arista_eos': 'Software image version:\s(\S+)', 'juniper_junos': 'Junos:\s(\S+)'}

def load_device_versions(path):
    with open(path) as file:
        return yaml.safe_load(file)

def test_device_version(device_connections):
    device_versions = load_device_versions(path="tests/device_versions.yaml")
    print(device_pattern)
    for device in device_connections:
        output = device["connection"].send_command("show version")
        print(output)
        match = re.match(device_pattern.get(device["device_type"]), output, re.MULTILINE)
        if match:
            print(match.group(1))
        expected_version = device_versions.get(device["device_type"])
        assert expected_version in output, f"Expected version {expected_version}, but got {output}"