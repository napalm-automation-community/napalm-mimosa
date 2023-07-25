from napalm.base.base import NetworkDriver
from pysnmp.hlapi import *
from ipaddress import ip_network, ip_address
from rich import print


class MimosaDriver(NetworkDriver):
    def __init__(
        self,
        hostname,
        username,
        password,
        timeout=60,
        snmp_community="public",
        optional_args=None,
    ):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.timeout = timeout
        self.snmp_community = snmp_community

    def open(self):
        pass  # we don't need to open a connection for SNMP

    def close(self):
        pass  # likewise, no connection to close

    def _snmp_get(self, mib, oid=None):
        if mib.startswith("."):
            # OID provided, not MIB
            object_id = ObjectType(ObjectIdentity(mib))
        else:
            # MIB and OID provided
            object_id = ObjectType(ObjectIdentity(mib, oid, 0))

        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(
                SnmpEngine(),
                CommunityData(self.snmp_community),
                UdpTransportTarget((self.hostname, 161)),
                ContextData(),
                object_id,
            )
        )

        if errorIndication or errorStatus:
            return None

        result = varBinds[0][1]

        return result.prettyPrint()

    def _snmp_get_multiple(self, oid):
        object_id = ObjectType(ObjectIdentity(oid))

        result = []

        for errorIndication, errorStatus, errorIndex, varBinds in nextCmd(
            SnmpEngine(),
            CommunityData(self.snmp_community),
            UdpTransportTarget((self.hostname, 161)),
            ContextData(),
            object_id,
            lexicographicMode=False,
        ):
            if errorIndication or errorStatus:
                return None

            result.extend([varBind[-1].prettyPrint() for varBind in varBinds])

        return result

    def _snmp_get_multiple_with_index(self, oid):
        object_id = ObjectType(ObjectIdentity(oid))

        result = []

        for errorIndication, errorStatus, errorIndex, varBinds in nextCmd(
            SnmpEngine(),
            CommunityData(self.snmp_community),
            UdpTransportTarget((self.hostname, 161)),
            ContextData(),
            object_id,
            lexicographicMode=False,
        ):
            if errorIndication or errorStatus:
                return None

            result.extend(
                [
                    (str(varBind[0]).split(".")[-1], varBind[-1].prettyPrint())
                    for varBind in varBinds
                ]
            )

        return result

    def get_facts(self):
        # map sysObjectID values to model names
        model_map = {
            "SNMPv2-SMI::enterprises.43356.1.1.1": "mimosaB5",
            "SNMPv2-SMI::enterprises.43356.1.1.2": "mimosaB5Lite",
            "SNMPv2-SMI::enterprises.43356.1.1.3": "mimosaA5",
            "SNMPv2-SMI::enterprises.43356.1.1.4": "mimosaC5",
        }

        sysObjectID = self._snmp_get(".1.3.6.1.2.1.1.2.0")

        facts = {
            "uptime": self._snmp_get(".1.3.6.1.2.1.1.3.0"),
            "vendor": "Mimosa",
            "os_version": self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.1.3.0"),
            "serial_number": self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.1.2.0"),
            "model": model_map.get(
                sysObjectID, "Unknown"
            ),  # map the sysObjectID to a model
            "hostname": self._snmp_get(".1.3.6.1.2.1.1.5.0"),
            "fqdn": self._snmp_get(".1.3.6.1.2.1.1.5.0"),
            "interface_list": self.get_interfaces_list(),  # SNMP does not typically provide this info
        }
        return facts

    def get_interfaces_list(self):
        interfaces = self._snmp_get_multiple("1.3.6.1.2.1.2.2.1.2")
        return interfaces if interfaces is not None else []

    def get_interfaces(self):
        interfaces = {}

        # OIDs for the different interface data we want to collect
        oids = {
            "ifDescr": "1.3.6.1.2.1.2.2.1.2",
            "ifOperStatus": "1.3.6.1.2.1.2.2.1.8",
            "ifAdminStatus": "1.3.6.1.2.1.2.2.1.7",
            "ifSpeed": "1.3.6.1.2.1.2.2.1.5",
            "ifMtu": "1.3.6.1.2.1.2.2.1.4",
            "ifPhysAddress": "1.3.6.1.2.1.2.2.1.6",
        }

        # Get interface data
        for oid_name, oid in oids.items():
            results = self._snmp_get_multiple_with_index(oid)
            if results is None:
                return {}

            for interface_index, interface_value in results:
                if interface_index not in interfaces:
                    interfaces[interface_index] = {}
                interfaces[interface_index][oid_name] = interface_value

        # Post-process the interface data
        processed_interfaces = {}
        for interface_index, interface in interfaces.items():
            interface["is_up"] = interface.pop("ifOperStatus") == "1"
            interface["is_enabled"] = interface.pop("ifAdminStatus") == "1"
            interface["description"] = interface.pop("ifDescr")
            interface["last_flapped"] = -1.0  # SNMP doesn't provide this data
            interface["speed"] = (
                float(interface.pop("ifSpeed", 0)) / 1000000.0
            )  # Convert speed from bps to Mbps
            interface["mtu"] = int(interface.pop("ifMtu", 0))

            if "ifPhysAddress" in interface:
                phys_addr = interface.pop("ifPhysAddress")
                # Ensure the MAC address has correct length and format
                if phys_addr.startswith("0x"):
                    # Convert hexadecimal string to proper MAC format
                    formatted_mac = ":".join(
                        [phys_addr[i : i + 2] for i in range(2, len(phys_addr), 2)]
                    )
                    interface["mac_address"] = formatted_mac
                else:
                    interface["mac_address"] = ""
            else:
                interface["mac_address"] = ""

            interface_name = interface["description"]
            processed_interfaces[interface_name] = interface

        return processed_interfaces

    def get_interfaces_ip(self):
        interfaces_ip = {}

        # OIDs for the different interface IP data we want to collect
        oids = {
            "mimosa_local_ip": ".1.3.6.1.4.1.43356.2.1.2.5.8.0",
            "mimosa_netmask": ".1.3.6.1.4.1.43356.2.1.2.5.9.0",
        }

        # Retrieve the IP address and netmask from the device
        ip_address = self._snmp_get(oids["mimosa_local_ip"])
        netmask = self._snmp_get(oids["mimosa_netmask"])
        # Convert the netmask to a prefix length
        network = ip_network(f"{ip_address}/{netmask}", strict=False)
        prefix_length = network.prefixlen

        # Structure the returned data to match the example
        interfaces_ip["br_local"] = {}
        interfaces_ip["br_local"]["ipv4"] = {}
        interfaces_ip["br_local"]["ipv4"][ip_address] = {"prefix_length": prefix_length}

        return interfaces_ip

    def get_wireless_settings(self):
        wan_status_mapping = {
            "1": "connected",
            "2": "disconnected",
        }

        wireless_mode_mapping = {
            "1": "accessPoint",
            "2": "station",
        }

        tdma_mode_mapping = {
            "1": "a",
            "2": "b",
        }

        traffic_split_mapping = {
            "1": "symmetric",
            "2": "asymmetric",
            "3": "auto",
        }

        network_mode_mapping = {
            "1": "enabled",
            "2": "disabled",
            "3": "auto",
        }

        wireless_settings = {
            "unlock_code": self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.1.6.0"),
            "regulatory_domain": self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.1.9.0"),
            "wan_ssid": self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.3.1.0"),
            "wan_status": wan_status_mapping.get(
                self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.3.3.0"), "unknown"
            ),
            "wireless_mode": wireless_mode_mapping.get(
                self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.4.1.0"), "unknown"
            ),
            "tdma_mode": tdma_mode_mapping.get(
                self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.4.2.0"), "unknown"
            ),
            "tdma_window": self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.4.4.0"),
            "traffic_split": traffic_split_mapping.get(
                self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.4.5.0"), "unknown"
            ),
            "network_mode": network_mode_mapping.get(
                self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.5.1.0"), "unknown"
            ),
            "recovery_ssid": self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.5.2.0"),
            "local_ssid": self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.5.3.0"),
            "local_channel": self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.5.4.0 "),
        }
        return wireless_settings

    def get_dns_servers(self):
        dns_servers = {
            "primary_dns_server": self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.5.12.0"),
            "secondary_dns_server": self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.5.13.0"),
        }

        return dns_servers

    def get_services(self):
        https_status_mapping = {
            "1": "enabled",
            "2": "disabled",
        }

        mgmt_vlan_mapping = {
            "1": "enabled",
            "2": "disabled",
        }

        mgmt_cloud_mapping = {
            "1": "enabled",
            "2": "disabled",
        }

        syslog_mapping = {
            "1": "enabled",
            "2": "disabled",
        }

        services = {
            "https_status": https_status_mapping.get(
                self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.8.1.0"), "unknown"
            ),
            "mgmt_vlan_status": mgmt_vlan_mapping.get(
                self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.8.2.0"), "unknown"
            ),
            "mgmt_cloud_status": mgmt_cloud_mapping.get(
                self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.8.3.0"), "unknown"
            ),
            "syslog_status": syslog_mapping.get(
                self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.8.6.0"), "unknown"
            ),
        }

        return services
