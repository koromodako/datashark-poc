# Datashark Core | TODO

**Note: Datashark is being developed for educational and research purpose.**

## HashDatabase

_N/A_

## Workspace

_N/A_

## Container

 + Create a `flag` attribute based on an `Enum` to save boolean properties

 + Add `carving_required` flag

 + Add `dissected` flag

## Dissection

 + Do not enqueue containers with `dissected` flag set YET persist them

 + Dissectors must create a container for each part processed at their level
   and set `dissected` flag before returning to worker.

 + Set `carving_required` flag on the

### Dissectors

#### Disk Image Formats

 + QCOW: implement everything
 + QCOW2: implement everything
 + QED: implement everything
 + VDI:
    + create "dissected" containers for metadata
    + flag for carving if required
    + type fixed dissection
    + type differencing dissection
 + VMDK:
    + flag for carving if required
    + create "dissected" containers for metadata
    + type flat 2GB splitted dissection
    + type flat monolithic dissection
    + type sparse 2GB splitted dissection
    + type sparse 2GB ESX dissection
    + type stream optimized
    + type raw device mapping
    + type physical disk dissection
 + VHD:
    + create "dissected" containers for metadata
    + flag for carving if required
    + parent-stack-based dissection
 + etc.

#### Volume Formats

 + MBR: implement everything
 + GPT: implement everything
 + etc.

#### File System Formats

 + extN: implement everything
 + fatN: implement everything
 + NTFS: implement everything
 + etc.

## DissectionDatabase

 + FSDB: implement everything
 + SQLite: implement everything
 + etc.
