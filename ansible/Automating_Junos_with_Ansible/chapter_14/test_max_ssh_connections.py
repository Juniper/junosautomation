#!/usr/bin/env python
"""Query devices for maximum allowed SSH connection-limit and rate-limit."""

import re
import sys
from jnpr.junos import Device
from jnpr.junos.exception import ConfigLoadError
from jnpr.junos.utils.config import Config
from jnpr.junos.utils.start_shell import StartShell
from pprint import pprint


######################################################################

class MaxSSHConnections(object):
    """Class to query devices or maximum connection-limit setting."""

    def __init__(self, device, **kwargs):
        """Initialize instance variables."""
        self.dev = Device(host=device, normalize=True)

        self.desired_connection_limit = kwargs.get('connection_limit', 15)
        self.desired_rate_limit = kwargs.get('rate_limit', 10)
        self.test_value = kwargs.get('test_value', 0)

        self.results = {'host': device,
                        'connection_max': 0,
                        'rate_max': 0,
                        'connection_limit': 0,
                        'rate_limit': 0,
                        'exception_message': '',
                        'shell_results': [],
                        'warnings': []
                        }

    # ------------------------- #

    def get_max_connections(self):
        """Use shell commands to find maximum allowed connection-limit."""
        # the list of commands that will:
        #  - exit from the command shell to the Junos CLI
        #  - enter configuration mode
        #  - issue the command "set system services ssh connection-limit ?",
        #      which will return help information we want to process
        #  - exit configuration mode
        shell_commands = [
            {'command': 'exit', 'prompt': '> ', 'max': False},
            {'command': 'configure', 'prompt': '# ', 'max': False},
            {'command': 'set system services ssh connection-limit ?',
             'prompt': '# ', 'max': True},
            {'command': 'exit', 'prompt': '> ', 'max': False}
        ]

        # open a command shell on the device
        shell = StartShell(self.dev)
        shell.open()

        # iterate over the list of commands, capturing the output from
        #   the command in whose results we are interested ('max' = True)
        max_msg = None
        for shellcmd in shell_commands:
            shellout = shell.run(shellcmd['command'], shellcmd['prompt'])
            self.results['shell_results'].append(shellout)

            if shellout[0] is False:
                msg = 'Shell command "%s" did not complete as expected: %s' \
                    % (shellcmd['command'], shellout[1])
                raise RuntimeError(msg)

            if shellcmd['max']:
                max_msg = shellout[1]

        shell.close()

        # process the command output to find the max allowed value
        if max_msg is not None:
            max_arr = max_msg.splitlines()
            regex = r'connection-limit[^\(\[]*[\(\[]\d+\.\.(\d+)'
            max_str = None
            for line in max_arr:
                m = re.search(regex, line, flags=re.IGNORECASE)
                if m is not None:
                    max_str = m.group(1)
                    break

            if max_str is not None:
                reported_max = int(max_str)
                self.results['connection_max'] = reported_max
                if reported_max < self.desired_connection_limit:
                    self.results['connection_limit'] = reported_max
                else:
                    self.results['connection_limit'] = \
                        self.desired_connection_limit
            else:
                msg = 'Regex match expected but not found in command results'
                raise ValueError(msg)
        else:
            msg = 'Missing expected results from shell commands.'
            raise ValueError(msg)

    # ------------------------- #

    def get_max_rate(self):
        """Set an invalid value for rate-limit and process the exception."""
        # configuration object for Junos device
        cfg = Config(self.dev)

        # make sure no config change is pending before our set command
        diff = cfg.diff()
        if diff is not None:
            msg = 'Uncommitted change found: %s' % str(diff)
            raise RuntimeError(msg)

        # try to set a invalid (too large) value for rate-limit
        set_cmd = 'set system services ssh rate-limit ' + str(self.test_value)
        try:
            cfg.load(set_cmd, format='set')
            # Config load should raise exception if the test value is invalid.
            # If we got here, it means the device accepted the (apparently
            #   valid) rate-limit, so roll back the change and assume the
            #   test value is the maximum allowed rate limit
            cfg.rollback()
            msg = 'Test configuration loaded without error, actual max '
            msg += 'rate limit may be higher than the test value '
            msg += '%s.' % str(self.test_value)
            self.results['warnings'].append(msg)
            self.results['rate_max'] = self.test_value
            if self.test_value < self.desired_rate_limit:
                self.results['rate_limit'] = self.test_value
            else:
                self.results['rate_limit'] = self.desired_rate_limit
        except ConfigLoadError as err:
            self.results['exception_message'] = err.message
            # catch the expected ConfigLoadError from the invalid rate-limit
            match = re.search(r'\(\d+\.\.(\d+)\)', err.message)
            if match is not None:
                max_str = int(match.group(1))
                reported_max = int(max_str)
                self.results['rate_max'] = reported_max
                if reported_max < self.desired_rate_limit:
                    self.results['rate_limit'] = reported_max
                else:
                    self.results['rate_limit'] = self.desired_rate_limit
            else:
                msg = 'Regex match expected but not found in caught '
                msg += 'exception: %s' % str(err)
                raise ValueError(msg)

    # ------------------------- #

    def run(self):
        """Run the device test and return result."""
        # open a PyEZ connection to the device
        self.dev.open()

        # get max connection limit (first approach)
        self.get_max_connections()

        # get max rate limit (second approach)
        self.get_max_rate()

        # close device connection
        self.dev.close()


######################################################################

def main():
    """Test the MaxSSHConnections class."""
    desired_connections = 15
    desired_rate = 10
    test_value = 0
    device = 'aragorn'

    find_max = MaxSSHConnections(device, test_value=test_value,
                                 rate_limit=desired_rate,
                                 connection_limit=desired_connections)
    try:
        find_max.run()
    except Exception as err:
        print(str(err))
        sys.exit(1)

    pprint(find_max.results)


######################################################################

if __name__ == '__main__':
    main()
