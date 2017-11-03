# findDuplicateIp

Supported Python version: 3.6.2.

Purpose of this application is to search for potential duplicate IP addressing within the POC lab environment for Juniper's POC lab and report
there location via physical interfaces on infrastructure TORs.  It is generic enough to be potentially be extended to other environments.

## Assumptions
- Your network is made up of MX, EX and/or QFX devices.  
- You are using IRBs and bridge domains on your gateway MX.
- You are using IPv4 within your network.  IPv6 is not supported.
- You have installed Python 3.6.2.

## Install

You can choose to run this via Docker or natively on your computer within a virtual environment.

### Docker

- Install [Docker](https://www.docker.com/products/overview).
- Install Git (https://git-scm.com/downloads)
- After cloning the repo, and going through the `Setup` section below, build the container:

        $ cd findDuplicateIp
        $ docker build -f Dockerfile -t fdip .

### Virtual Environment

- Install [virtualenv](https://virtualenv.pypa.io/en/stable/installation/).
- Install Git (https://git-scm.com/downloads)        
- After cloning the repo, create a virtual environment.

        $ cd findDuplicateIp
        $ virtualenv env3 -p python3
        $ source env3/bin/activate
        $ pip install -r requirements.txt

## Setup
- Customize the `RouteTable: args: table:` value within `data/op_table_views.yml` for your environment.

    ```yaml
    RouteTable:
      rpc: get-route-information
      args:
        table: <my-main-table.inet.0>
    ```
    
    The argument here supports a topology with a custom VR as its main table. Enter your VR's custom table name, 
     or just the default table name `inet.0` for IPv4.
    
## Run

### Docker
- Simply run the container with:

        $ cd findDuplicateIp
        $ docker run -it -v $PWD/logs:/fdip/logs fdip <gateway> -u <username> --vendor

### Natively
- Make sure your virtual environment is running:

        $ cd findDuplicateIp
        $ source env3/bin/activate
        
- Run the `main.py` with arguments:

        $ python main.py <gateway> -u <username>  --vendor

### Program Arguments
- Minimum arguments needed to run the application:

        $ python main.py <gateway> -u <username>
        
- Show help menu:

        $ python main.py -h
        
- Add vendor MAC resolution via Wireshark's OUI database: `--vendor`
- Update Wireshark's OUI database file (`data/manuf`) before scan:

        $ python main.py <gateway> -u <username> --vendor --update_vendor

- Adjust PyEZ's Device connect timeout value: `-connect_timeout <value>`
- Adjust the file path on the gateway router from which you are pulling the duplicate IP addressing log file: `--router_log_path <my/custom/path>`
- Change the default log filename which the application downloads from the router: `-f <filename>`


## Logging

Logging output is dumped into the `logs/` directory.  You can adjust the verbosity of the output by editing the `conf/logging.yml` file.


## Contributors

- Matt Mellin <mmellin@juniper.net>
