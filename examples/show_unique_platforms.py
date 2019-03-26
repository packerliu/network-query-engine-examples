#!/usr/bin/env python
"""Find unique Vendor, Model, OS combinations in the snapshot"""


import requests
from forward_nqe_client import FwdApi, printTable, formatIpAddr
from collections import defaultdict
import argparse
requests.packages.urllib3.disable_warnings()


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

# API to query Forward Data Model Export GraphQL API
api = FwdApi(args.url, (args.username, args.password), args.verify)

# Query to get device interface and VRF data.
platformQuery = '''
{
  devices{
    platform{
      vendor
      model
      osVersion
    }
  }
}
'''

# Query the API
platformDataset = api.query(args.snapshotId, platformQuery)

platforms = set()
osVersions = set()
models = set()
vendors = set()

for device in platformDataset['devices']:
    platform = device['platform']
    platforms.add((platform['vendor'], platform['model'],
                   platform['osVersion']))
    osVersions.add((platform['osVersion']))
    models.add((platform['model']))
    vendors.add((platform['vendor']))

print "Number of unique vendor, model, os combinations:", len(platforms)
print "Number of unique OS versions:", len(osVersions)
print "Number of unique device models:", len(models)
print "Number of unique vendors:", len(vendors)
print ""

printTable(["Vendor", "Model", "Os Version"],
           [list(x) for x in sorted(platforms)])
