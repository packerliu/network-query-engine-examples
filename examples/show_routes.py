#!/usr/bin/env python

"""Prints IPv4 RIBs of all devices in a network snapshot."""

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

rootQuery = '''
query rootQuery {
  devices {
    name
    networkInstances {
      name
    }
  }
}
'''


routeQuery= '''
query routeQuery($deviceName: String, $instanceName: String) {
  devices(name: $deviceName) {
    networkInstances(name: $instanceName) {
      afts {
        ipv4Unicast {
          ipEntriesPage {
            items {
              prefix
              nextHops {
                ipAddress
              }
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
}
'''

def print_route(route):
    printTableNoHeader([[route['prefix'], route['nextHops'][0]['ipAddress'] if len(route['nextHops']) > 0 else 'none']])


if __name__ == "__main__":
    # Perform the initial query
    dataset = api.query(args.snapshotId, rootQuery)

    for d in dataset['devices']:
        deviceName = d['name']
        print("\nDevice: %s" % deviceName)
        for i in d['networkInstances']:
            for route in api.iterate_pages(args.snapshotId,
                                           routeQuery, 
                                           { "deviceName": deviceName, 
                                             "instanceName": i['name']
                                           },
                                           ['devices', 'networkInstances', 'afts', 'ipv4Unicast', 'ipEntriesPage']):
                print_route(route)
