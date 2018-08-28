#!/usr/bin/env python
"""Query devices for maximum allowed SSH connection-limit and rate-limit."""
from ansible.module_utils.basic import AnsibleModule
module_import_error = False
try:
    import os
    import sys

    # determine fully qualified path to our classes directory
    # based on the relative path ./classes (from where the playbook lives)
    class_path = os.path.realpath(os.path.join(os.path.realpath('.'),
                                  'classes'))
    # add our class path to the Python system path
    if class_path not in sys.path:
        sys.path.insert(0, class_path)
    # import the MaxSSHConnections class from
    #   <class directory>/max_ssh_connections_2.py
    from max_ssh_connections_2 import MaxSSHConnections
except ImportError as err:
    module_import_error = True
    module_msg = 'Error importing required modules: %s' % str(err)


######################################################################

def main():
    """Query devices for maximum SSH connection-limit and rate-limit."""
    # define arguments from Ansible
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(required=True),
            test_value=dict(required=False, type='int', default=0),
            rate_limit=dict(required=False, type='int', default=10),
            connection_limit=dict(required=False, type='int', default=15)
            )
        )

    # early exit if required modules failed to import
    if module_import_error:
        module.fail_json(msg=module_msg)

    # copy playbook arguments into local variables
    host = module.params['host']
    test_value = module.params['test_value']
    rate_limit = module.params['rate_limit']
    connection_limit = module.params['connection_limit']

    # instantiate MaxSSHConnections and run
    find_max = MaxSSHConnections(host, test_value=test_value,
                                 rate_limit=rate_limit,
                                 connection_limit=connection_limit)
    try:
        find_max.run()
    except Exception as err:
        module.fail_json(msg=str(err), results=find_max.results)

    module.exit_json(changed=False, results=find_max.results,
                     rate_limit=find_max.results['rate_limit'],
                     connection_limit=find_max.results['connection_limit'])


######################################################################

if __name__ == '__main__':
    main()
