__author__ = 'pvbouwel'

import unittest
from moto import mock_ec2
import boto


from awschecks.awscheckscli import CheckAwsTagsCli


class RegionValidationTests(unittest.TestCase):
    def test_a_valid_region_should_be_returned_in_a_list(self):
        cli = CheckAwsTagsCli(["title"])
        result = cli.get_validated_region("eu-west-1")
        expected_result = ["eu-west-1"]
        self.assertEqual(result, expected_result)

    def test_ALL_must_return_multiple_regions_in_a_list(self):
        cli = CheckAwsTagsCli(["title"])
        result = cli.get_validated_region("ALL")
        #Assume that AWS will always have eu-west-1 and us-west-1 and that it will always have more than 5 regions
        self.assertTrue(isinstance(result,list) and len(result)>=5 and "eu-west-1" in result and "us-west-1" in result)

    def test_invalid_region_must_raise_value_error(self):
        cli = CheckAwsTagsCli(["title"])
        self.assertRaises(ValueError, cli.get_validated_region,"south-pole-1")


class TaggingTests(unittest.TestCase):
    @mock_ec2
    def test_a_volume_without_a_mandatory_tag_must_raise_an_alert(self):
        conn = boto.connect_ec2('key', 'secret')
        volume = conn.create_volume(80, "us-east-1a")

        all_volumes = conn.get_all_volumes()
        self.assertTrue(len(all_volumes) == 1 and all_volumes[0].size == 80 and all_volumes[0].zone == "us-east-1a")
        volume = all_volumes[0]
        conn.create_tags([volume.id], {"name": "unknown"})
        all_volumes2 = boto.connect_ec2('the_key', 'the_secret').get_all_volumes()
        volume2 = all_volumes2[0]

        volume.delete()

        self.assertTrue(len(conn.get_all_volumes()) == 0)