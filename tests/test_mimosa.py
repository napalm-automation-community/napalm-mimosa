import unittest
from napalm_mimosa import MimosaDriver
from unittest import mock


class MockSnmpResponse:
    def prettyPrint(self):
        return "mocked_result"


class TestMimosaDriver(unittest.TestCase):
    def test_initialization(self):
        driver = MimosaDriver("community", "a_series", "hostname")
        self.assertEqual(driver.snmp_community, "community")
        self.assertEqual(driver.radio_type, "a_series")
        self.assertEqual(driver.hostname, "hostname")

    def test_validate_series(self):
        driver = MimosaDriver("community", "a_series", "hostname")
        driver.validate_series()

    @mock.patch("napalm_mimosa.mimosa.getCmd")
    @mock.patch("napalm_mimosa.mimosa.UdpTransportTarget")
    @mock.patch("napalm_mimosa.mimosa.SnmpEngine")
    def test_snmp_get(self, mock_snmp_engine, mock_udp_transport_target, mock_getCmd):
        mock_udp_transport_target.return_value = "mocked_transport_target"
        mock_getCmd.return_value = iter(
            [(None, None, None, [("", MockSnmpResponse())])]
        )
        driver = MimosaDriver("community", "a_series", "hostname")
        expected_oid = ".1.3.6.1.4.1.43356.2.1.2.1.6.0"

        result = driver._snmp_get(expected_oid)

        self.assertEqual(result, "mocked_result")
        mock_udp_transport_target.assert_called_once_with(("hostname", 161))
        mock_getCmd.assert_called_once()
        mock_snmp_engine.assert_called_once()


if __name__ == "__main__":
    unittest.main()
