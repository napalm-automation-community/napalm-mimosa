# napalm-mimosa
Mimosa Radios
# Napalm-Mimosa

A Network Automation and Programmability Abstraction Layer with Multivendor support (NAPALM) driver for Mimosa Radios.

## Overview

This is a custom NAPALM driver which is designed to use SNMP (Simple Network Management Protocol) to interact with Mimosa Radios. It does not establish a direct connection to the device but gathers information via SNMP.

## Requirements

- Python 3.7+
- Napalm 4.1.0+
- pysnmp 4.4.12+
- pysnmp-pyasn1 1.1.3+

## Installation

1. Clone the repository.
2. Navigate to the root directory of the project (where the `pyproject.toml` file resides).
3. Run `poetry install` to install the project and its dependencies.

## Usage

Here is a basic usage example:
radio_type='a_series' or 'b_c_series'

```python
from napalm import get_network_driver

driver = get_network_driver('mimosa')
device = driver(
    snmp_community='your_community', 
    radio_type='a_series', 
    hostname='your_hostname'
)

# No need to open or close connection as the SNMP driver does not establish a connection.
print(device.get_facts())
```

Please replace `'your_community'`, `'a_series'` and `'your_hostname'` with your SNMP community, radio type, and hostname respectively.

## Features

This driver supports the following NAPALM getter methods:

- get_facts
- get_interfaces_list
- get_interfaces
- get_interfaces_ip
- get_wireless_settings
- get_dns_servers
- get_services

## Examples
```python
from napalm import get_network_driver
driver = get_network_driver("mimosa")
device = driver(
    hostname="10.10.10.28", snmp_community="admin123", radio_type="b_c_series"
)
print(device.get_facts())

print(device.get_interfaces())

print(device.get_interfaces_ip())


print(device.get_wireless_settings())


print(device.get_dns_servers())


print(device.get_services())
```
## Results b_c series

```python
{
    'uptime': '53614393',
    'vendor': 'Mimosa',
    'os_version': '2.4.6',
    'serial_number': 'your_serial_number',
    'model': 'mimosaB5',
    'hostname': 'mimosa',
    'fqdn': 'mimosa',
    'interface_list': ['eth1_emac1', 'eth1_emac2', 'wifi0']
}
{
    'eth1_emac1': {
        'is_up': True,
        'is_enabled': True,
        'description': 'eth1_emac1',
        'last_flapped': -1.0,
        'speed': 1000.0,
        'mtu': 1500,
        'mac_address': 'your_mac'
    },
    'eth1_emac2': {
        'is_up': False,
        'is_enabled': True,
        'description': 'eth1_emac2',
        'last_flapped': -1.0,
        'speed': 1000.0,
        'mtu': 1500,
        'mac_address': 'your_mac'
    },
    'wifi0': {
        'is_up': True,
        'is_enabled': True,
        'description': 'wifi0',
        'last_flapped': -1.0,
        'speed': 0.0,
        'mtu': 1500,
        'mac_address': 'your_mac'
    }
}
{'br_local': {'ipv4': {'10.10.10.5': {'prefix_length': 24}}}}
{
    'unlock_code': 'your_unlock_code',
    'regulatory_domain': 'United States',
    'wan_ssid': 'mimosa064',
    'wan_status': 'disconnected',
    'wireless_mode': 'accessPoint',
    'tdma_mode': 'a',
    'tdma_window': '4',
    'traffic_split': 'auto',
    'network_mode': 'auto',
    'recovery_ssid': 'mimosaR064',
    'local_ssid': 'mimosaM064',
    'local_channel': '6'
}
{'primary_dns_server': '8.8.8.8', 'secondary_dns_server': '8.8.4.4'}
{
    'https_status': 'disabled',
    'mgmt_vlan_status': 'disabled',
    'mgmt_cloud_status': 'enabled',
    'syslog_status': 'disabled'
}

```

```python
from napalm import get_network_driver
driver = get_network_driver("mimosa")
device = driver(
    hostname="10.10.10.28", snmp_community="admin123", radio_type="a_series"
)
print(device.get_facts())

print(device.get_interfaces())

print(device.get_interfaces_ip())


print(device.get_wireless_settings())


print(device.get_dns_servers())


print(device.get_services())
```
## Results a_series

```python
{
    'uptime': '423520',
    'vendor': 'Mimosa',
    'os_version': '2.5.2',
    'serial_number': 'your_serial_number',
    'model': 'mimosaA5',
    'hostname': 'mimosaA5',
    'fqdn': 'mimosaA5',
    'interface_list': ['A5EthPort', 'wifi0', 'wifi1', 'wlan0']
}
{
    'A5EthPort': {
        'is_up': True,
        'is_enabled': True,
        'description': 'A5EthPort',
        'last_flapped': -1.0,
        'speed': 1048.576,
        'mtu': 1500,
        'mac_address': 'your_mac'
    },
    'wifi0': {
        'is_up': True,
        'is_enabled': True,
        'description': 'wifi0',
        'last_flapped': -1.0,
        'speed': 1073.741824,
        'mtu': 1500,
        'mac_address': 'your_mac'
    },
    'wifi1': {
        'is_up': False,
        'is_enabled': True,
        'description': 'wifi1',
        'last_flapped': -1.0,
        'speed': 1073.741824,
        'mtu': 1500,
        'mac_address': 'your_mac'
    },
    'wlan0': {
        'is_up': True,
        'is_enabled': True,
        'description': 'wlan0',
        'last_flapped': -1.0,
        'speed': 0.0,
        'mtu': 1500,
        'mac_address': 'your_mac'
    }
}
{'br_local': {'ipv4': {'10.10.10.5': {'prefix_length': 24}}}}
{
    'unlock_code': 'your_unlock_code',
    'regulatory_domain': 'United States',
    'mimosa_wireless_mode': 'wifiinterop',
    'mimosa_auto_channel': 'false',
    'ssid_table': {
        '1': {
            'mimosaPtmpSsidName': 'labtest3',
            'mimosaPtmpSsidType': 'cpe',
            'mimosaPtmpSsidEnabled': 'true',
            'mimosaPtmpSsidBroadcastEnabled': 'true',
            'mimosaPtmpSsidIsolationEnabled': 'true'
        },
        '2': {
            'mimosaPtmpSsidName': 'fdsfsfsfdsfsd',
            'mimosaPtmpSsidType': 'cpe',
            'mimosaPtmpSsidEnabled': 'true',
            'mimosaPtmpSsidBroadcastEnabled': 'true',
            'mimosaPtmpSsidIsolationEnabled': 'true'
        },
        '3': {
            'mimosaPtmpSsidName': 'fdfsdfdsfsf',
            'mimosaPtmpSsidType': 'hotspot',
            'mimosaPtmpSsidEnabled': 'false',
            'mimosaPtmpSsidBroadcastEnabled': 'true',
            'mimosaPtmpSsidIsolationEnabled': 'true'
        },
        '4': {
            'mimosaPtmpSsidName': 'mimosaM336',
            'mimosaPtmpSsidType': 'hotspot',
            'mimosaPtmpSsidEnabled': 'true',
            'mimosaPtmpSsidBroadcastEnabled': 'true',
            'mimosaPtmpSsidIsolationEnabled': 'true'
        }
    },
    'channel_power_table': {
        '1': {
            'mimosaPtmpChPwrRadioName': 'MIMOSA-5Ghz-1',
            'mimosaPtmpChPwrCntrFreqCfg': '5240',
            'mimosaPtmpChPwrPrimChannelCfg': '48',
            'mimosaPtmpChPwrChWidthCfg': '20',
            'mimosaPtmpChPwrTxPowerCfg': '24',
            'mimosaPtmpChPwrCntrFreqCur': '5240',
            'mimosaPtmpChPwrPrimChannelCur': '48',
            'mimosaPtmpChPwrChWidthCur': '20',
            'mimosaPtmpChPwrTxPowerCur': '24',
            'mimosaPtmpChPwrAgcMode': '2',
            'mimosaPtmpChPwrMinRxPower': '0'
        },
        '2': {
            'mimosaPtmpChPwrRadioName': 'MIMOSA-2Ghz-1',
            'mimosaPtmpChPwrCntrFreqCfg': '2437',
            'mimosaPtmpChPwrPrimChannelCfg': '6',
            'mimosaPtmpChPwrChWidthCfg': '20',
            'mimosaPtmpChPwrTxPowerCfg': '16',
            'mimosaPtmpChPwrCntrFreqCur': '2437',
            'mimosaPtmpChPwrPrimChannelCur': '6',
            'mimosaPtmpChPwrChWidthCur': '20',
            'mimosaPtmpChPwrTxPowerCur': '16',
            'mimosaPtmpChPwrAgcMode': 'off',
            'mimosaPtmpChPwrMinRxPower': '0'
        }
    }
}
{'primary_dns_server': '8.8.8.8', 'secondary_dns_server': '8.8.4.4'}
{'mgmt_vlan_status': 'disabled', 'mgmt_vlan_passthrough': 'disabled'}

```

## Contributing

We welcome contributions from everyone. If you've got a feature request, bug report, or a new feature of your own, feel free to make a pull request or open an issue. 

## License

This project is licensed under the terms of the MIT license.
