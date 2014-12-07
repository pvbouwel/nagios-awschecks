from awschecks.nagioscheck import NagiosExitCodes
from awschecks.nagioscheckscli import NagiosCheckCli

__author__ = 'pvbouwel'

import unittest
from moto import mock_ec2
import boto


class TaggingTests(unittest.TestCase):
    @mock_ec2
    def test_a_volume_without_a_mandatory_critical_tag_must_report_critical_state(self):
        conn = boto.connect_ec2('key', 'secret')
        volume = conn.create_volume(80, "us-east-1a")
        conn.create_tags([volume.id], {"name": "unknown"})

        test_arguments = ["application_title.py","--region", "ALL", "--warning", "warningtag", "--critical",
                          "criticaltag", "--check", "awstagscheck"]
        nagios_cli = NagiosCheckCli(test_arguments)
        with self.assertRaises(SystemExit) as exit_context:
            nagios_cli.execute()
        self.assertEqual(exit_context.exception.code, NagiosExitCodes.CRITICAL)
        volume.delete()

    @mock_ec2
    def test_a_volume_without_a_mandatory_warning_tag_but_with_all_critical_tags_must_report_warning_state(self):
        conn = boto.connect_ec2('key', 'secret')
        volume = conn.create_volume(80, "us-east-1a")
        conn.create_tags([volume.id], {"name": "unknown", "criticaltag": "VeryUsefullTagValue"})

        test_arguments = ["application_title.py","--region", "ALL", "--warning", "warningtag", "--critical",
                          "criticaltag", "--check", "awstagscheck"]
        nagios_cli = NagiosCheckCli(test_arguments)
        with self.assertRaises(SystemExit) as exit_context:
            nagios_cli.execute()
        self.assertEqual(exit_context.exception.code, NagiosExitCodes.WARNING)
        volume.delete()

    @mock_ec2
    def test_a_volume_with_all_mandatory_tags_report_OK_state(self):
        conn = boto.connect_ec2('key', 'secret')
        volume = conn.create_volume(80, "us-east-1a")
        conn.create_tags([volume.id], {"name": "unknown", "criticaltag": "VeryUsefullTagValue"})

        test_arguments = ["application_title.py","--region", "ALL", "--critical",
                          "criticaltag", "--check", "awstagscheck"]
        nagios_cli = NagiosCheckCli(test_arguments)
        with self.assertRaises(SystemExit) as exit_context:
            nagios_cli.execute()
        self.assertEqual(exit_context.exception.code, NagiosExitCodes.OK)
        volume.delete()