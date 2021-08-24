# Executing JunOS scripts with command-line arguments

The document demonstrates how to execute the command `./run.py -l debug -p /var/run/my.pid` in JunOS context: `op` and `extension` scripts to be specific

## JET scripts

1) If arguments provided is similar to  bash arguments `-l debug -p /var/run/my.pid`

    ```python
    Configuration:
    set system extensions extension-service application file run.py arguments "-l debug --pid-file /var/run/my.pid"
    set system scripts language python
    
    JET script:
    import argparse
    
    if __name__ == "__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument("-l", "--logging", help="Set logging level")
        parser.add_argument("-p", "--pid-file", help="Specify the location of the pidfile")
        args, unknown = parser.parse_known_args()
        print("Logging level: " + args.logging)
        print("PID File: " + args.pid_file)
    
    Running extension service:
    root@R1_re0> request extension-service start run.py
    Extension-service application 'run.py' started with PID: 33190
    Logging level: debug
    PID File: /var/run/my.pid
    ```
    
2) If arguments are provided as a dictionary `{"logging": "debug", "pid_file": "/var/run/my.pid"}`

    ```python
    Configuration:
    set system extensions extension-service application file run.py arguments "{\"logging\": \"debug\", \"pid_file\": \"/var/run/pid\"}"
    set system scripts language python
    
    JET script:
    import argparse
    import sys
    import json
    
    if __name__ == "__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument("-l", "--logging", help="Set logging level")
        parser.add_argument("-p", "--pid-file", help="Specify the location of the pidfile")
        args = json.loads("".join(sys.argv[1:]))
        print("Logging level: " + args["logging"])
        print("PID File: " + args["pid_file"])
    
    Running extension service:
    root@choc-qfx-a> request extension-service start run.py
    Extension-service application 'run.py' started with PID: 92998
    Logging level: debug
    PID File: /var/run/my.pid
    ```

## Op Script

1) To run the op script without configuring the arguments

    ```python
    Configuration:
    set system scripts op allow-url-for-python
    set system scripts language python
    
    OP script:
    root@R1_re0:/var/db/scripts/op # cat run.py
    import argparse
    
    if __name__ == "__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument("-l", "--logging", help="Set logging level")
        parser.add_argument("-p", "--pid-file", help="Specify the location of the pidfile")
        args, unknown = parser.parse_known_args()
        print(args)
        print("Logging level: " + args.logging)
        print("PID File: " + args.pid_file)
    
    Running the op script:
    root@R1_re0> op url /var/db/scripts/op/run.py -l debug -p /var/run/my.pid
    Namespace(logging='debug', pid_file='/var/run/my.pid')
    Logging level: debug
    ```