#!/usr/bin/env python

"""Finds ips that are applied to multiple interfaces within a VRF."""

from forward_nqe_client import FwdApi, printTable, formatIpAddr
from collections import defaultdict
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "url",
    help="The URL of a Forward Networks instance, e.g. https://fwd.app.")
parser.add_argument(
    "username",
    help="The username of an account on the above-specified "
         "Forward Networks instance.")
parser.add_argument(
    "password",
    help="The password of an account on the above-specified "
         "Forward Networks instance.")
parser.add_argument(
    "snapshotId",
    help="The snapshotId of a snapshot on the above-specified "
         "Forward Networks instance.")
parser.add_argument(
    "--verify",
    help="Whether to verify the certificate on the instance "
         "(e.g. True or False)",
    action="store_true")
args = parser.parse_args()

# API to query Forward NQE API
api = FwdApi(args.url, (args.username, args.password), args.verify)

# Query to get device interface and VRF data.
query = '''
{
  devices {
    name

    # IP addresses for interfaces, located in the subinterfaces.
    interfaces {
      name
      adminStatus
      subinterfaces {
        name
        adminStatus
        ipv4 {
          addresses {
            ip
            prefixLength
          }
        }
      }
    }

    # VRF name and associated interface & subinterface
    networkInstances {
      name
      interfaces {
        interfaceName
        subInterfaceName
      }
    }
  }
}
'''

# Query the API
dataset = api.query(args.snapshotId, query)

# Violations are those (vrf, subnet) pairs that are assigned to multiple
# distinct interfaces on a vrf. To compute this, we do the following:
#  (1) Get the IP addresses for interface
#  (2) Build a map from IP address to the the set of interfaces where it is
#      assigned by going over each vrf, getting its interfaces, and then
#      (using (1)) get its ip addresses and update the map with the location
#      of the found interface.

# (1) Define a dictionary mapping device interfaces to their assigned
# ip subnets.
ifaceToIpsMap = {(d['name'], iface['name'], subiface['name']):
                 subiface['ipv4']['addresses']
                 for d in dataset['devices']
                 for iface in d['interfaces']
                 for subiface in iface['subinterfaces']
                 }

# Exclude devices in "backup mode"
devicesInBackupOpMode = ["atl-edge-fw02"]

# (2) Build the dictionary that maps each (vrf, ip) pair to the locations
# where it has been assigned.
vrfSubnetToIfaceMap = defaultdict(set)
for dev in dataset['devices']:
    devName = dev['name']
    if not (devName in devicesInBackupOpMode):
        for vrf in dev['networkInstances']:
            for iface in vrf['interfaces']:
                location = (devName, iface['interfaceName'],
                            iface['subInterfaceName'])
                for addr in ifaceToIpsMap.get(location, []):
                    address = (addr['ip'], addr['prefixLength'])
                    vrfSubnetToIfaceMap[(vrf['name'], address)].add(location)

violations = [(vrf, addr, ifaces) for (vrf, addr),
              ifaces in vrfSubnetToIfaceMap.items() if len(ifaces) > 1]

if not violations:
    print ("OK")
else:
    print ("Found the following IP uniqueness violations:")
    printTable(
        ["VRF", "Subnet", "Interfaces"],
        [[vrf, formatIpAddr(addr), ", ".join([dn + ':' + s
         for (dn, i, s) in locs])] for (vrf, addr, locs) in violations])
