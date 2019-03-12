
# Network Query Engine Examples [![Build Status](https://travis-ci.com/forwardnetworks/network-query-engine-examples.svg?token=F2RHJ9964SXT8kpW4Ns5&branch=master)](https://travis-ci.com/forwardnetworks/network-query-engine-examples)

Network Query Engine (NQE) by Forward Networks provides a simple API that exposes information about the network as JSON data in a
fully-parsed form. The information is normalized and presented uniformly across devices from different vendors. The
exported data structures are standards-aligned with [OpenConfig](http://www.openconfig.net/) (details below), and
all data is available through a [GraphQL](https://graphql.org/) API. This API allows network operators to
easily develop scripts - for example, to perform sanity checks or to display information - that work across the entire
fleet of devices in their network.

This repository helps you get started with NQE. In particular, it walks you through the process of
interactively crafting queries against a Forward Networks instance and explains the request and response structure of the
API. This repository also includes a simple Python client library that you can use to write Python scripts that query
and consume NQE data. This README describes how to install that library and provides example scripts that use this
client library in interesting ways.

If you'd like to start out with more background on NQE, please check out [this blog post](https://www.forwardnetworks.com/blog/network-query-engine).

# Getting Started

## Try Queries on the Demo Network

The quickest way to get started is to try out sample queries against a demo network on [Forward App](https://fwd.app/). Note that if
you do not already have an account there, you can
[request an account here](https://www.forwardnetworks.com/free-trial/).

Browse to the [Network Query Explorer in app](https://fwd.app/network-query-explorer). Use the network and snapshot selectors in the toolbar to select the demo
network and its snapshot. Now try out the following simple query, by dropping the following query into the left hand-side pane and
running the play button:
```
{
  devices {
    name
  }
}
```

You should see output like this in the right hand-side pane, containing all the device names in the demo network:
```
{
  "data": {
    "devices": [
      {
        "name": "atl-app-lb01"
      },
      {
        "name": "atl-ce01"
      },
      ...
    ]
  }
}
```

You can try out other queries. The editor provides assistance via auto-complete and inline help, which you can access
by pressing control+shift keys. In addition, you can explore the full schema, including detailed formal and informal
documentation, by opening the "Docs" pane in the top-right-hand side toolbar.

Note that you can try out these queries against your own network snapshot by choosing the appropriate network and
snapshot on the query window.

## Use the Sample Python NQE Client

This repository includes a simple client library that can be used to run queries. The library is verified to work on
Python versions 2.6 and 2.7.

Install the library like this:
```
pip install -r requirements.txt .
```
Root permissions may be required to run the above command.

Now you can run the examples in the examples/ directory. For example, in the examples directory, run:
```
python mismatched_interfaces.py https://fwd.app <yourUsername> <yourPassword> <yourSnapshotId>
```

# Examples

The repository provides the following example queries and scripts:
* [Show names of all devices.](examples/show_all_device_names.py) This is a simple example to simply list all devices
in a network.
* [Show unique platforms.](examples/show_unique_platforms.py) This script shows the unique Vendor, model, and OS combinations in a network.
* [Find interfaces with clashing configured and operational status.](examples/mismatched_interfaces.py) Interfaces can
be configured up, but can be operationally down for a variety of reasons. This script finds cases where the states
differ, so that an operator can do further investigation.
* [Find IP addresses that are assigned to more than one interface within a VRF.](examples/ip_uniqueness.py) Assigning
a single IP address to multiple interfaces in a network can often lead to problems. This script queries Forward Networks
NQE and finds all violations of this problem, showing the interfaces on which each duplicate IP address is assigned.

# Data Coverage

The initial data set covered by NQE includes:
* Basic device info including device name, vendor, platform, and os.
* Interface data.
* IPv4 and IPv6 RIBs across all VRFs.
* Subset of BGP RIBs (`adj-rib-in` and `adj-rib-out`).
* Topology data via fields that link interfaces to other connected interfaces.

The [Data Model Explorer](https://fwd.app/data-model-explorer) (explained below) provided by Forward Network instances
provides an easy to use tool to interactively view the full schema details. However, you can also
[see the full schema offline here](network-schema.md).

NQE will include more data over time. If the information that you need is not in the schema, please open
an issue and request the data.

# Relationship to OpenConfig

Forward Networks NQE is *aligned* with OpenConfig, but is not literally the same data model as any of the various
JSON representations of the OpenConfig YANG data models. Rather, Forward Networks NQE can be seen as an idiomatic
representation of OpenConfig as a GraphQL data source: we have adapted the OpenConfig YANG data models to fit within
the constraints of GraphQL, to adapt to the conventions prevalent within GraphQL APIs, and to take advantage of the
powerful query features available in GraphQL.

Specifically, Forward Networks NQE differs from OpenConfig models in the following ways:
1. Names are camel-cased. Dashes are not permitted in GraphQL.
2. The config and state hierarchy is squashed out, similar to "path-compression" in
[ygot](https://github.com/openconfig/ygot/blob/master/docs/design.md#openconfig-path-compression).
3. OpenConfig sometimes represents some complex entity as a string with specific format, such as vlan range in the
`x..y` format. NQE chooses to model these as structured objects.
4. Some collections of elements, such as BGP routes, are "paged" in NQE because they are often very large. This paging
allows clients to ask for a page of routes at a time.
5. Additional data is sometimes added, such as device platform information under the `platform` field of `Device`, or
the `links` field of an interface that adds topology information to the interface object information.
6. NQE takes advantage of GraphQL's *graph* model to provide fields on objects that link (aka *join*) to related
information. For example, a field of an interface links to other interface to which it is connected. This field
provides the related interface object, not just its name.
7. Forward Networks NQE only covers a subset of OpenConfig models. [More info on included data.](#Data-Coverage)


# API Details

The API is available via HTTP POST to the following URL
```
https://<ForwardInstance>/api/snapshots/<SnapshotId>/graphql
```
The body of the POST should follow the [standard GraphQL request JSON structure](https://graphql.org/learn/serving-over-http/#post-request). Specifically, it should include a query field to hold the query string, and an optional variables field to pass variables used by the query ([see here for background on GraphQL variables](https://graphql.org/learn/queries/#variables)):
```
{ "query": "<your query>", "variables": [{"var1", "value1"}, ..., {"varn", "valuen"}]}
```

The API is authenticated via basic auth.

For example, you can issue the query shown previously via curl against https://fwd.app as follows:

```
curl --user myusername:mypassword https://fwd.app/api/snapshots/100/graphql -X POST -H "Content-Type: application/json" -d '{"query": "{ devices { name } }"}'
```


# Contributing

We welcome contributions! Please submit and share scripts, queries, and examples. Bug fixes, doc improvements and so on
are also welcome. To contribute, fork the repository, push your work to a branch in that repository and then submit a
pull request. Specifically, do:

1. Fork this repo
2. Clone your forked repo
2. In your forked repo, create your feature branch (`git checkout -b my-feature`)
3. Push to the new branch of your forked repo: (`git push origin my-feature`)
4. Create new Pull Request

## Contact

[@AndreasVoellmy](@AndreasVoellmy) or use the project GitHub issues.

# Further reading

* [Product docs](https://app.forwardnetworks.com/docs/applications/data_model_export/)
* [Network Query Engine Blog Post](https://www.forwardnetworks.com/blog/network-query-engine)
