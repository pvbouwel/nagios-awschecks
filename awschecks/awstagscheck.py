__author__ = 'pvbouwel'

from nagioscheck import NagiosCheck
from nagioscheck import NagiosCheckThresholdError
from nagioscheck import NagiosCheckOptionError


class AWSTagCheck(NagiosCheck):
    possible_resources = ['instance', 'volume', 'snapshot']
    warning_tags = []
    critical_tags = []
    resources_to_check = []

    def __init__(self, connection, warning, critical, options):
        """
        The constructor for an AWSTagCheck

        :param connection: An EC2_connection
        :param warning: A list of mandatory tags that will result in a warning if not present
        :param critical: A list of mandatory tags that will result in a critical if not present
        :param options: An optional list with options (e.g. can contain credentials)
        :return: void
        """
        super(AWSTagCheck, self).__init__(connection, warning, critical, options)

    def run(self):
        """
        Implements the logic behind the check
        :return:
        """

        self.process_passed_thresholds()
        self.check_options()
        region_name = self.connection.region.name

        #If volumes are to be checked
        if 'volume' in self.resources_to_check:
            all_volumes = self.connection.get_all_volumes()
            for volume in all_volumes:
                self.check_tags(volume.tags, volume.id, "Volume", region_name)

        if 'snapshot' in self.resources_to_check:
            all_snapshots = self.connection.get_all_snapshots(owner='self')
            for snapshot in all_snapshots:
                self.check_tags(snapshot.tags, snapshot.id, "Snapshot", region_name)

        if 'instance' in self.resources_to_check:
            #Currently get_only_instances is used to return all instances.  In future boto releases this might change.
            #get_all_instances currently returns reservations but in future might return instances
            # More info at: http://boto.readthedocs.org/en/latest/ref/ec2.html#module-boto.ec2.connection
            all_instances = self.connection.get_only_instances()
            for instance in all_instances:
                self.check_tags(instance.tags, instance.id, "Instance", region_name)

    def check_tags(self, present_tags, resource_id, resource_type, region):
        """
        Verifies whether the tags present on a resource are good enough.  It sets the check results (warnings, criticals
        and OKs).

        :param present_tags: The tags that are present on the resource
        :param resource_id:  The resource ID of which the tags are checked
        :param resource_type: The resource type of which the tags are checked
        :return:
        """
        resource_ok = True
        for critical_tag in self.critical_tags:
            if not critical_tag in present_tags:
                self.criticals.append("CRITICAL: " + resource_type + " " + resource_id + "(" + region + ") is missing "
                                      "tag " + critical_tag)
                resource_ok = False

        for warning_tag in self.warning_tags:
            if not warning_tag in present_tags:
                self.warnings.append("WARNING: " + resource_type + " " + resource_id + "(" + region + ") is missing "
                                     "tag " + warning_tag)
                resource_ok = False

        if resource_ok:
            self.OKs.append("OK: " + resource_type + " " + resource_id)

    def process_passed_thresholds(self):
        """
        Set the warning_tags and critical_tags lists to have appropriate content.  Meaning if nothing is passed an
        empty list and if a comma-separated string is passed it should be a list with the comma separated tags .
        :return:
        """
        if self.warning is None:
            self.warning_tags = []
        else:
            self.check_is_string(self.warning)
            self.warning_tags = self.warning.split(',')
        if self.critical is None:
            self.critical_tags = []
        else:
            self.check_is_string(self.critical)
            self.critical_tags = self.critical.split(',')

    def check_options(self):
        """
        Check all options that can be passed
        :return:
        """
        self.resources_to_check = self.get_validated_resources_to_check()

    def get_validated_resources_to_check(self):
        """
        This method verifies whether the string that is passed as a comma separated list of resources contains valid
        resource types.  It will return a list of valid resources.  Valid means that this check knows how to test them.

        :return: a list of resources that are to be checked
        """
        if 'resource' in self.options.keys():
            input_resource = self.options['resource']
        else:
            self.log.debug("No resource passed as argument so all resources will be validated.")
            return self.possible_resources

        if not isinstance(input_resource, str):
            err_message = "If a resource is passed as option, it should be a comma-separated string! Received: " \
                          + type(input_resource)
            raise NagiosCheckOptionError(err_message)

        if input_resource.upper() == "ALL":
            return self.possible_resources

        possible_resources_list = []
        input_resources = input_resource.split(',')
        for ir in input_resources:
            if ir in self.possible_resources:
                possible_resources_list.append(ir)
            else:
                raise NagiosCheckOptionError("Unknown resource type passed as resource " + ir)

        return possible_resources_list

    @staticmethod
    def check_is_string(received_object):
        if isinstance(received_object, str):
            return True
        else:
            err_message = "Warning and critical threshold should be of type string.  Received " + \
                          str(type(received_object))
            raise NagiosCheckThresholdError(err_message)

    def print_usage(self):
        usage_info = "-- Usage information for AWSTagCheck --\n"
        usage_info += "This check is initiated with --check=awstagscheck and will report missing tags\n"
        usage_info += "--- arguments --- \n\n"
        usage_info += "warning is a list containing comma-separated tags that will result in a warning when missing.\n"
        usage_info += "critical is a list containing comma-separated tags that will result in a critical when missing."\
                      "\n"
        usage_info += "resource is a AWS resource-type that needs to be checked, by default all will be checked.\n "
        usage_info += "         If this option is used only the resource of the mentioned type will be checked."
        usage_info += "         A commaseparated list can be used to take multiple. ALL can be passed to check all "
        usage_info += "         supported resource types (default behavior)."
        usage_info += "         Possible values:"
        for resource in self.possible_resources:
            usage_info += "           - " + resource
        usage_info += "\n"
        print(usage_info)
