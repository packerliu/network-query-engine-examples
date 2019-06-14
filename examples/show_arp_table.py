#!/usr/bin/env python

"""Prints IPv4 ARP table of all devices in a network snapshot."""

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

# Neighbors page subsection in a query
neighborsPageSubSection = '''
ipv4 {
  neighborsPage(after: $cursor) {
    items {
      ip
      linkLayerAddress
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
'''

# Initial query to get all devices' interfaces and a single page of their
# neighbors.
initialQuery = '''
query initialQuery($cursor: String) {
  devices {
    name
    interfaces {
      name
      subinterfaces {
        name
        ''' + neighborsPageSubSection + '''
      }
      bridge {
        ''' + neighborsPageSubSection + '''
      }
      tunnel {
        ''' + neighborsPageSubSection + '''
      }
      routedVlan {
        ''' + neighborsPageSubSection + '''
      }
    }
  }
}
'''

# Query to get a devices' sub-interfaces and a page of its neighbors after a
# cursor.
subinterfaceQuery = '''
query subinterfaceQuery($deviceName: String, $interfaceName: String,
                        $subinterfaceName: String, $cursor: String) {
  devices(name: $deviceName) {
    interfaces(name: $interfaceName) {
      subinterfaces(name: $subinterfaceName) {
        ''' + neighborsPageSubSection + '''
      }
    }
  }
}
'''

# Query to get a devices' bridge interface and a page of its neighbors after a
# cursor.
bridgeQuery = '''
query bridgeQuery($deviceName: String, $interfaceName: String,
                  $cursor: String) {
  devices(name: $deviceName) {
    interfaces(name: $interfaceName) {
      bridge {
        ''' + neighborsPageSubSection + '''
      }
    }
  }
}
'''

# Query to get a devices' tunnel interface and a page of its neighbors after a
# cursor.
tunnelQuery = '''
query tunnelQuery($deviceName: String, $interfaceName: String,
                  $cursor: String) {
  devices(name: $deviceName) {
    interfaces(name: $interfaceName) {
      tunnel {
        ''' + neighborsPageSubSection + '''
        }
      }
    }
  }
}
'''

# Query to get a devices' routed vlan interface and a page of its neighbors
# after a cursor.
routedVlanQuery = '''
query routedVlanQuery($deviceName: String, $interfaceName: String,
                      $cursor: String) {
  devices(name: $deviceName) {
    interfaces(name: $interfaceName) {
      routedVlan {
        ''' + neighborsPageSubSection + '''
      }
    }
  }
}
'''

# Perform the initial query
dataset = api.query(args.snapshotId, initialQuery)


def print_neighbor(neighbor):
    printTableNoHeader([[neighbor['ip'], neighbor['linkLayerAddress']]])


def iterate_pages_in_intf_type(subTree, intfType, subQuery,
                               isSubTreeArray=False):
    for item in subTree['ipv4']['neighborsPage']['items']:
        print_neighbor(item)
    pageInfo = subTree['ipv4']['neighborsPage']['pageInfo']
    cursor = pageInfo['endCursor']
    # Iterate over all the pages
    while pageInfo['hasNextPage']:
        subDataset = \
            api.queryWithVars(args.snapshotId, subQuery,
                              {'deviceName': deviceName,
                               'interfaceName': interfaceName,
                               'subinterfaceName': subinterfaceName,
                               'cursor': cursor})
        device = subDataset['devices'][0]
        if isSubTreeArray:
            subTree = device['interfaces'][0][intfType][0]
        else:
            subTree = device['interfaces'][0][intfType]
        neighborsPage = subTree['ipv4']['neighborsPage']
        for item in neighborsPage['items']:
            print_neighbor(item)
        pageInfo = neighborsPage['pageInfo']
        cursor = pageInfo['endCursor']


for d in dataset['devices']:
    deviceName = d['name']
    print("\nDevice: %s" % deviceName)
    for i in d['interfaces']:
        interfaceName = i['name']
        # Iterate subinterfaces
        for s in i['subinterfaces']:
            subinterfaceName = s['name']
            iterate_pages_in_intf_type(s, 'subinterfaces', subinterfaceQuery,
                                       True)
        # Iterate pages in bridge
        if i['bridge'] is not None:
            iterate_pages_in_intf_type(i['bridge'], 'bridge', bridgeQuery)
        # Iterate pages in tunnel
        if i['tunnel'] is not None:
            iterate_pages_in_intf_type(i['tunnel'], 'tunnel', tunnelQuery)
        # Iterate pages in routed vlan
        if i['routedVlan'] is not None:
            iterate_pages_in_intf_type(i['routedVlan'], 'routedVlan',
                                       routedVlanQuery)
