#!/usr/bin/env python

"""Test script for JunosCommits class."""

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
    # import the JunosCommits class from <class directory>/junos_commits.py
    from junos_commits import JunosCommits

except ImportError as err:
    print '* * * Error importing required modules! * * *'
    raise err


######################################################################

def main():
    """Test class JunosCommits."""
    host = 'vsrx1'
    filename = 'vsrx1.commit'
    max_commits = 4
    user = None
    password = None

    gen_file = False if filename is None else True

    jc = JunosCommits(host, gen_file, user, password, max_commits)
    try:
        jc.run()
    except Exception as err:
        print str(err)
        sys.exit(1)

    pprint(jc.commits)
    print "Temporary file (if created) is %s" % jc.filespec


######################################################################

if __name__ == '__main__':
    main()
