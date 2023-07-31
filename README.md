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

```python
from napalm import get_network_driver

driver = get_network_driver('mimosa')
device = driver(
    snmp_community='your_community', 
    radio_type='ptp', 
    hostname='your_hostname'
)

# No need to open or close connection as the SNMP driver does not establish a connection.
print(device.get_facts())
```

Please replace `'your_community'`, `'ptp'` and `'your_hostname'` with your SNMP community, radio type, and hostname respectively.

## Features

This driver supports the following NAPALM getter methods:

- get_facts
- get_interfaces_list
- get_interfaces
- get_interfaces_ip
- get_wireless_settings
- get_dns_servers
- get_services

## Contributing

We welcome contributions from everyone. If you've got a feature request, bug report, or a new feature of your own, feel free to make a pull request or open an issue. 

## License

This project is licensed under the terms of the MIT license.
