#!/usr/bin/env python
"""Test script for MaxSSHConnections class."""

try:
    import os
    import sys
    from pprint import pprint

    # determine fully qualified path to our classes directory
    # based on the relative path ./classes (from where this program lives)
    class_path = os.path.realpath(os.path.join(os.path.realpath('.'),
                                  'classes'))
    # add our class path to the Python system path
    if class_path not in sys.path:
        sys.path.insert(0, class_path)
    # import the MaxSSHConnections class from
    #   <class directory>/max_ssh_connections_2.py
    from max_ssh_connections_2 import MaxSSHConnections
except ImportError as err:
    print('* * * Error importing required modules! * * *')
    raise


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
