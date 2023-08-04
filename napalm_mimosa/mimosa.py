"""
Napalm driver for Mimosa. This driver does not establish a connection with the device;
instead, it utilizes SNMP to gather information.

Please refer to napalm.readthedocs.org for more information.

"""

from napalm.base.base import NetworkDriver
from pysnmp.hlapi import *
from ipaddress import ip_network


class MimosaDriver(NetworkDriver):
    b_c_series_OIDs = {
        # OIDs for the b and c series
        "unlock_code": ".1.3.6.1.4.1.43356.2.1.2.1.6.0",
        "regulatory_domain": ".1.3.6.1.4.1.43356.2.1.2.1.9.0",
        "wan_ssid": ".1.3.6.1.4.1.43356.2.1.2.3.1.0",
        "wan_status": ".1.3.6.1.4.1.43356.2.1.2.3.3.0",
        "wireless_mode": ".1.3.6.1.4.1.43356.2.1.2.4.1.0",
        "tdma_mode": ".1.3.6.1.4.1.43356.2.1.2.4.2.0",
        "tdma_window": ".1.3.6.1.4.1.43356.2.1.2.4.4.0",
        "traffic_split": ".1.3.6.1.4.1.43356.2.1.2.4.5.0",
        "network_mode": ".1.3.6.1.4.1.43356.2.1.2.5.1.0",
        "recovery_ssid": ".1.3.6.1.4.1.43356.2.1.2.5.2.0",
        "local_ssid": ".1.3.6.1.4.1.43356.2.1.2.5.3.0",
        "local_channel": ".1.3.6.1.4.1.43356.2.1.2.5.4.0",
        "mimosa_local_ip": ".1.3.6.1.4.1.43356.2.1.2.5.8.0",
        "mimosa_netmask": ".1.3.6.1.4.1.43356.2.1.2.5.9.0",
        "primary_dns_server": ".1.3.6.1.4.1.43356.2.1.2.5.12.0",
        "secondary_dns_server": ".1.3.6.1.4.1.43356.2.1.2.5.13.0",
        "https_status": ".1.3.6.1.4.1.43356.2.1.2.8.1.0",
        "mgmt_vlan_status": ".1.3.6.1.4.1.43356.2.1.2.8.2.0",
        "mgmt_cloud_status": ".1.3.6.1.4.1.43356.2.1.2.8.3.0",
        "syslog_status": ".1.3.6.1.4.1.43356.2.1.2.8.6.0",
    }

    a_series_OIDs = {
        # OIDs for the a series
        "unlock_code": ".1.3.6.1.4.1.43356.2.1.2.1.6.0",
        "regulatory_domain": ".1.3.6.1.4.1.43356.2.1.2.1.9.0",
        "mimosa_local_ip": ".1.3.6.1.4.1.43356.2.1.2.9.7.1.0",
        "mimosa_netmask": ".1.3.6.1.4.1.43356.2.1.2.9.7.2.0",
        "mimosa_ssid_list": ".1.3.6.1.4.1.43356.2.1.2.9.1.1",
        "mimosa_wireless_mode": ".1.3.6.1.4.1.43356.2.1.2.9.2.1.0",
        "mimosa_auto_channel": ".1.3.6.1.4.1.43356.2.1.2.9.3.1.0",
        "primary_dns_server": ".1.3.6.1.4.1.43356.2.1.2.9.7.5.0",
        "secondary_dns_server": ".1.3.6.1.4.1.43356.2.1.2.9.7.6.0",
        "mgmt_vlan_status": ".1.3.6.1.4.1.43356.2.1.2.9.7.7.0",
        "mgmt_vlan_passthrough": ".1.3.6.1.4.1.43356.2.1.2.9.7.9.0",
    }

    interface_name_mapping = {
        "eth1_emac1": "Ethernet0",
        "eth1_emac2": "Fiber_SFP",
        "wifi0": "Wireless0",
        "lo": "Loopback0",
        "tqe": "Tqe",
        "wlan0": "Wlan0",
        "br0": "Bridge0",
        "br_local": "BridgeLocal",
        "br_recovery": "BridgeRecovery",
        "br1": "Bridge1",
        "mon.wlan0": "MonitorWlan0",
        "wifi1": "Wireless1",
        "A5EthPort": "Ethernet0",
    }

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

    enabled_disabled_mapping = {
        "1": "enabled",
        "0": "disabled",
    }

    enabled_disabled_mapping_backup = {
        "1": "enabled",
        "2": "disabled",
    }

    ptmp_true_false_mapping = {"1": "true", "2": "false"}

    ptmp_wireless_mode_mapping = {
        "1": "srs",
        "2": "wifiinterop",
    }

    ptmp_ssid_type_mapping = {"0": "hotspot", "1": "cpe"}

    ptmp_on_off_mapping = {"1": "on", "0": "off"}

    def __init__(
        self,
        snmp_community,
        radio_type,
        hostname=None,
        username=None,
        password=None,
        optional_args=None,
        timeout=60,
    ) -> None:
        """
        :param snmp_community: SNMP community string
        :param radio_type: Type of radio, either "a_series" or "b_c_series"
        :param hostname: IP or FQDN of the device you want to connect to.
        :param username: No username required for SNMP
        :param password: No password required for SNMP
        :param optional_args: Pass additional arguments to underlying driver
        :return:
        """
        self.hostname = hostname
        self.username = username
        self.password = password
        self.timeout = timeout
        self.snmp_community = snmp_community
        self.radio_type = radio_type
        self.OIDs = (
            self.b_c_series_OIDs
            if self.radio_type == "b_c_series"
            else self.a_series_OIDs
        )
        self.validate_series()

    def validate_series(self):
        radio_type = ["a_series", "b_c_series"]
        if self.radio_type not in radio_type:
            raise ValueError(f"Invalid series. Series should be one of {radio_type}")

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

        if errorIndication:
            raise Exception(f"SNMP Error: {errorIndication}")
        elif errorStatus:
            raise Exception(f"SNMP Error: {errorStatus.prettyPrint()}")

        result = varBinds[0][1]
        result = result.prettyPrint()

        if result.startswith("0x"):  # Check if result is a hexadecimal string
            hex_string = result[2:]  # Remove '0x' at the start
            bytes_object = bytes.fromhex(hex_string)
            ascii_string = bytes_object.decode("ASCII")
            return ascii_string.strip()

        return result

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
            if errorIndication:
                raise Exception(f"SNMP Error: {errorIndication}")
            elif errorStatus:
                raise Exception(f"SNMP Error: {errorStatus.prettyPrint()}")

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
            if errorIndication:
                raise Exception(f"SNMP Error: {errorIndication}")
            elif errorStatus:
                raise Exception(f"SNMP Error: {errorStatus.prettyPrint()}")

            result.extend(
                [
                    (str(varBind[0]).split(".")[-1], varBind[-1].prettyPrint())
                    for varBind in varBinds
                ]
            )

        return result

    def get_facts(self):
        try:
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
                "hostname": self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.1.1.0"),
                "fqdn": self._snmp_get(".1.3.6.1.4.1.43356.2.1.2.1.1.0"),
                "interface_list": self.get_interfaces_list(),
            }
            return facts
        except Exception as e:
            return f"Error getting facts: {e}"

    def get_interfaces_list(self):
        try:
            interface_list = []
            interfaces = self._snmp_get_multiple("1.3.6.1.2.1.2.2.1.2")
            for intf in interfaces:
                intf = self.interface_name_mapping.get(intf, intf)
                interface_list.append(intf)

            return interface_list if interfaces is not None else []
        except Exception as e:
            return f"Error getting interface list: {e}"

    def get_interfaces(self):
        try:
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
                interface_name = self.interface_name_mapping.get(
                    interface_name, interface_name
                )

                processed_interfaces[interface_name] = interface

            return processed_interfaces
        except Exception as e:
            return f"Error getting interfaces: {e}"

    def get_interfaces_ip(self):
        try:
            interfaces_ip = {}

            # Retrieve the IP address and netmask from the device
            ip_address = self._snmp_get(self.OIDs["mimosa_local_ip"])
            netmask = self._snmp_get(self.OIDs["mimosa_netmask"])

            # Convert the netmask to a prefix length
            network = ip_network(f"{ip_address}/{netmask}", strict=False)
            prefix_length = network.prefixlen

            # Structure the returned data to match the example
            interfaces_ip["br_local"] = {}
            interfaces_ip["br_local"]["ipv4"] = {}
            interfaces_ip["br_local"]["ipv4"][ip_address] = {
                "prefix_length": prefix_length
            }

            return interfaces_ip
        except Exception as e:
            return f"Error getting interfaces ip: {e}"

    def get_wireless_settings(self):
        try:
            if self.radio_type == "b_c_series":
                ptp_wireless_settings = {
                    "unlock_code": self._snmp_get(self.OIDs["unlock_code"]),
                    "regulatory_domain": self._snmp_get(self.OIDs["regulatory_domain"]),
                    "wan_ssid": self._snmp_get(self.OIDs["wan_ssid"]),
                    "wan_status": self.wan_status_mapping.get(
                        self._snmp_get(self.OIDs["wan_status"]), "unknown"
                    ),
                    "wireless_mode": self.wireless_mode_mapping.get(
                        self._snmp_get(self.OIDs["wireless_mode"]), "unknown"
                    ),
                    "tdma_mode": self.tdma_mode_mapping.get(
                        self._snmp_get(self.OIDs["tdma_mode"]), "unknown"
                    ),
                    "tdma_window": self._snmp_get(self.OIDs["tdma_window"]),
                    "traffic_split": self.traffic_split_mapping.get(
                        self._snmp_get(self.OIDs["traffic_split"]), "unknown"
                    ),
                    "network_mode": self.network_mode_mapping.get(
                        self._snmp_get(self.OIDs["network_mode"]), "unknown"
                    ),
                    "recovery_ssid": self._snmp_get(self.OIDs["recovery_ssid"]),
                    "local_ssid": self._snmp_get(self.OIDs["local_ssid"]),
                    "local_channel": self._snmp_get(self.OIDs["local_channel"]),
                }
                return ptp_wireless_settings

            elif self.radio_type == "a_series":
                ssid_list = self._snmp_get_multiple_with_index(
                    oid=".1.3.6.1.4.1.43356.2.1.2.9.1.1"
                )

                processed_ssid_list = {}

                property_names = [
                    "mimosaPtmpSsidName",
                    "mimosaPtmpSsidType",
                    "mimosaPtmpSsidEnabled",
                    "mimosaPtmpSsidBroadcastEnabled",
                    "mimosaPtmpSsidIsolationEnabled",
                ]

                for index, value in ssid_list:
                    if index not in processed_ssid_list:
                        processed_ssid_list[index] = {}
                        continue

                    if len(processed_ssid_list[index]) == 1:
                        value = self.ptmp_ssid_type_mapping.get(value, value)

                    else:
                        value = self.ptmp_true_false_mapping.get(value, value)

                    property_name = property_names[len(processed_ssid_list[index])]

                    processed_ssid_list[index][property_name] = value

                channel_power_table = self._snmp_get_multiple_with_index(
                    oid=".1.3.6.1.4.1.43356.2.1.2.9.3.3"
                )

                processed_channel_power_table = {}

                channel_power_property_names = [
                    "mimosaPtmpChPwrRadioName",
                    "mimosaPtmpChPwrCntrFreqCfg",
                    "mimosaPtmpChPwrPrimChannelCfg",
                    "mimosaPtmpChPwrChWidthCfg",
                    "mimosaPtmpChPwrTxPowerCfg",
                    "mimosaPtmpChPwrCntrFreqCur",
                    "mimosaPtmpChPwrPrimChannelCur",
                    "mimosaPtmpChPwrChWidthCur",
                    "mimosaPtmpChPwrTxPowerCur",
                    "mimosaPtmpChPwrAgcMode",
                    "mimosaPtmpChPwrMinRxPower",
                ]

                for index, value in channel_power_table:
                    if index not in processed_channel_power_table:
                        processed_channel_power_table[index] = {}
                        continue

                    if len(processed_channel_power_table[index]) == 9:
                        value = self.ptmp_on_off_mapping.get(value, value)

                    property_name = channel_power_property_names[
                        len(processed_channel_power_table[index])
                    ]

                    processed_channel_power_table[index][property_name] = value

                ptmp_wireless_settings = {
                    "unlock_code": self._snmp_get(self.OIDs["unlock_code"]),
                    "regulatory_domain": self._snmp_get(self.OIDs["regulatory_domain"]),
                    "mimosa_wireless_mode": self.ptmp_wireless_mode_mapping.get(
                        self._snmp_get(self.OIDs["mimosa_wireless_mode"]), "unknown"
                    ),
                    "mimosa_auto_channel": self.ptmp_true_false_mapping.get(
                        self._snmp_get(self.OIDs["mimosa_auto_channel"]), "unknown"
                    ),
                    "ssid_table": processed_ssid_list,
                    "channel_power_table": processed_channel_power_table,
                }

                return ptmp_wireless_settings
        except Exception as e:
            return f"Error getting wireless settings: {e}"

    def get_dns_servers(self):
        try:
            if self.radio_type == "b_c_series":
                dns_servers = {
                    "primary_dns_server": self._snmp_get(
                        self.OIDs["primary_dns_server"]
                    ),
                    "secondary_dns_server": self._snmp_get(
                        self.OIDs["secondary_dns_server"]
                    ),
                }
            elif self.radio_type == "a_series":
                dns_servers = {
                    "primary_dns_server": self._snmp_get(
                        self.OIDs["primary_dns_server"]
                    ),
                    "secondary_dns_server": self._snmp_get(
                        self.OIDs["secondary_dns_server"]
                    ),
                }

            return dns_servers
        except Exception as e:
            return f"Error getting DNS servers: {e}"

    def get_services(self):
        try:
            if self.radio_type == "b_c_series":
                services = {
                    "https_status": self.enabled_disabled_mapping_backup.get(
                        self._snmp_get(self.OIDs["https_status"]), "unknown"
                    ),
                    "mgmt_vlan_status": self.enabled_disabled_mapping_backup.get(
                        self._snmp_get(self.OIDs["mgmt_vlan_status"]), "unknown"
                    ),
                    "mgmt_cloud_status": self.enabled_disabled_mapping_backup.get(
                        self._snmp_get(self.OIDs["mgmt_cloud_status"]), "unknown"
                    ),
                    "syslog_status": self.enabled_disabled_mapping_backup.get(
                        self._snmp_get(self.OIDs["syslog_status"]), "unknown"
                    ),
                }

            elif self.radio_type == "a_series":
                services = {
                    "mgmt_vlan_status": self.enabled_disabled_mapping.get(
                        self._snmp_get(self.OIDs["mgmt_vlan_status"]), "unknown"
                    ),
                    "mgmt_vlan_passthrough": self.enabled_disabled_mapping.get(
                        self._snmp_get(self.OIDs["mgmt_vlan_passthrough"]), "unknown"
                    ),
                }

            return services
        except Exception as e:
            return f"Error getting services: {e}"
