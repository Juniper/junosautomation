# Copyright 2017, Juniper Networks Pvt Ltd.
# All rights reserved.
# Same test using direct RPC call
def check_ospf_full_adjacencies(dev, neighbor_count):
    full_count = 0
    rpc_result = dev.rpc.get_ospf_neighbor_information()
    for element in rpc_result.findall("ospf-neighbor"):
        if element.findtext("ospf-neighbor-state") == "Full":
            full_count += 1
        else:
            return False
    return full_count == neighbor_count

# Same test using jxmlease
import jxmlease
def check_ospf_full_adjacencies(dev, neighbor_count):
    full_count = 0
    parser = jxmlease.EtreeParser()
    res = parser(dev.rpc.get_ospf_neighbor_information())
    for neighbor_data in res["ospf-neighbor-information"]["ospf-neighbor"]:
        if neighbor_data["ospf-neighbor-state"] == "Full":
            full_count += 1
        else:
            return False
    return full_count == neighbor_count
