#!/usr/bin/env python

"""Finds interfaces whose configured and operational states differ."""

from forward_data_model_export_client import FwdApi, printTable
import sys
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

# API to query Forward Data Model Export GraphQL API
api = FwdApi(args.url, (args.username, args.password), args.verify)

# Query to get device interfaces and their states.
query = '''
{
  devices {
    name
    interfaces {
      name
      adminStatus
      operStatus
    }
  }
}
'''

# Perform the query
dataset = api.query(args.snapshotId, query)

# Calculate violations
violations = [(d, i)
              for d in dataset['devices']
              for i in d['interfaces']
              if i['adminStatus'] != i['operStatus']]

# Report the violations, if any
if not violations:
    print "OK"
else:
    print "Interfaces with differing admin and operational states"
    printTable(
        ["Device", "Interface", "Admin status", "Oper status"],
        [[d['name'], i['name'], i['adminStatus'], i['operStatus']]
         for (d, i) in violations])
