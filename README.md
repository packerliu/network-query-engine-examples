
# Network Query Engine Examples [![Build Status](https://travis-ci.com/forwardnetworks/network-query-engine-examples.svg?token=F2RHJ9964SXT8kpW4Ns5&branch=master)](https://travis-ci.com/forwardnetworks/network-query-engine-examples)

Network Query Engine (NQE) by Forward Networks provides information about the network as JSON data in a fully-parsed form.
The information is normalized and presented uniformly across devices from different vendors.
The exported data structures are standards-aligned with [OpenConfig](http://www.openconfig.net/) (details below), and all data is available through a [GraphQL](#graphql) API as well as custom verification checks directly in the Forward Enterprise browser-based interface ([In-App NQE Checks](#in-app-nqe-checks)).

This repository helps you get started with the NQE GraphQL interface.

In particular, it walks you through the process of interactively crafting queries against a Forward Networks instance and explains the request and response structure of the API.
This repository also includes a simple Python client library that you can use to write Python scripts that query and consume NQE data.
This README describes how to install that library and provides example scripts that use this client library in interesting ways.
Finally, it provides all the information needed to configure and use Postman as GraphQL client.

If you'd like to start out with more background on NQE, please check out this [blog post](https://www.forwardnetworks.com/blog/network-query-engine) or the [network-query-engine](https://github.com/forwardnetworks/network-query-engine) repository.

# Getting Started

You can use any GraphQL client to consume NQE data.  
To get started you can use one of these options:
* [Try Queries on the Demo Network](#demo-network)
* [Use the Sample Python NQE Client](#nqe-client)
* [Use Postman](#postman)

<a id="demo-network"></a>
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

![Network Query Explorer](/images/network-query-explorer.png?width=800px)

You can try out other queries. The editor provides assistance via auto-complete and inline help, which you can access
by pressing control+shift keys. In addition, you can explore the full schema, including detailed formal and informal
documentation, by opening the "Docs" pane in the top-right-hand side toolbar.

Note that you can try out these queries against your own network snapshot by choosing the appropriate network and
snapshot on the query window.

<a id="nqe-client"></a>
## Use the Sample Python NQE Client

This repository includes a simple client library that can be used to run queries. The library is verified to work on
Python versions 2.6, 2.7, 3.4, 3.5 and 3.6.

Install the library like this:
```
pip install -r requirements.txt .
```
Root permissions may be required to run the above command.

Now you can run the examples in the examples/ directory. For example, in the examples directory, run:
```
python mismatched_interfaces.py https://fwd.app <yourUsername> <yourPassword> <yourSnapshotId>
```
<a id="postman"></a>
## Use Postman

Postman is a popular HTTP API testing and development environment. Mostly used for REST APIs, now [Postman supports GraphQL](https://blog.getpostman.com/2019/06/18/postman-v7-2-supports-graphql/?mkt_tok=eyJpIjoiWkdJMk1EZ3hPV0V3WVdOaSIsInQiOiJabDcxSUlIUTRXU3JNWlh2Tkx0ekdCT3VBSnNHTG1TWmkrQkhDOGhLNHlsamI0U2hKdHdzZU9mSlJ3XC9xUmNDVVp6dXJwdW9XQUFiczZnSDg1T3BQMnYrazNqXC8rYUlGeGFsXC9JMTBORGhadWtmUWtcLzRWb0lZbTFHaGVlaGg2NEEifQ%3D%3D) as well.  
Unfortunately, it doesn't support GraphQL Introspection, a key feature that allows to populate the schema inspector, provides autocomplete and enables to easily build schema documentation.

The GraphQL schema can be [imported manually](https://learning.getpostman.com/docs/postman/sending_api_requests/graphql/#importing-graphql-schemas) instead, providing autocomplete but no documentation. [GraphQL Schema Definition Language](https://www.prisma.io/blog/graphql-sdl-schema-definition-language-6755bcb9ce51) (SDL) is the only format supported.

The schema in SDL format can be exported from the Forward Platform using tools like [get-graphql-schema](https://www.npmjs.com/package/get-graphql-schema) or by running the following Introspection query in the [Network Query Explorer](https://fwd.app/network-query-explorer) and converting the JSON output to the SDL format using tools like [graphql-introspection-json-to-sdl](https://www.npmjs.com/package/graphql-introspection-json-to-sdl):

You can find the Forward GraphQL Schema [here](graphql-schema).

The picture below shows a simple query to get device platform details:
![NQE Postman](/images/nqe-postman.png?width=800px)

Select JSON format from the drop down menu (step 3 in the picture above) for a
prettier data visualization.

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
