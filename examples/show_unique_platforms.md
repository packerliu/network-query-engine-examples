# Show Unique Platforms

## Description

Find unique Vendor, Model, OS combinations in a network snapshot

## Query

The following query shows only how to get all the platform vendor, model and osVersion. To find the unique Vendor, Model, OS combinations you need to execute the Python script.

```
{
  devices{
    platform{
      vendor
      model
      osVersion
    }
  }
}
```

## Python Script
[Show Unique Platforms](show_unique_platforms.py)

## Sample output
![Unique Platforms](/images/show_unique_platforms.png?width=800px&classes=shadow)
