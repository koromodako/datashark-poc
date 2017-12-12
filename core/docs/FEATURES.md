# Datashark Core | FEATURES

**Note: Datashark is being developed for educational and research purpose.**


 1. [HashDB](#hashdb)
 2. [Workspace](#workspace)
 3. [Container](#container)
 4. [Dissection](#dissection)
    1. [Dissection Process](#dissection-process)
    2. [Dissectors](#dissectors)
 5. [DissectionDB](#dissectiondb)
    1. [Adapters](#adapters)
 6. [Carving](#carving)


## HashDB

A HashDB is a database containing a dictionary of hashes and associated file.

It can be used as:

 + a **whitelist** to exlude files from dissection if these files are known to
   be legitimate.

 + a **blacklist** to exclude files from dissection if these files are known not
   to be legitimate.

Datashark accepts both lists (white & black) as input parameters of the
dissection process.

## Workspace

A Workspace is created for each instance of Datashark. It provides an organized
space in host filesystem to save output data, temporary data and execution
logs.

## Container

A container can be seen as a bytearray of a given length. We do not presume
what a container may contain or represent. Data within a container might be
encrypted, encoded, structured or not, compressed or not, or it might be
random bytes.

The job of dissectors is to extract meaningful data from these containers
if the data matches a known, _implemented_ file type.

In the event of an unknown container, meaning which cannot be dissected,
carvers can be used to identify and if possible retrieve information from this
data.

## Dissection

This concept represent the fact of extracting, recursively, any type of
container which is given as an input. Dissection aims at identifying,
extracting and interpreting metadata contained in a file format in order to
extract additional data.

### Dissection Process

_TODO_

### Dissectors

|     **Category**    | **Name** | **Implemented** |   **Tested**  |
|:-------------------:|:---------|:---------------:|:-------------:|
| Virtual Disk Format |   VMDK   |   _incomplete_  |  _incomplete_ |
| Virtual Disk Format |   VDI    |   _incomplete_  |  _incomplete_ |
| Virtual Disk Format |   VHD    |   _incomplete_  |  _incomplete_ |
| Virtual Disk Format |   QCOW   |   NO            |  NO           |
| Virtual Disk Format |   QCOW2  |   NO            |  NO           |
| Virtual Disk Format |   QED    |   NO            |  NO           |

_TODO_

## DissectionDB

This concept represents any type of implemented storage depending on the
resources you have and the efficiency you want when browsing results or
running complementary analysis tools, etc.

This storage will be used to store information created extracted during the
dissection process.

A storage is associated with a workspace which means that:

```
one dissection process => one workspace => one storage instance
```

### Adapters

| **Name** | **Format** | **Description**                                     |
|:--------:|:----------:|:----------------------------------------------------|
|   json   |    JSON    | containers are stored inside a single json file     |
|  sqlite  |   SQL DB   | containers are stored inside a relational database  |
|    fs    |     FS     | containers are stored as a FS tree                  |


## Carving

_N/A_
