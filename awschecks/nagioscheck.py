__author__ = 'pvbouwel'
import sys
import logging
import abc

__all__ = ('NagiosExitCodes', 'NagiosCheck')


class NagiosExitCodes:
    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = 3

    def __init__(self):
        pass


class NagiosCheckThresholdError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class NagiosCheckOptionError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class NagiosCheck:
    __metaclass__ = abc.ABCMeta
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    log = logging.getLogger(__name__)

    def __init__(self, connection=None, warning='', critical='', options={}):
        """
        NagiosCheck constructor takes 3 keyword arguments

        :param connection -- a boto.ec2.connection.EC2Connection
        :param warning  -- a NagiosCheck-specific string identifying warning thresholds
        :param critical -- a NagiosCheck-specific string identifying warning thresholds
        :param options  -- a dict with options specific to this check
        """
        self.warning = warning
        self.critical = critical
        self.options = options
        self.OKs = []
        self.unknowns = []
        self.warnings = []
        self.criticals = []
        self.performance_data = {}
        self.state = NagiosExitCodes.OK
        self.connection = connection

    def __add__(self, other):
        result = DummyNagiosCheck()
        result.unknowns.extend(self.unknowns)
        result.unknowns.extend(other.unknowns)
        result.warnings.extend(self.warnings)
        result.warnings.extend(other.warnings)
        result.criticals.extend(self.criticals)
        result.criticals.extend(other.criticals)
        result.OKs.extend(self.OKs)
        result.OKs.extend(other.OKs)
        result.performance_data = dict(self.performance_data.items() + other.performance_data.items())
        return result

    def update_state(self):
        """
        This will set the state of the NagiosCheck.  When there are indicators for being critical the state will be
        critical even when there are indicators for an unknown state, if something is critical the whole situation is
        considered critical.  When there are indicators for both unknown and warning we report the state unknown since
        there might be parts of the check that couldn't be determined but that should be considered critical.
        """
        if len(self.criticals) > 0:
            self.state = NagiosExitCodes.CRITICAL
        elif len(self.unknowns) > 0:
            self.state = NagiosExitCodes.UNKNOWN
        elif len(self.warnings) > 0:
            self.state = NagiosExitCodes.WARNING
        else:
            self.state = NagiosExitCodes.OK

    def report_state(self):
        """
        State for a Nagios check is reported via the exit code, therefore this call will stop execution.
        """
        self.update_state()
        sys.exit(self.state)

    def report(self):
        """
        This will first print the output and than will exit with the Nagios Exit code.
        :return:
        """
        self.print_nagios_output_string()
        self.report_state()

    def print_performance_data(self):
        """
        This method will convert a dict with performance data to the output format that Nagios expects and will then
        print it.
        :return:
        """
        perf_data = self.get_enriched_performance_data_dict()
        str_perf_data = ''
        str_perf_data += '|'
        first = True
        for key, value in perf_data.iteritems():
            if not first:
                str_perf_data += ', '
            else:
                first = False
            str_perf_data += str(key)
            str_perf_data += '='
            str_perf_data += str(value)
        self.log.info(str_perf_data)

    def get_enriched_performance_data_dict(self):
        """
        This method adds metrics on the number of messages that are in the Nagios Check state.
        :return:
        """
        perf_dict = self.performance_data
        perf_dict['OKs'] = len(self.OKs)
        perf_dict['warnings'] = len(self.warnings)
        perf_dict['criticals'] = len(self.criticals)
        perf_dict['unknowns'] = len(self.unknowns)
        return perf_dict

    def print_nagios_output_string(self):
        """
        This method translates the NagiosCheck object's state to Nagios output.  When needed this can be overwritten.
        """
        self.update_state()

        if self.state == NagiosExitCodes.OK:
            for ok_message in self.OKs:
                self.log.debug(ok_message)
            self.log.info('State is OK')
        else:
            ##First print criticals
            for error_message in self.criticals:
                self.log.error(error_message)
            ##2nd print warnings
            for warning_message in self.warnings:
                self.log.warn(warning_message)
            ##Finally print unknowns as
            for unknown_message in self.unknowns:
                self.log.warning(unknown_message)

        self.print_performance_data()

    @abc.abstractmethod
    def run(self):
        """
        The method that implements the check logic. This is a mandatory method.

        The health check needs to be performed messages need to be appended to the corresponding list
          self.OKs = []
          self.unknowns = []
          self.warnings = []
          self.criticals = []

        If performance data is calculated it can be reported by placing it in the self.performance_data dict.  The key
        will be the metric name and the value is a string that holds the metric value (in Nagios performance data value
        form)
        :return void
        """
        return

    @abc.abstractmethod
    def print_usage(self):
        """
        This method will print the print_usage information for the check. It should state how the following parameters
         should be passed:
          - warning
          - critical
          - options (show whether options are mandatory or optional)
        :return:
        """


class DummyNagiosCheck(NagiosCheck):
    def run(self):
        pass

    def print_usage(self):
        pass