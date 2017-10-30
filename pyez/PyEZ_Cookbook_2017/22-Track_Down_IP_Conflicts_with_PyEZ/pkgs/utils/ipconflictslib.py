""" Module that contains code for finding IP conflicts """
import gzip
import magic
import os
from collections import defaultdict
from contextlib import contextmanager
from multiprocessing import Pool
from functools import partial
from pathlib import Path
from pkgs.utils.log import get_logger
from pkgs.utils import manuf
from jnpr.junos import Device
from jnpr.junos.utils.scp import SCP
from jnpr.junos.exception import (ConnectAuthError, ConnectError, ConnectTimeoutError)
from jnpr.junos.factory import loadyaml


# Setup logger
logger = get_logger(__name__)

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
data_dir = os.path.join(base_dir, 'data')
log_dir = os.path.join(base_dir, 'logs')

# Create classes per table/view and add them to the global namespace
globals().update(loadyaml(os.path.join(data_dir, 'op_table_views.yml')))


@contextmanager
def connect_dut(dut, credentials, connect_timeout=None, facts=True):
    """Custom function to connect to device. Wraps PyEZ Device.open() function.

    SSH key support currently not tested.

    Args:
        dut (str): IP or hostname of a JUNOS device with which to establish an SSH session.
        credentials (dict): Contains credential information along with the mode of requested authentication.
        connect_timeout (int): PyEZ connection timeout in seconds.
        facts (bool): Allows establishing a PyEZ connection with or without 'facts' gathering.

    Returns:
        dev (obj): PyEZ object with open SSH connection to JUNOS device (dut).

    Raises:
        ConnectAuthError: If the authentication fails.
        ConnectError: If there are connectivity problems during connection establishment.

    """
    user = credentials['username']
    password = credentials['password']
    auth_mode = credentials['auth_mode']
    dev = None
    try:
        if auth_mode == 'password' and password:
            if connect_timeout:
                Device.timeout = connect_timeout
            dev = Device(host=dut, user=user, password=password, gather_facts=facts).open()
        elif auth_mode == 'ssh-key':
            dev = Device(host=dut, gather_facts=True).open()
        else:
            logger.error("Proper credentials for device login not provided.")
        logger.info('Connection Successful ({} - {}).'.format(dev.facts.get('hostname'), dut))
        yield dev

    except ConnectAuthError as e:
        logger.error("Authentication failed to {}.\n {}".format(dut, e))
        raise
    except ConnectTimeoutError as e:
        logger.error("Connection timeout to {}.\n {}".format(dut, e))
        raise
    except ConnectError as e:
        logger.error("Failed to connect to {}.\n {}".format(dut, e))
        raise
    finally:
        if dev:
            dev.close()
            logger.info("Closed connection to {}".format(dut))


def update_vendor_file(path=None):
    """Updates the Wireshark OUI text file for use with Manuf.py module.

    Args:
        path (str): Absolute path of the Wireshark MAC OUI Manuf text file.

    Returns:
        None

    """
    if not path:
        path = Path(os.path.join(data_dir, "manuf"))
    try:
        manuf.MacParser(manuf_name=path.as_posix(), update=True)
        logger.info("Update done successfully.")
    except Exception:
        raise


def determine_vendor(mac):
    """Resolve MAc OUI to hardware vendor

    Args:
        mac (str): MAC address to resolve.

    Returns:
        vendor (str): MAC addressing hardware vendor name.

    """
    v = manuf.MacParser(manuf_name=os.path.join(data_dir, 'manuf'))
    vendor = v.get_manuf(mac)
    return vendor


def create_output_structures(_scanned_systems, _seed_dict, resolve_vendor=False):
    """Creates an easily consumed data structure for use when printing program findings.

    Args:
        _scanned_systems (dict): Final output of network scan. Contains all relevant system data.
        _seed_dict (dict): Initial Mac/IP mappings.
        resolve_vendor (bool): Allows toggling of MAC OUI vendor resolution.

    Returns:
        output (obj): DefaultDict dictionary like object with all relevant findings.

    """
    output = defaultdict(lambda: defaultdict(list))
    leaves = None
    mgt_ip = None
    vendor = None
    # Build initial output dictionary
    for system_ip, system_values in _scanned_systems.items():
        try:
            leaves = system_values['leaves']
            mgt_ip = system_ip

        except KeyError:
            for parent, parent_info in system_values['parent_info'].items():
                leaves = parent_info
                mgt_ip = parent

        assert leaves is not None, "The leaves dictionary does not exist.  Cannot parse."
        for vlan_id, values in leaves.items():
            for interface, macs in values.items():
                for mac in macs:
                    dup_ip = _seed_dict['mac_to_ip_mapping'][mac]
                    if resolve_vendor:
                        vendor = determine_vendor(mac)
                    for ip in dup_ip:
                        output[vlan_id][ip].append((mac, vendor, _scanned_systems[mgt_ip]['name'], mgt_ip, interface))
    # Pad each IP in the output dictionary where a MAC was not found.
    for vlan, vlan_values in output.items():
        for ip, values in vlan_values.items():
            '''Some MACs for a given IP may not have been found, thus the number of MACs for this IP in the current
            output dictionary might not match the original number of MACs found for this IP.  We need to match up the
            lengths here and fill in blank values for the missing information.
            '''
            original_macs = _seed_dict['ip_to_mac_mapping'][ip]
            original_count = len(original_macs)
            new_count = len(values)
            # original_count should not be less than new_count
            if original_count > new_count:
                current_macs = []
                for value_tuple in values:
                    mac_address = value_tuple[0]
                    current_macs.append(mac_address)
                org_s = set(original_macs)
                new_s = set(current_macs)
                missing_macs = org_s - new_s
                for mac in missing_macs:
                    if resolve_vendor:
                        vendor = determine_vendor(mac)
                    blank_tuple = (mac, vendor, None, None)
                    output[vlan][ip].append(blank_tuple)
    return output


def copy_log_to_local(dev, remote_dir, filename):
    """Copies a file from a remote device to a local device via SCP.

    Args:
        dev (obj): PyEZ JUNOS device object with open SSH session.
        remote_dir (str): Absolute path for directory holding remote log file.
        filename (str): Name of file to be copied.

    Returns:
        None

    """
    logger.info('Copying log file {} to local disk...'.format(filename))
    try:
        with SCP(dev) as scp:
            scp.get(os.path.join(remote_dir, filename), os.path.join(log_dir, filename))
        logger.info('Duplicate IP log file copied.')
        logger.debug("{} -> {}".format(os.path.join(remote_dir, filename), os.path.join(log_dir, filename)))
    except Exception as e:
        logger.exception(e)
        raise
    return


class UnsupportedError(Exception):
    """Custom exception for unsupported methods."""
    def __init__(self, message):
        super().__init__(message)


class LogFile:
    """Object the represents a 'duplicate_ips' log file.

    Contains functions to open and parse the log file that was created on the MX gateway router to
    document IP conflicts.

    Attributes:
        filename (str): Name of the IP conflict log file.
        remote_log_dir (str): Absolute path of the remote directory housing the IP conflict log file.
        local_log_dir (str): Absolute path of the local log directory.
        remote_file_path (str): Absolute path of the remote IP conflict log file.
        local_file_path (str): Absolute path of the local IP conflict log file.
        file_type (str): The type of file that is the IP conflict log file.

    """
    def __init__(self, filename, local_log_dir, remote_log_dir):
        """

        Args:
            filename (str): Name of the IP conflict log file. Used for both remote and local files.
            local_log_dir (str): Absolute path of the local log directory.
            remote_log_dir (str): Absolute path of the remote directory housing the IP conflict log file.

        Returns:

        """
        self.filename = filename
        self.remote_log_dir = remote_log_dir
        self.local_log_dir = local_log_dir
        self.remote_file_path = self.create_file_path(self.remote_log_dir, self.filename)
        self.local_file_path = self.create_file_path(self.local_log_dir, self.filename)
        self.file_type = None

    @staticmethod
    def create_file_path(directory, filename):
        """Joins the directory and filename"""
        return os.path.join(directory, filename)

    def _set_file_type(self, logfile):
        """Determine the type of input file and set the file_type attribute."""
        mime = magic.Magic(mime=True)
        self.file_type = mime.from_file(logfile)

    def copy_log_to_local(self, device):
        """Copies a remote file to the local device via SCP"""
        try:
            with SCP(device) as scp:
                scp.get(self.remote_file_path, self.local_file_path)
        except Exception as e:
            logger.exception(e)
            raise

    def create_lines(self, logfile):
        """Creates a Python list data structure for lines in an input file.

        Args:
            logfile (str): Absolute path of a file to open.

        Returns:
            (list): Output from f.readlines()

        """
        self._set_file_type(logfile)
        if self.file_type == 'text/plain':
            with open(logfile, 'r') as f:
                return f.readlines()
        elif self.file_type == 'application/x-gzip':
            with gzip.open(logfile, 'rt') as f:
                return f.readlines()
        else:
            raise UnsupportedError("Unsupported file type: {}".format(self.file_type))


    # Main function
    def create_seed_dict(self, dev):
        """Function that initiates the creation of IP/MAC mappings from the IP conflict log file.

        Args:
            dev (obj): PyEZ JUNOS device with open SSH connection.

        Returns:
            (dict): Output of a call to the generate_seed_dict method with in LogParsers class.
            A LogParsers object is created and the list of lines from the file is fed to a method which
            returns a dictionary with IP/MAC mappings.

        """
        self.copy_log_to_local(dev)
        lines = self.create_lines(self.local_file_path)
        return LogParsers.generate_seed_dict(lines)


class LogParsers:
    """ Parses the log file and finds all IP addresses and the associated MACs.
    This code works for unstructure syslog only.

    Sample log output:
    Jun 12 23:26:53  My-MX1 /kernel: KERN_ARP_ADDR_CHANGE: arp info overwritten for 192.168.1.10 from 00:11:7d:1f:0b:3e to 0c:c5:7a:52:d1:aa
    """

    @staticmethod
    def generate_seed_dict(lines):
        """Create a dictionary that maps IP addresses to MAC and vice versa.

        Args:
            lines (list): List of lines form IP conflict file.

        Returns:
            seed_dict (dict): A mapping between IP and MAC addressing.

        """
        ip_to_macs = defaultdict(list)
        mac_to_ips = defaultdict(list)
        seed_dict = defaultdict(dict)
        for line in lines:
            if 'kernel' in line:
                junk, data = line.split("for")
                ip, mac_strings = data.split("from")
                ip = ip.strip()
                mac_raw_list = mac_strings.split("to")
                mac_raw_list = [mac.strip() for mac in mac_raw_list]
                for mac in mac_raw_list:
                    if mac not in ip_to_macs[ip]:
                        ip_to_macs[ip].append(mac)
                    if ip not in mac_to_ips[mac]:
                        mac_to_ips[mac].append(ip)
        seed_dict['ip_to_mac_mapping'] = ip_to_macs
        seed_dict['mac_to_ip_mapping'] = mac_to_ips
        return seed_dict


def determine_vlan(dev, seed_dict):
    """Generator function that finds and returns VLAN information for a set of MACs given an IP.

    Args:
        dev (obj): PyEZ JUNOS device with open SSH connection.
        seed_dict (dict): IP/MAC mappings.

    Yields:
        (tuple):
            vlan_name (str): The name of the VLAN as determined by the MX configuration associated with the IP/MAC info.
            vlan_id (str): VLAN tag of the VLAN discovered.
            ip (str): IP Address used for the search and associated with the yielded MACs.
            macs (list): List of strings.  The MAC addresses associated with the IP.

    """
    for ip, macs in seed_dict['ip_to_mac_mapping'].items():
        rt_tbl = RouteTable(dev)
        ifl_tbl = LogicalInterfaceTable(dev)
        rt_tbl.get(ip)
        # Assumes only a single active element
        find = rt_tbl[0]
        nh_int = find.via
        ifl_tbl.get(nh_int)
        ifl_info = ifl_tbl[0].bridge
        # Capture vlan name and TAG (JUNOS Format = VLAN_NAME+TAGID)
        vlan_name, vlan_id = ifl_info.split('+')
        yield (vlan_name, vlan_id, ip, macs)


def find_learned_interface(dev, personality, model, vlan_id, macs):
    """Determine from which interfaces a set of MAC addresses was learned.

    Args:
        dev (obj): PyEZ JUNOS device with open SSH connection.
        personality (str): General type of JUNOS device. 'MX' or 'SWITCH' supported.
        model (str): JUNOS model name.  'MX', 'EX' or 'QFX' supported.
        vlan_id (str): VLAN tag of the VLAN where the MACs are located.
        macs (list): MAC addresses for which to search for interfaces.

    Returns:
        parents (obj): DefaultDict dictionary like object keyed by the interface. Maps interfaces to MACs.

    Raises:
        UnsupportedError: If personality or model is not supported, this error is raised.

    """
    parents = defaultdict(list)
    if personality.lower() == 'mx':
        logger.debug("MACs associated with this IP:")
        # Compare MACs from duplicate list to MACs in this device's MAC table
        for mac in macs:
            # Because of invalid XML in 13.3R8.7, cannot search just bridge-domain.
            mac_table = BridgeTable(dev).get(address=mac)
            if len(mac_table.values()) > 0:
                for item in mac_table:
                    if item.vlan_id == vlan_id:
                        parents[item.interface].append(mac)
                        logger.debug("{} found on {}".format(mac, item.interface))
            else:
                logger.debug("No interface found for {}.".format(mac))

    elif personality == 'SWITCH':
        if 'QFX' in model:
            mac_table = QFXEtherSwTable(dev).get(vlan_id=vlan_id)
            logger.debug("MACs associated with this IP:")
            for item in mac_table:
                # Compare MACs from duplicate list to MACs in this device's MAC table
                for mac in macs:
                    if mac == item.mac:
                        logger.debug("{} found on {}".format(mac, item.interface))
                        parents[item.interface].append(mac)

        elif 'EX' in model:
            mac_table = EtherSwTable(dev).get(vlan_name=vlan_id)
            logger.debug("MACs associated with this IP:")
            for item in mac_table:
                # Compare MACs from duplicate list to MACs in this device's MAC table
                for mac in macs:
                    if mac == item.mac:
                        logger.debug("{} found on {}".format(mac, item.interface))
                        parents[item.interface].append(mac)
            logger.debug("Parents: {}".format(parents))

    else:
        raise UnsupportedError("No matching Table/View for hostname personality: {}, hostname model: {}"
                               .format(personality, model))
    return parents


def validate_login(ip, credentials):
    """Validates that a JUNOS device can be authenticated to via a set of known credentials.

    This rudimentary function is used to validate that a device belongs to a common set of search nodes, such as a
    lab's infrastructure devices.  All devices in this group have a common login.  Devices outside this
    scope should have a different login so that this function will fail.  Failure is one determiner of when
    to stop searching the network.

    Currently supports only username/password authentication.

    Args:
        ip (str): IP address of the device in question.
        credentials (dict): Credentials dictionary with auth mode, user/passwords and/or SSH keys.

    Returns:
        bool: True if connection success, else False.

    Raises:
        Exception: Whatever exceptions are thrown by the connect_dut func().

    """
    try:
        logger.info("Attempting to validate connection to {}...".format(ip))
        with connect_dut(ip, credentials=credentials, facts=False) as device:
            if device:
                logger.info("Connection validated.")
                pass
        return True
    except Exception as e:
        logger.info("{} failed login validation. Assuming this IP is a leaf.".format(ip))
        logger.error(e)
        return False


def find_local_interface(dev, interface):
    """Using LLDP, resolve the input interface to the first local physical interface.

    An interface could be an aggregate/bundle (AE) and this function finds, via LLDP, the first matching
    physical interface associated.  This local physical interface will be used to determine whether there are any
    neighbors attached or not.

    Args:
        dev (obj): PyEZ JUNOS device with open SSH connection.
        interface (str): The interface we are looking to resolve into a physical interface.

    Returns:
        local_int (str): If the input interface argument is an aggregate/bundle, it will return item.local_parent.
               If the item was a singular interface to begin with, it will return that IFD.
        None: local_int will be 'None' if interface not found in LLDP table.

    """
    def _find_local_int(table):
        """Internal function to iterate through LLDP table.

        Uses PyEZ Table/Views to determine LLDP information.

        Args:
            table (obj): PyEZ LLDPTable object that acts like a list. Each item in the table is an LLDPTableView
                         object with attributes created via YAML.

        Returns:
            (str): Interface name if a match was found.
            None: If no match is found.

        """
        logger.debug("Interface: {}".format(interface))
        for item in table:
            if item.local_int in interface:
                logger.debug("No parent match. Interface: {}, item.local_int: {}".format(interface, item.local_int))
                return item.local_int
            elif item.local_parent == "-":
                pass
            elif item.local_parent in interface:
                logger.debug("Local_parent {} match: local_int: {}".format(item.local_parent, item.local_int))
                # Returns the first local-interface that matches, not all interfaces.
                # This should be OK because an AE locals would be connected to same remote system.
                return item.local_int

    lldp_main_tbl = LLDPTable(dev).get()
    local_int = _find_local_int(lldp_main_tbl)
    return local_int


def find_remote_system(dev, model, local_int):
    """Finds, via LLDP, whether or not a device has a directly connected neighbor.

    Uses PyEZ Table/Views to determine LLDP information.

    Args:
        dev (obj): PyEZ JUNOS device with open SSH connection.
        model (str): JUNOS model name.  'MX', 'EX' or 'QFX' supported. Function assumes EX if not MX or QFX.
        local_int (str): Interface within the LLDP table on which to search for a neighbor.

    Returns:
        ip (str): IP address of the neighbor.
        name (str): Hostname of the neighbor.
        description (str): Description string of the neighbor from the LLDP table.

    """
    logger.debug("Model: {}".format(model.lower()))
    if 'mx' in model.lower():
        lldp_int_tbl = LLDPInterfaceNeighborMX(dev).get(interface_device=local_int)
    elif 'qfx' in model.lower():
        lldp_int_tbl = LLDPInterfaceNeighborMX(dev).get(interface_device=local_int)
    else:
        lldp_int_tbl = LLDPInterfaceNeighborEX(dev).get(interface_name=local_int)
    ip = lldp_int_tbl[0].remote_system_ip
    name = lldp_int_tbl[0].remote_system_name
    description = lldp_int_tbl[0].remote_system_description

    return ip, name, description


def search_remote_system(credentials, connect_timeout, system_data):
    """Searches a JUNOS system for MAC/IP/VLAN information, discovers neighbors, builds the tree.

    This function is the main worker function, used with multiprocessing, to scan through a JUNOS system,
    call other library functions and build a remote systems dictionary.  This data structure maps IP and
    MAC addressing to VLANs, interfaces and neighbors, along with which devices are end leaf devices and
    which have leaves connected to them.

    Args:
        credentials (dict): Contains credential information along with the mode of requested authentication.
        connect_timeout (int): PyEZ connection timeout in seconds.
        system_data (list): Contains a single tuple with system_ip and a system's value dictionary housing complete information about what
                           has been found so far for a single device.

    Returns:
        mytuple (tuple): Tuple of _systems_dict (dict) and macs_found (list).
                         _systems_dict gets larger each time this function discovers new devices. Each device
                         is marked with a bool 'searched: True' if it has been processed, or 'searched: False'
                         if it has just been discovered.

                         Macs_found is a total list of all MAC addressing found
                         while searching.

    """
    assert len(system_data) == 1, "Invalid length of input to 'search_remote_system'."
    # Convert tuple argument into dictionary for processing
    system_ip = system_data[0][0]
    _system_dict = dict(system_data)
    # Keep track of macs that we find interfaces for.
    macs_found = []
    logger.info("#### Searching System {}".format(system_ip))
    try:
        with connect_dut(system_ip, credentials, connect_timeout=connect_timeout) as dev:
            interfaces_to_macs = defaultdict(list)
            leaves = defaultdict(dict)
            parent_info = defaultdict(dict)

            # Add basic facts for this system if they don't exist
            keys = _system_dict.keys()
            if 'facts' not in keys:
                personality = dev.facts.get('personality')
                model = dev.facts.get('model')
                _system_dict[system_ip]['facts'] = {'personality': personality, 'model': model}
            old_interface = None
            for vlan, my_vlans_macs in _system_dict[system_ip]['vlans'].items():
                try:
                    learned_interfaces = find_learned_interface(dev, personality, model, vlan, my_vlans_macs)
                except UnsupportedError as e:
                    raise e
                if len(learned_interfaces) > 0:
                    for interface, my_ifaces_macs in learned_interfaces.items():
                        this_interfaces_macs = []       # Placeholder for MACs in the parent info
                        if interface:
                            macs_found.extend([mac for mac in my_ifaces_macs if mac not in macs_found])
                            local_int = find_local_interface(dev, interface=interface)
                            if local_int:
                                if old_interface:
                                    new_interface = local_int
                                else:
                                    old_interface = local_int
                                # If you found a local interface via LLDP, attempt to see if there is a remote IP associated.
                                r_ip, name, description = find_remote_system(dev, model=dev.facts.get('model'),
                                                                             local_int=local_int)
                                # If you didn't find a remote IP in the LLDP table, this interface is a leaf
                                if not r_ip:
                                    interfaces_to_macs[interface].extend([mac for mac in my_ifaces_macs if mac not in
                                                                          interfaces_to_macs[interface]])
                                else:
                                    # Creates an association between the parent and remote systems for these MACs
                                    parent_info[system_ip][vlan] = {local_int: this_interfaces_macs}
                                    this_interfaces_macs.extend(my_ifaces_macs)
                                    # Add a new remote system to the data structure
                                    if r_ip not in _system_dict:
                                        _system_dict[r_ip] = {'personality': personality, 'model': model, 'name': name,
                                                              'description': description, 'searched': False,
                                                              'vlans': {vlan: []}, 'parent_info': parent_info}
                                    # If we have not yet seen this MAC yet, add it to our existing data structure
                                    try:
                                        vlan_mac_list = _system_dict[r_ip]['vlans'][vlan]
                                        vlan_mac_list.extend([mac for mac in my_ifaces_macs if mac not in vlan_mac_list])
                                    except KeyError:
                                        if old_interface == new_interface:
                                            _system_dict[r_ip]['vlans'][vlan] = []
                                            vlan_mac_list = _system_dict[r_ip]['vlans'][vlan]
                                            vlan_mac_list.extend([mac for mac in my_ifaces_macs if mac not in vlan_mac_list])
                                        else:
                                            logger.error("Two distinct interfaces are connected from {} to {}. Potential mis-match access "
                                                         "vlan and/or mis-cabling issue.".format(system_ip, r_ip))
                                            logger.error("Check the following connections: {}:{}, {} <--> {}"
                                                         .format(system_ip, old_interface, new_interface, r_ip))
                                        continue
                            else:
                                # If you didn't find a local interface in the LLDP table, this interface is a leaf
                                interfaces_to_macs[interface].extend([mac for mac in my_ifaces_macs if mac not in
                                                                      interfaces_to_macs[interface]])
                else:
                    logger.warning("No MACs found while searching Vlan {} on device {}".format(vlan, system_ip))
                leaves[vlan].update(interfaces_to_macs)
            _system_dict[system_ip]['leaves'] = leaves
            _system_dict[system_ip]['searched'] = True
    except:
        # If you cannot login to the system, it is a leaf node.
        _system_dict[system_ip]['searched'] = True
    mytuple = (_system_dict, macs_found)
    return mytuple


def system_scan(systems_dict, credentials, processes, connect_timeout=None):
    """Recursive function to scan the network, building a data structure of the things it finds.

    Args:
        systems_dict (obj): Defaultdict dictionary like data structure with current view of network.
        credentials (dict): Contains credential information along with the mode of requested authentication.
        processes (int): Number of concurrent threads for multiprocessing.Pool()
        connect_timeout (int): PyEZ connection timeout in seconds.

    Returns:
        systems_dict (obj): Defaultdict dictionary like data structure housing all data relevant to the
                            network search for IP conflicts.
        all_macs_found (list): All the MAC addresses that where found during the search.
                                Sometimes MAC addressing in the log file do not show up in the search
                                because the address had timed out already.  We keep track of what we do
                                find for later.

    """
    depth = len(systems_dict)
    # Keeps track of all MACs that were returned from the search where an interface was found.
    all_macs_found = []
    logger.debug("Depth = {}".format(depth))
    # Find all systems which haven't yet been searched
    tosearch = [system for system in systems_dict if not systems_dict[system]['searched']]
    systems_pool = [[(system, systems_dict[system])] for system in tosearch]
    worker = partial(search_remote_system, credentials, connect_timeout)

    with Pool(processes) as p:
        results = p.map(worker, systems_pool)
    for item in results:
        systems_dict.update(item[0])
        all_macs_found.extend(item[1])

    new_depth = len(systems_dict.keys())
    logger.debug("New depth = {}".format(new_depth))
    if depth < new_depth:
        return system_scan(systems_dict, credentials, processes)
    else:
        return systems_dict, all_macs_found

