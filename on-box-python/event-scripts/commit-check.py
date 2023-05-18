"""
This sample script will run after UI_COMMIT_COMPLETED event, then get the latest commit and check how the commit is applied via cli, netconf of other user. the custom log generated could be received by log server for further usage.  

To prepare the script do as follow: 
 * Generate SHA256 checksum of the script:
   $ sha256sum commit-check.py

 * Load the following configs on the box:
   # set system scripts language python3
   # set event-options policy noc-commit-check events ui_commit_completed
   # set event-options policy noc-commit-check then event-script commit-check.py
   # set event-options event-script file commit-check.py python-script-user <USER>
   # set event-options event-script file commit-check.py checksum sha-256 <SHA256-CHECKSUM>

 * Copy the commit-check.py script in '/var/db/scripts/event/' folder of the junos device
 * For testing the script, run the following command: 
   % logger -e UI_COMMIT_COMPLETED
"""

import jcs
from jnpr.junos import Device
from lxml import etree

def main():
    jdev = Device()

    # Opens a connection
    jdev.open()

    # Get show system storage
    root = jdev.rpc.get_commit_information()
    #rsp_str = etree.tostring(rsp).decode('utf-8')    # Convert the response object to a string

    latest_commit = commit_history = root.find(".//commit-history[sequence-number='0']")
    client_elem = latest_commit.find('client')
    user_elem = latest_commit.find('user')
    
    try:
        comment_elem = latest_commit.find('comment')
        if ('commit confirmed, rollback in' in etree.tostring(comment_elem).decode('utf-8')):
            # We are in `commit confirmed` status and no need to check for cli/netconf.
            if (DEBUG):
                jcs.syslog('external.warning', " commit-check: State is in commit confirmed, no need for cli/ansible-noc checks ")
            return
    except:
        pass

    # Debug
    # Convert the response object to a string
    # latest_commit_str = etree.tostring(latest_commit).decode('utf-8')
    # client_elem_str = etree.tostring(client_elem).decode('utf-8')
    # comment_elem_str = etree.tostring(comment_elem).decode('utf-8')
    # jcs.syslog('external.warning', latest_commit_str)
    # jcs.syslog('external.warning', client_elem_str)
    # jcs.syslog('external.warning', comment_elem_str)

    #
    # cli: commit from command prompt
    # netconf: commit from ansible-noc
    # other: commit is rollbacked
    #
    if (client_elem.text == 'cli'):
        jcs.syslog('external.warning', f" commit-check: {user_elem.text} commited via cli")
    elif (client_elem.text == 'netconf'):
        jcs.syslog('external.warning', " commit-check: commited via netconf")        
    elif (client_elem.text == 'other'):
        jcs.syslog('external.warning', " commit-check: rollback via other user")

if __name__ == '__main__':
    main()
