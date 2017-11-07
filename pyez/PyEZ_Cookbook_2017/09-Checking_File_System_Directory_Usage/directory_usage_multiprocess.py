# Copyright 2017, Juniper Networks Pvt Ltd.
# All rights reserved.
#!/usr/bin/python3

from jnpr.junos import Device                                  # (1)
from jnpr.junos.utils.fs import FS
from jnpr.junos.exception import *
import multiprocessing
import time

NUM_PROCESSES = 8                                              # (2)
USER = "lab"
PASSWD = "lab123"
DEVICES = [
    "10.254.0.31",
    "10.254.0.34",
    "10.254.0.35",
    "10.254.0.37",
    "10.254.0.38",
    "10.254.0.41",
    "10.254.0.42",
]
DIRECTORY = "/var/tmp/"

def check_directory_usage(host):                               # (3)
    try:
        with Device(host=host, user=USER, password=PASSWD) as dev:
            fs = FS(dev)                                       # (4)
            print("Checking %s: " % host, end="")
            print(fs.directory_usage(DIRECTORY))               # (5)
    except ConnectRefusedError:                                # (6)
        print("%s: Error - Device connection refused!" % host)
    except ConnectTimeoutError:
        print("%s: Error - Device connection timed out!" % host)
    except ConnectAuthError:
        print("%s: Error - Authentication failure!" % host)

def main():                                                    # (7)
    time_start = time.time()
    with multiprocessing.Pool(processes=NUM_PROCESSES) as process_pool:  # (8)
        process_pool.map(check_directory_usage, DEVICES)       # (9)
        process_pool.close()                                   # (10)
        process_pool.join()
    print("Finished in %f sec." % (time.time() - time_start))  # (11)

if __name__ == "__main__":                                     # (12)
    main()
