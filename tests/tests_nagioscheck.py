__author__ = 'pvbouwel'

import unittest
from awschecks.nagioscheck import NagiosExitCodes, NagiosCheck
from testfixtures import LogCapture
from awschecks.nagioscheckscli import NagiosCheckCli
import logging


class NagiosCheckTests(unittest.TestCase):
    def setUp(self):
        class TrivialNagiosCheckImplementation(NagiosCheck):
            def __init__(self):
                super(TrivialNagiosCheckImplementation, self).__init__()

            def run(self):
                pass

            def print_usage(self):
                pass

        self.nagios_check = TrivialNagiosCheckImplementation()

    def test_a_single_critical_gives_critical_state(self):
        nc = self.nagios_check
        nc.criticals.append('This is a critical message')
        nc.update_state()
        self.assertEqual(nc.state, NagiosExitCodes.CRITICAL)

    def test_a_critical_and_a_warning_gives_critical_state(self):
        nc = self.nagios_check
        nc.criticals.append('This is a critical message')
        nc.warnings.append('This is a warning')
        nc.update_state()
        self.assertEqual(nc.state, NagiosExitCodes.CRITICAL)

    def test_a_single_OK_gives_OK_state(self):
        nc = self.nagios_check
        nc.OKs.append('This is an OK message')
        nc.update_state()
        self.assertEqual(nc.state, NagiosExitCodes.OK)

    def test_a_single_warning_gives_warning_state(self):
        nc = self.nagios_check
        nc.warnings.append('This is a warning message')
        nc.update_state()
        self.assertEqual(nc.state, NagiosExitCodes.WARNING)

    def test_if_exit_code_is_correctly_used_for_unknown(self):
        nc = self.nagios_check
        nc.unknowns.append('This is an unknown message')
        with self.assertRaises(SystemExit) as exit_context:
            nc.report()
        self.assertEqual(exit_context.exception.code, NagiosExitCodes.UNKNOWN)

    def test_performance_data_from_single_OK(self):
        nc = self.nagios_check
        nc.OKs.append('This is an OK message')
        with LogCapture(level=logging.INFO) as l:
            with self.assertRaises(SystemExit):
                nc.report()
        l.check(('awschecks.nagioscheck', 'INFO', 'State is OK'),
                ('awschecks.nagioscheck', 'INFO', '|unknowns=0, OKs=1, criticals=0, warnings=0'))

    def test_an_implementation_of_nagioscheck_must_implement_the_run_method(self):
        class BadNagiosCheckImplementation(NagiosCheck):
            def __init__(self):
                super(BadNagiosCheckImplementation, self).__init__()
        with self.assertRaises(TypeError) as error:
            bad_nagios_check_implementation = BadNagiosCheckImplementation()

        self.assertTrue(error.exception.message.startswith("Can't instantiate abstract class"))

    def test_unknown_arguments_format2_should_be_handled_as_options_for_the_check(self):
        test_arguments = ["application_title.py","--region", "ALL", "--warning", "1", "--critical", "2",
                          "--check", "awstagscheck", "--extra-option", "test", "--extra-option2=test2" ]
        nagios_cli = NagiosCheckCli(test_arguments)
        nagios_cli.process_arguments()
        expected_options = {"extra-option": "test", "extra-option2": "test2"}
        self.assertEqual(expected_options, nagios_cli.options)