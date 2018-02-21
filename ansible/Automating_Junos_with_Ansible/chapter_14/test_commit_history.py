#!/usr/bin/env python

import sys
import tempfile
from jnpr.junos import Device
from pprint import pprint


######################################################################

class JunosCommits(object):
    """Get commit history from a Junos device."""

    def __init__(self, host, gen_file, username, password, max_commits):
        self.host = host
        self.generate_file = gen_file
        self.username = username
        self.password = password
        self.max_commits = max_commits

        # instantiate a PyEZ Device to communicate with the Junos device
        self.dev = Device(host=self.host,
                          user=self.username,
                          passwd=self.password,
                          normalize=True)

        # list to store commit history
        self.commits = []

        # number of commits returned by device
        self.num_commits = 0

        # path+filename and file descriptor for output tempfile
        self.filespec = ''
        self.file_descriptor = None

    # ------------------------- #

    def get_commit_history_from_device(self):
        """Get commit history from Junos device and store in list of dicts."""
        try:
            self.dev.open()
        except Exception as err:
            msg = 'Error opening connection to Junos device: %s' % str(err)
            raise Exception(msg)

        # get from device the equivalent of "show sytem commit"
        try:
            commit_info = self.dev.rpc.get_commit_information()
        except Exception as err:
            msg = 'Error getting commit history from device: %s' % str(err)
            raise Exception(msg)

        # extract all 'commit-history' elements from XML
        # put data in a list of dictionaries
        try:
            commits_xml = commit_info.findall('commit-history')
            self.num_commits = len(commits_xml)
            for commit in commits_xml:
                commit_dict = {
                    'num': commit.findtext('sequence-number'),
                    'user': commit.findtext('user'),
                    'client': commit.findtext('client'),
                    'date_time': commit.findtext('date-time'),
                    'comment': commit.findtext('log')
                }
                self.commits.append(commit_dict)

            # truncate list if a max_commits value was specified
            if (self.max_commits is not None) and \
               (self.max_commits < self.num_commits):
                del self.commits[self.max_commits:]

        except Exception as err:
            msg = 'Error processing commit history: %s' % str(err)
            raise Exception(msg)

    # ------------------------- #

    def temp_commit_history_file(self):
        """Save commit history to temporary file."""
        try:
            self.file_descriptor, self.filespec = tempfile.mkstemp()
            outfile = open(self.filespec, 'w')

            outfile.write('Device returned %s commits.\n' % self.num_commits)
            if self.max_commits is not None:
                outfile.write('Saving latest %s commits.\n'
                              % self.max_commits)
            outfile.write('\n- - - Commit History - - -\n')

            for c in self.commits:
                line = '%2s: %s by %s via %s (%s)\n' % \
                    (c['num'], c['date_time'], c['user'],
                     c['client'], c['comment'])
                outfile.write(line)

            outfile.close()

        except Exception as err:
            msg = 'Error writing to file %s: %s' % (self.filespec, str(err))
            raise Exception(msg)

    # ------------------------- #

    def run(self):
        """Process Junos device."""
        self.get_commit_history_from_device()
        if self.generate_file:
            self.temp_commit_history_file()


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
