
import re
import yaml
import pytest


def load_device_versions(path):
    with open(path) as file:
        return yaml.safe_load(file)
    
@pytest.mark.skip(reason="Skipping this test for now")
def test_device_version(device_connections):
    device_versions = load_device_versions(path="tests/test_version/device_versions.yaml")
    for device in device_connections:
        output = device["connection"].send_command("show version")
        expected_version = device_versions.get(device["device_type"])
        assert expected_version in output, f"Expected version {expected_version}, but got {output}"