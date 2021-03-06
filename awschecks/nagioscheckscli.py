__author__ = 'pvbouwel'
__doc__ = 'https://github.com/pvbouwel/nagios-awschecks'

import sys
import argparse
import logging
from boto import ec2, boto
from nagioscheck import NagiosExitCodes


class NagiosCheckCli:
    args = None
    arguments_processed = False
    aws_access_key_id = None
    aws_secret_access_key = None
    check = None
    critical = ""
    log = logging.getLogger(__name__)
    options = None
    parser = None
    region = ["eu-west-1"]
    tags = None
    title = None
    unknowns = None
    version = "0.0.2"
    warning = ""
    supported_checks = {"awstagscheck":"awschecks.AWSTagCheck"}


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
        self.parser = parser

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
        self.log.setLevel(log_level)
        self.log.debug("Logging initialized with verbosity " + str(verbosity))

    def process_arguments(self):
        if self.arguments_processed:
            return

        self.log.debug("Processing arguments: " + str(self.args))
        self.process_credentials()
        self.process_region()
        try:
            self.process_check()
        except(ValueError):
            self.log.error("Currently only " + str(self.supported_checks.keys()) + " are supported as checks.")
            sys.exit(NagiosExitCodes.UNKNOWN)

        self.process_thresholds()
        self.process_unknown_cli_arguments()
        self.arguments_processed = True

    def process_unknown_cli_arguments(self):
        """
        Unknown arguments are considered options for the launched check,  So parse them and put them in the options dict
        These should come in pairs like --optionkey optionvalue
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
        """
        This method takes a list of arguments if there are arguments in this list that are of the form key=value they
        will be splitted into key and value.  This will allow to process arguments in a homogeneous way i.e.:
        '--key=value' will be treated similar as '--key value'
        :param arguments:
        :return:
        """
        normalized_arguments = []
        for argument in arguments:
            if '=' in argument:
                for element in argument.split('=', 1):
                    normalized_arguments.append(element)
            else:
                normalized_arguments.append(argument)
        return normalized_arguments

    def process_thresholds(self):
        """
        Just sets the thresholds, the check itself is responsible for checking the values.  It can be None since this
        means the default value might be used.
        :return:
        """
        self.warning = self.args.warning
        self.critical = self.args.critical

    def process_check(self):
        if self.args.check is None:
            self.log.fatal("The check parameter is mandatory!")
            raise(ValueError("Invalid check name passed as an argument, check configuration."))
        else:
            if self.args.check.lower() in self.supported_checks.keys():
                self.check = self.supported_checks[self.args.check.lower()]
            else:
                raise(ValueError("Invalid check name passed as an argument, check configuration."))

    def process_region(self):
        try:
            self.region = self.get_validated_region(self.args.region)
        except ValueError as e:
            self.log.error(str(e))
            sys.exit(NagiosExitCodes.UNKNOWN)

    def get_validated_region(self, region_name):
        """
        Verifies whether a region is valid.
        :param region_name:
        :return:
        """
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

    def get_all_region_names(self):
        """ Get a list with all region names
        :return: list with all region names
        """
        if self.aws_access_key_id:
            regions = ec2.regions(aws_access_key_id=self.aws_access_key_id,
                                  aws_secret_access_key=self.aws_secret_access_key)
        else:
            regions = ec2.regions()

        all_regions = []
        for region in regions:
            if region.name in ["cn-north-1", "us-gov-west-1"]:
                self.log.warning("Ignoring " + region.name + " since not public to the world yet.")
                self.log.info("You can test " + region.name + " by explicitly specify the region to the regions "
                                                              "argument.")
            else:
                all_regions.append(region.name)

        return all_regions

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

    def get_connection(self,region):
        if self.args.aws_access_key_id and self.args.aws_secret_access_key:
            return ec2.connect_to_region(region, aws_access_key_id=self.args.aws_access_key_id, aws_secret_access_key=self.args.aws_secret_access_key)
        else:
            return ec2.connect_to_region(region)

    def get_check(self, region):
        """
        Get the check on a reflection-like way.  The check will be pointed to by a full module path + the class name:
        Similar to http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname
        E.g. awschecks.AWSTagCheck
        :return:
        """
        parts = self.check.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        check_class = m
        return check_class(connection=self.get_connection(region), warning=self.warning, critical=self.critical,
                           options=self.options)

    def execute(self):
        """Execute the check for each requested region"""
        aggregated_check = None
        for region_name in self.region:
            self.log.debug("Checking region " + region_name)
            check = self.get_check(region_name)
            check.run()
            if aggregated_check is None:
                aggregated_check = check
            else:
                aggregated_check += check

        aggregated_check.report()


def main():
    cli_instance = NagiosCheckCli(sys.argv)
    cli_instance.process_arguments()
    cli_instance.execute()

if __name__ == '__main__':
    main()
