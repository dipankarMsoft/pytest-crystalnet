
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

@pytest.mark.skip(reason="Skipping this test for now")
def test_isis_adj_data(device_connections):
    isis_neighbor_data = load_yaml_file(path="tests/test_isis_neighbor/expected_isis_neighbors.yaml")
    juniper_junos_pattern = r'(\S+\.\S+)\s+(\w+\.\w+)\s+\S+\s+(\w+)'
    arista_eos_pattern = r'1\s+default\s+(\w+\.\w+)\s+\S+\s+(\S+)\s+P2P\s+(\w+)'
    cisco_xr_pattern = r'(\w+\.\w+)\s+(\w+)\s+\*\w+\*\s+(Up|Down)'

    for device in device_connections:
        output = device["connection"].send_command(isis_command.get(device["device_type"]))
        print(f'******Checking isis adj {device["host"]}******')
        print(output)
        expected_isis_neighbor = isis_neighbor_data.get(device["host"])
        if device["device_type"] == "cisco_xr":
            matches = re.findall(cisco_xr_pattern, output)
            neighbor_dict = make_neighbor_dict_cisco_xr(matches)
            # write_dict_to_yaml(neighbor_dict, f"{device['host']}_isis_neighbors.yaml")
        elif device["device_type"] == "arista_eos":
            matches = re.findall(arista_eos_pattern, output)
            neighbor_dict = make_neighbor_dict_arista_eos(matches)
        elif device["device_type"] == "juniper_junos":
            matches = re.findall(juniper_junos_pattern, output)
            neighbor_dict = make_neighbor_dict_juniper_junos(matches)
        # print(neighbor_dict)
        for neighbor in expected_isis_neighbor:
            assert neighbor_dict[neighbor]['state'] in ['Up','UP'], f"Expected neighbor {neighbor} state to be Up, but got {neighbor_dict.get(neighbor['state'])}"

def configure_isis_auth(device_connections,action_to_apply,no_of_keys=1):
    for device in device_connections:
        # print(device)
        isis_neighbor_data = load_yaml_file(path=f"tests/test_isis_neighbor/isis_data/{device['host']}_isis_neighbors.yaml")
        print(f'****** {device["host"]}******')
        if no_of_keys == 1:
            template = Template(open(f"tests/test_isis_neighbor/templates/{device['device_type']}_isis_auth_template.j2").read())
            config = template.render(isis_neighbor_data=isis_neighbor_data, database_auth='abcd', adj_auth='abcd', action=action_to_apply)
        elif no_of_keys == 2:
            template = Template(open(f"tests/test_isis_neighbor/templates/{device['device_type']}_isis_auth_template_2keys.j2").read())
            config = template.render(isis_neighbor_data=isis_neighbor_data, database_auth='abcd', adj_auth='1234', action=action_to_apply)
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
            device["connection"].exit_config_mode()
            print("**** verify the config on the device ****")
            print(device["connection"].send_command("show run formal | include ISIS"))
            
@pytest.mark.skip(reason="Skipping this test for now")
def test_ipv4_ping(device_connections):
    IPv4_loopback = load_yaml_file(path="tests/test_isis_neighbor/ipv4_loopback.yaml")
    for device in device_connections:
        if device["host"] == "ier01.brz01":
            Local_ip = IPv4_loopback.get(device["host"])
            for remote_node, Remote_ip in IPv4_loopback.items():
                if Local_ip != Remote_ip:
                    print(f"Remote node : {remote_node} ping {Remote_ip} source {Local_ip}")
                    output = device["connection"].send_command(f"ping {Remote_ip} source {Local_ip} count 5 interval .1")
                    print(f"\n{output}\n")
                    assert re.search(r"5 packets transmitted, 5 packets received, 0% packet loss", output, re.MULTILINE), f"Ping is not success: {output}"
                else:
                    pass
        else:
            pass

@pytest.mark.skip(reason="Skipping this test for now")
def test_ipv6_ping(device_connections):
    IPv6_loopback = load_yaml_file(path="tests/test_isis_neighbor/ipv6_loopback.yaml")
    for device in device_connections:
        if device["host"] == "ier01.brz01":
            Local_ip = IPv6_loopback.get(device["host"])
            for remote_node, Remote_ip in IPv6_loopback.items():
                if Local_ip != Remote_ip:
                    print(f"Remote node : {remote_node} ping {Remote_ip} source {Local_ip}")
                    output = device["connection"].send_command(f"ping {Remote_ip} source {Local_ip} count 5 interval .1")
                    print(f"\n{output}\n")
                    assert re.search(r"5 packets transmitted, 5 packets received, 0% packet loss", output, re.MULTILINE), f"Ping is not success: {output}"
                else:
                    pass
        else:
            pass 

# def test_isis_adj_with_auth(device_connections):
#     configure_isis_auth(device_connections,action_to_apply='set',no_of_keys=1)
#     time.sleep(40)
#     test_isis_adj_data(device_connections)
#    test_ipv4_ping(device_connections)

# def test_isis_adj_without_auth(device_connections):
#     configure_isis_auth(device_connections,action_to_apply='delete',no_of_keys=1)
#     time.sleep(40)
#     test_isis_adj_data(device_connections)
#    test_ipv4_ping(device_connections)
@pytest.mark.run(order=1)
def test_isis_adj_with_database_adj_auth(device_connections):
    configure_isis_auth(device_connections,action_to_apply='set',no_of_keys=2)
    time.sleep(40)
    test_isis_adj_data(device_connections)
    test_ipv4_ping(device_connections)

@pytest.mark.run(order=2)
def test_isis_adj_without_database_adj_auth(device_connections):
    configure_isis_auth(device_connections,action_to_apply='delete',no_of_keys=2)
    time.sleep(40)
    test_isis_adj_data(device_connections)
    test_ipv4_ping(device_connections)
