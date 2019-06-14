#!/usr/bin/env python

"""Prints MAC table of all devices in a network snapshot."""

from forward_nqe_client import FwdApi, printTableNoHeader
import argparse
import urllib3

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

if not args.verify:
    urllib3.disable_warnings()

# API to query Forward NQE API
api = FwdApi(args.url, (args.username, args.password), args.verify)

# Query to get all devices' default network-instance and a page of its mac
# entries.
query = '''
query macQuery($deviceName: String, $cursor: String) {
  devices(name: $deviceName) {
    name
    networkInstances(name: "default") {
      fdb {
        macEntriesPage(after: $cursor) {
          items {
            macAddress
            vlan
            interfaces {
              interfaceName
              subinterfaceName
            }
            entryType
          }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    }
  }
}
'''

# Perform the initial query
dataset = api.query(args.snapshotId, query)


def print_mac_entry(macEntry):
    printTableNoHeader(
        [[macEntry['entryType'], macEntry['macAddress'],
          macEntry['vlan'],
          ", ".join(['interfaceName : "%s" sub-interfaceName : "%s"' %
                     (intf["interfaceName"], intf["subinterfaceName"])
                     for intf in macEntry['interfaces']])]])


for d in dataset['devices']:
    deviceName = d['name']
    # There will be only default network instance
    for n in d['networkInstances']:
        macEntriesPage = n['fdb']['macEntriesPage']
        for item in macEntriesPage['items']:
            print("\nDevice: %s" % deviceName)
            printTableNoHeader([["Type", "MAC", "Vlan", "Interfaces"]])
            print_mac_entry(item)
        pageInfo = macEntriesPage['pageInfo']
        cursor = pageInfo['endCursor']
        while pageInfo['hasNextPage']:
            subDataset = api.queryWithVars(args.snapshotId,
                                           query, {'deviceName': deviceName,
                                                   'cursor': cursor})
            device = subDataset['devices'][0]
            macEntriesPage =\
                device['networkInstances'][0]['fdb']['macEntriesPage']
            for item in macEntriesPage['items']:
                print_mac_entry(item)
            pageInfo = macEntriesPage['pageInfo']
            cursor = pageInfo['endCursor']
