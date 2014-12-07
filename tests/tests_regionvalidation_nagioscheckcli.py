__author__ = 'pvbouwel'
import unittest
import mock
from awschecks.nagioscheckscli import NagiosCheckCli


class RegionValidationTests(unittest.TestCase):
    def test_a_valid_region_should_be_returned_in_a_list(self):
        cli = NagiosCheckCli(["title"])
        mock_do_nothing = mock.Mock()
        cli.process_thresholds = mock_do_nothing
        result = cli.get_validated_region("eu-west-1")
        expected_result = ["eu-west-1"]
        self.assertEqual(result, expected_result)

    def test_ALL_must_return_multiple_regions_in_a_list(self):
        cli = NagiosCheckCli(["title"])
        mock_do_nothing = mock.Mock()
        cli.process_thresholds = mock_do_nothing
        result = cli.get_validated_region("ALL")
        #Assume that AWS will always have eu-west-1 and us-west-1 and that it will always have more than 5 regions
        self.assertTrue(isinstance(result, list) and len(result) >= 5 and "eu-west-1" in result
                        and "us-west-1" in result)

    def test_invalid_region_must_raise_value_error(self):
        cli = NagiosCheckCli(["title"])
        mock_do_nothing = mock.Mock()
        cli.process_thresholds = mock_do_nothing
        self.assertRaises(ValueError, cli.get_validated_region,"south-pole-1")