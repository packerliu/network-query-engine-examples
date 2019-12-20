# Find interfaces with clashing configured and operational status

## Description

Interfaces can be configured up, but can be operationally down for a variety of reasons.
This script finds cases where the states differ, so that an operator can do further investigation

## Query

The following query shows only how to get the interfaces adminStatus and operStatus.
To find the interfaces with clashing configured and operational status you need to execute the Python script.

```
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
```

## Python Script
[Find interfaces with clashing configured and operational status](mismatched_interfaces.py)

## Sample output
![Mismatched Interfaces](/images/mismatched_interfaces.png?width=800px&classes=shadow)
