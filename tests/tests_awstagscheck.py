from awschecks.nagioscheck import NagiosExitCodes
from awschecks.nagioscheckscli import NagiosCheckCli

__author__ = 'pvbouwel'

import unittest
from moto import mock_ec2
import boto
from boto import ec2
from awschecks.awstagscheck import AWSTagCheck
from awschecks.nagioscheck import NagiosCheckOptionError


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
            nagios_cli.process_arguments()
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
            nagios_cli.process_arguments()
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
            nagios_cli.process_arguments()
            nagios_cli.execute()
        self.assertEqual(exit_context.exception.code, NagiosExitCodes.OK)
        volume.delete()

    @mock_ec2
    def test_a_volume_without_a_mandatory_warning_tag_but_with_all_critical_tags_must_report_warning_state_if_ALL_resources_is_set(self):
        conn = boto.connect_ec2('key', 'secret')
        volume = conn.create_volume(80, "us-east-1a")
        conn.create_tags([volume.id], {"name": "unknown", "criticaltag": "VeryUsefullTagValue"})

        test_arguments = ["application_title.py","--region", "ALL", "--warning", "warningtag", "--critical",
                          "criticaltag", "--resource", "ALL", "--check", "awstagscheck"]
        nagios_cli = NagiosCheckCli(test_arguments)
        with self.assertRaises(SystemExit) as exit_context:
            nagios_cli.process_arguments()
            nagios_cli.execute()
        self.assertEqual(exit_context.exception.code, NagiosExitCodes.WARNING)
        volume.delete()

    @mock_ec2
    def test_a_volume_without_a_mandatory_warning_tag_but_with_all_critical_tags_must_report_warning_state_if_instance_resources_is_set(self):
        """
        If no instance resource is available and the test should only check for instance tags than OK needs to be
        returned
        :return:
        """
        conn = boto.connect_ec2('key', 'secret')
        volume = conn.create_volume(80, "us-east-1a")
        conn.create_tags([volume.id], {"name": "unknown", "criticaltag": "VeryUsefullTagValue"})

        test_arguments = ["application_title.py","--region", "ALL", "--warning", "warningtag", "--critical",
                          "criticaltag", "--resource", "instance", "--check", "awstagscheck"]
        nagios_cli = NagiosCheckCli(test_arguments)
        with self.assertRaises(SystemExit) as exit_context:
            nagios_cli.process_arguments()
            nagios_cli.execute()
        self.assertEqual(exit_context.exception.code, NagiosExitCodes.OK)
        volume.delete()


    @mock_ec2
    def test_invalid_resource_is_set(self):
        """
        Only certain resources can be passed to the check, if an invalid resource is passed a NagiosCheckOptionError
        needs to be raised
        :return:
        """
        options = {"resource":"BoguSResource"}
        warning = "warningtag1,warningtag2"
        critical = "criticalTag"
        check = AWSTagCheck(None, warning, critical, options)

        self.assertRaises(NagiosCheckOptionError,check.run)

    @mock_ec2
    def test_an_instance_without_a_mandatory_critical_tag_must_report_critical_state(self):
        conn = boto.connect_ec2('key', 'secret')
        reservation = conn.run_instances('ami-748e2903')
        instance = reservation.instances[0]
        conn.create_tags([instance.id], {"name": "unknown"})

        test_arguments = ["application_title.py","--region", "ALL", "--critical",
                          "criticaltag", "--check", "awstagscheck"]
        nagios_cli = NagiosCheckCli(test_arguments)
        with self.assertRaises(SystemExit) as exit_context:
            nagios_cli.process_arguments()
            nagios_cli.execute()
        self.assertEqual(exit_context.exception.code, NagiosExitCodes.CRITICAL)
        conn.terminate_instances(instance.id)

    @mock_ec2
    def test_an_instance_with_a_mandatory_critical_tag_must_report_OK_state(self):
        conn = boto.connect_ec2('key', 'secret')
        reservation = conn.run_instances('ami-748e2903')
        instance = reservation.instances[0]
        conn.create_tags([instance.id], {"name": "unknown"})

        test_arguments = ["application_title.py","--region", "ALL", "--critical",
                          "name", "--check", "awstagscheck"]
        nagios_cli = NagiosCheckCli(test_arguments)
        with self.assertRaises(SystemExit) as exit_context:
            nagios_cli.process_arguments()
            nagios_cli.execute()
        self.assertEqual(exit_context.exception.code, NagiosExitCodes.OK)
        conn.terminate_instances(instance.id)

    @mock_ec2
    def test_an_instance_with_missing_mandatory_critical_tag_must_report_CRITICAL_state_eu_region(self):
        conn_eu = ec2.connect_to_region('eu-west-1')
        reservation_eu = conn_eu.run_instances('ami-748e2903')
        instance_eu = reservation_eu.instances[0]
        conn_eu.create_tags([instance_eu.id], {"Name": "unknown"})

        test_arguments = ["application_title.py","--region", "eu-west-1", "--critical",
                          "name", "--check", "awstagscheck"]
        nagios_cli = NagiosCheckCli(test_arguments)
        with self.assertRaises(SystemExit) as exit_context:
            nagios_cli.process_arguments()
            nagios_cli.execute()
        self.assertEqual(exit_context.exception.code, NagiosExitCodes.CRITICAL)
        conn_eu.terminate_instances(instance_eu.id)

    @mock_ec2
    def test_an_instance_with_missing_mandatory_critical_tag_must_report_CRITICAL_state_us_region(self):
        conn_us = ec2.connect_to_region('us-west-1')
        reservation_us = conn_us.run_instances('ami-748e2903')
        instance_us = reservation_us.instances[0]
        conn_us.create_tags([instance_us.id], {"Name": "unknown"})

        test_arguments = ["application_title.py","--region", "us-west-1", "--critical",
                          "name", "--check", "awstagscheck"]
        nagios_cli = NagiosCheckCli(test_arguments)
        with self.assertRaises(SystemExit) as exit_context:
            nagios_cli.process_arguments()
            nagios_cli.execute()
        self.assertEqual(exit_context.exception.code, NagiosExitCodes.CRITICAL)
        conn_us.terminate_instances(instance_us.id)

    @mock_ec2
    def test_an_instance_with_missing_mandatory_critical_tag_must_report_CRITICAL_state_multi_region_1(self):
        conn_us = ec2.connect_to_region('us-east-1')
        reservation_us = conn_us.run_instances('ami-748e2903')
        instance_us = reservation_us.instances[0]
        conn_us.create_tags([instance_us.id], {"name": "unknown"})
        conn_eu = ec2.connect_to_region('eu-west-1')
        reservation_eu = conn_eu.run_instances('ami-748e2903')
        instance_eu = reservation_eu.instances[0]
        conn_eu.create_tags([instance_eu.id], {"name2": "unknown"})

        test_arguments = ["application_title.py","--region", "ALL", "--critical",
                          "name", "--check", "awstagscheck"]
        nagios_cli = NagiosCheckCli(test_arguments)
        with self.assertRaises(SystemExit) as exit_context:
            nagios_cli.process_arguments()
            nagios_cli.execute()
        self.assertEqual(exit_context.exception.code, NagiosExitCodes.CRITICAL)
        conn_us.terminate_instances(instance_us.id)
        conn_eu.terminate_instances(instance_eu.id)

    @mock_ec2
    def test_an_instance_with_missing_mandatory_critical_tag_must_report_CRITICAL_state_multi_region_1(self):
        conn_us = ec2.connect_to_region('us-east-1')
        reservation_us = conn_us.run_instances('ami-748e2903')
        instance_us = reservation_us.instances[0]
        conn_us.create_tags([instance_us.id], {"name2": "unknown"})
        conn_eu = ec2.connect_to_region('eu-west-1')
        reservation_eu = conn_eu.run_instances('ami-748e2903')
        instance_eu = reservation_eu.instances[0]
        conn_eu.create_tags([instance_eu.id], {"name": "unknown"})

        test_arguments = ["application_title.py","--region", "ALL", "--critical",
                          "name", "--check", "awstagscheck"]
        nagios_cli = NagiosCheckCli(test_arguments)
        with self.assertRaises(SystemExit) as exit_context:
            nagios_cli.process_arguments()
            nagios_cli.execute()
        self.assertEqual(exit_context.exception.code, NagiosExitCodes.CRITICAL)
        conn_us.terminate_instances(instance_us.id)
        conn_eu.terminate_instances(instance_eu.id)