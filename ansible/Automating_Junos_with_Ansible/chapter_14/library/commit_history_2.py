#!/usr/bin/env python

"""Ansible module to gather commit history from a Junos device."""

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
    # import the JunosCommits class from <class directory>/junos_commits.py
    from junos_commits import JunosCommits

except ImportError as err:
    module_import_error = True
    module_msg = 'Error importing required modules: %s' % str(err)


######################################################################

def main():
    """Query Junos device and interface with Ansible playbook."""
    # define arguments from Ansible
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(required=True),
            filename=dict(required=False, default=None),
            user=dict(required=False, default=os.getenv('USER')),
            passwd=dict(required=False, default=None, no_log=True),
            max_commits=dict(required=False, type='int', default=None)
            )
        )

    # early exit if required modules failed to import
    if module_import_error:
        module.fail_json(msg=module_msg)

    # copy playbook arguments into local variables
    host = module.params['host']
    filename = module.params['filename']
    username = module.params['user']
    password = module.params['passwd']
    max_commits = module.params['max_commits']

    # determine if module should generate output file
    gen_file = False if filename is None else True

    # instantiate JunosCommits and run
    jc = JunosCommits(host, gen_file, username, password, max_commits)
    try:
        jc.run()
        if gen_file:
            module.atomic_move(jc.filespec, filename)
    except Exception as err:
        module.fail_json(msg=str(err))

    module.exit_json(changed=False, commits=jc.commits)


######################################################################

if __name__ == '__main__':
    main()
