import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "addon"))

from syslogger.parser import parse


class ParserTests(unittest.TestCase):
    def test_rfc3164(self):
        r = parse("<34>Oct 11 22:14:15 mymachine su: 'su root' failed", "10.0.0.1")
        self.assertEqual(r["facility"], "auth")
        self.assertEqual(r["severity"], 2)
        self.assertEqual(r["host"], "mymachine")
        self.assertEqual(r["app"], "su")
        self.assertEqual(r["message"], "'su root' failed")

    def test_rfc3164_with_pid(self):
        r = parse("<14>Oct  7 10:15:35 host1 app[99]: hello", "10.0.0.1")
        self.assertEqual(r["app"], "app")
        self.assertEqual(r["message"], "hello")

    def test_rfc5424(self):
        r = parse("<165>1 2026-10-17T10:15:32.003Z router1 sshd 1234 ID47 - Accepted password", "10.0.0.2")
        self.assertEqual(r["facility"], "local4")
        self.assertEqual(r["severity"], 5)
        self.assertEqual(r["host"], "router1")
        self.assertEqual(r["app"], "sshd")
        self.assertEqual(r["message"], "Accepted password")

    def test_rfc5424_structured_data(self):
        r = parse('<11>1 2026-10-17T10:15:33Z esp firmware - - [meta k="v"] Sensor failed', "10.0.0.3")
        self.assertEqual(r["severity"], 3)
        self.assertEqual(r["message"], "Sensor failed")

    def test_rfc5424_nil_host_falls_back_to_source(self):
        r = parse("<14>1 2026-10-17T10:15:33Z - app - - - msg", "10.0.0.4")
        self.assertEqual(r["host"], "10.0.0.4")

    def test_no_pri(self):
        r = parse("just some text\n", "10.0.0.5")
        self.assertIsNone(r["severity"])
        self.assertEqual(r["host"], "10.0.0.5")
        self.assertEqual(r["message"], "just some text")

    def test_tasmota_without_pri(self):
        r = parse("Western ESP-WIF: Checking connection...", "192.168.10.66")
        self.assertEqual(r["host"], "Western")
        self.assertEqual(r["app"], "ESP-WIF")
        self.assertEqual(r["message"], "Checking connection...")
        self.assertIsNone(r["severity"])

    def test_tasmota_boot_banner_has_no_colon(self):
        r = parse("Western ESP-Project tasmota - Western Sensor Version 9.5.0.99", "192.168.10.66")
        self.assertEqual(r["host"], "Western")
        self.assertEqual(r["app"], "ESP-Project")
        self.assertEqual(r["message"], "tasmota - Western Sensor Version 9.5.0.99")

    def test_tasmota_with_pri_and_no_timestamp(self):
        r = parse("<14>eastern ESP-MQT: tele/easternsensor/SENSOR = {}", "192.168.10.108")
        self.assertEqual(r["host"], "eastern")
        self.assertEqual(r["app"], "ESP-MQT")
        self.assertEqual(r["severity"], 6)
        self.assertEqual(r["message"], "tele/easternsensor/SENSOR = {}")

    def test_invalid_pri(self):
        self.assertIsNone(parse("<999>foo", "1.1.1.1")["severity"])

    def test_unparseable_body_keeps_text(self):
        r = parse("<13>weird body", "1.1.1.1")
        self.assertEqual(r["severity"], 5)
        self.assertEqual(r["message"], "weird body")


if __name__ == "__main__":
    unittest.main()
