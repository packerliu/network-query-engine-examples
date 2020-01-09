# Find IP addresses that are assigned to more than one interface within a VRF

## Description

Assigning a single IP address to multiple interfaces in a network can often lead
to problems.
This script queries Forward Networks NQE and finds all violations of this
problem, showing the interfaces on which each duplicate IP address is assigned.

## Query

```
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
```

## Python Script
[Find IP addresses that are assigned to more than one interface within a VRF](ip_uniqueness.py)

## Sample output
![IP Uniqueness](/images/ip_uniqueness.png?width=800px&classes=shadow)
