#!/usr/bin/env python

"""Prints names of all devices in a network snapshot."""

from forward_nqe_client import FwdApi, printTable
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

# Query to get device interfaces and their states.
query = '''
{
  devices {
    name
  }
}
'''

# Perform the query
dataset = api.query(args.snapshotId, query)

# Print the device names
printTable(["Device"], [[d['name']] for d in dataset['devices']])
