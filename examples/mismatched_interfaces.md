# Find interfaces with clashing configured and operational status

## Description

Interfaces can be configured up, but can be operationally down for a variety of reasons.
This script finds cases where the states differ, so that an operator can do further investigation

## Query

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
