__author__ = 'pvbouwel'

from nagioscheck import NagiosCheck


class AWSTagCheck(NagiosCheck):
    def __init__(self, warning, critical, options):
        """
        The constructor for an AWSTagCheck

        :param warning: A list of mandatory tags that will result in a warning if not present
        :param critical: A list of mandatory tags that will result in a critical if not present
        :param options: An optional list with options (e.g. can contain credentials)
        :return: void
        """
        super(AWSTagCheck, self).__init__(warning, critical, options)

    def run(self):
        pass

    def print_usage(self):
        pass