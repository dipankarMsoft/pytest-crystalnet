import re
import yaml
import pytest


def test_isis_config(device_connections):
    for device in device_connections:
        if device["device_type"] == "cisco_xr":
            output = device["connection"].send_command("show run formal | include isis")
            print(f"****** {device['host']}******")
            print(output)
            assert "router isis" in output, f"Expected 'router isis' in output, but got {output}"
        elif device["device_type"] == "arista_eos":
            output = device["connection"].send_command("show run section isis")
            print(f"****** {device['host']}******")
            print(output)
            assert "router isis" in output, f"Expected 'router isis' in output, but got {output}"
        elif device["device_type"] == "juniper_junos":
            output = device["connection"].send_command("show configuration | display set | match isis")
            print(f"****** {device['host']}******")
            print(output)
            assert "protocols isis" in output, f"Expected 'protocols isis' in output, but got {output}"