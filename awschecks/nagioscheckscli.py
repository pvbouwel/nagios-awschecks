__author__ = 'pvbouwel'
__doc__ = 'https://github.com/pvbouwel/nagios-awschecks'

import sys
import argparse
import logging
from boto import ec2
from nagioscheck import NagiosExitCodes
import wrapt


class NagiosCheckCli:
    args = None
    arguments_processed = False
    aws_access_key_id = None
    aws_secret_access_key = None
    check = None
    critical = ""
    log = logging.getLogger(__name__)
    options = None
    region = "eu-west-1"
    tags = None
    title = None
    unknowns = None
    version = "0.0.1"
    warning = ""
    checks = ["awstagscheck"]


    def __init__(self, cli_arguments):
        self.title = cli_arguments[0]
        real_arguments = cli_arguments[1:]
        self.parse_arguments(real_arguments)
        self.configure_logging()

    def parse_arguments(self, arguments):
        parser = argparse.ArgumentParser(description='Check whether tags are set on AWS resources.  '
                                                     'Report missing tags according to nagios conventions.')
        parser.add_argument('--region', metavar='REGION',
                            help='the region in which the resources need to be checked. "ALL" can be used to search'
                                 ' all regions.  E.g. us-east-1')
        parser.add_argument('--check', metavar='CHECK', help='The check that needs to be executed.  If no additional '
                                                             'information is provided print_usage of the check is '
                                                             'shown.  This parameter is mandatory')
        parser.add_argument('--warning', metavar='WARNING', help='A string providing the warning threshold (mandatory)')
        parser.add_argument('--critical', metavar='CRITICAL', help='A string providing the warning threshold '
                                                                   '(mandatory)')
        parser.add_argument('--verbose', '-v', action='count', help='enable verbose output (-v[v]* for more), should '
                                                                    'not be used in nagios configuration.')
        parser.add_argument('--aws_access_key_id', '-i', help='The AWS access key id to be used to authenticate.')
        parser.add_argument('--aws_secret_access_key', '-k', help='The AWS access key to be used to authenticate.')
        self.args, self.unknowns = parser.parse_known_args(arguments)

    def configure_logging(self):
        verbosity = self.args.verbose

        log_prefix = ''
        log_suffix = ''

        if verbosity > 1:
            log_prefix = '(%(lineno)s):%(funcName)s] - ' + log_prefix
        if verbosity > 0:
            log_prefix = '%(asctime)s [%(name)s] %(levelname)s ' + log_prefix

        log_format = log_prefix + '%(message)s' + log_suffix
        log_level = logging.DEBUG if verbosity >= 1 else logging.INFO

        logging.basicConfig(level=log_level, format=log_format)
        logging.getLogger('boto').setLevel(logging.CRITICAL)
        self.log.debug("Logging initialized with verbosity " + str(verbosity))

    def process_arguments(self):
        if self.arguments_processed:
            return

        self.log.debug("Processing arguments: " + str(self.args))
        self.process_credentials()
        self.process_region()
        self.process_check()
        self.process_thresholds()
        self.process_unknowns()
        self.arguments_processed = True

    def process_unknowns(self):
        """
        Unknown arguments are considered options for the launched check,  So parse them and put them in the options dict
        :return:
        """
        self.options = {}
        unknowns = self.normalize_cli_arguments(self.unknowns)
        if len(unknowns) % 2 == 1:
            raise(argparse.ArgumentError("Unknown arguments need to come in pairs.", "Make sure the passed arguments "
                                                                                     "are valid"))
        else:
            nr_elements = len(unknowns)/2
            for index in range(0, nr_elements):
                if not unknowns[2*index].startswith("--"):
                    raise(argparse.ArgumentError("Unknown arguments need to come in pairs like: '--key value'",
                                                 "Make sure the passed arguments are valid."))
                else:
                    key = unknowns[2*index][2:]
                    value = unknowns[2*index + 1]
                    self.options[key] = value

    @staticmethod
    def normalize_cli_arguments(arguments):
        normalized_arguments = []
        for argument in arguments:
            if '=' in argument:
                for element in argument.split('=', 1):
                    normalized_arguments.append(element)
            else:
                normalized_arguments.append(argument)
        return normalized_arguments

    def process_thresholds(self):
        if self.args.warning is None or self.args.critical is None:
            self.log.error("The warning and critical parameters are mandatory. Showing check print_usage information:")
            self.get_check().print_usage()
        else:
            self.warning = self.args.warning
            self.critical = self.args.critical

    def process_check(self):
        if self.args.check is None:
            self.log.fatal("The check parameter is mandatory!")
        else:
            if self.args.check in self.checks:
                self.check = self.args.check
            else:
                raise(ValueError("Invalid checkname passed as an argument, check configuration."))

    def get_validated_region(self, region_name):
        if not region_name:
            self.log.debug("No region passed as argument -> using default.")
        else:
            self.region = region_name
            self.log.debug("Region passed as argument (" + str(self.region)+").")

        available_regions = self.get_all_region_names()
        if self.region == 'ALL':
            return available_regions
        elif self.region in available_regions:
            self.log.debug("Region is a valid AWS region.")
            return [region_name]
        else:
            raise(ValueError("Invalid region passed as an argument, check configuration."))

    def process_region(self):
        try:
            self.region = self.get_validated_region(self.args.region)
        except ValueError as e:
            self.log.error(str(e))
            sys.exit(NagiosExitCodes.UNKNOWN)

    def get_all_region_names(self):
        if self.aws_access_key_id:
            regions = ec2.regions(aws_access_key_id=self.aws_access_key_id,
                                  aws_secret_access_key=self.aws_secret_access_key)
        else:
            regions = ec2.regions()

        return [region.name for region in regions]

    def process_credentials(self):
        self.log.debug("Check credentials")
        if self.args.aws_access_key_id:
            self.log.debug("aws_access_key_id is set this means a secret access key is mandatory")
            if not self.args.aws_secret_access_key:
                self.log.warn("--aws_secret_access_key is mandatory when --aws_access_key_id is used")
                self.log.warn("Verify that correct credentials are used.")
                sys.exit(NagiosExitCodes.UNKNOWN)
            else:
                self.aws_access_key_id = self.args.aws_access_key_id
                self.aws_secret_access_key = self.args.aws_secret_access_key

    def get_check(self):
        return None


if __name__ == '__main__':
    check = NagiosCheckCli(sys.argv).get_check()
    check.run()
    check.report()