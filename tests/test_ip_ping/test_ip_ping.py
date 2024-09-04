
import re
import yaml
# import pytest


def load_device_versions(path):
    with open(path) as file:
        return yaml.safe_load(file)

def test_ipv4_ping(device_connections):
    IPv4_loopback = load_device_versions(path="tests/test_ip_ping/ipv4_loopback.yaml")
    for device in device_connections:
        if device["host"] == "ier01.brz01":
            Local_ip = IPv4_loopback.get(device["host"])
            for remote_node, Remote_ip in IPv4_loopback.items():
                if Local_ip != Remote_ip:
                    print(f"Remote node : {remote_node} ping {Remote_ip} source {Local_ip}")
                    output = device["connection"].send_command(f"ping {Remote_ip} source {Local_ip} count 5 interval .1")
                    print(f"\noutput\n")
                    assert re.search(r"5 packets transmitted, 5 packets received, 0% packet loss", output, re.MULTILINE), f"Ping is not success: {output}"
                else:
                    pass
        else:
            pass

def test_ipv6_ping(device_connections):
    IPv6_loopback = load_device_versions(path="tests/test_ip_ping/ipv6_loopback.yaml")
    for device in device_connections:
        if device["host"] == "ier01.brz01":
            Local_ip = IPv6_loopback.get(device["host"])
            for remote_node, Remote_ip in IPv6_loopback.items():
                if Local_ip != Remote_ip:
                    print(f"Remote node : {remote_node} ping {Remote_ip} source {Local_ip}")
                    output = device["connection"].send_command(f"ping {Remote_ip} source {Local_ip} count 5 interval .1")
                    print(f"\noutput\n")
                    assert re.search(r"5 packets transmitted, 5 packets received, 0% packet loss", output, re.MULTILINE), f"Ping is not success: {output}"
                else:
                    pass
        else:
            pass 