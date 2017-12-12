# Datashark | README

**Note: Datashark is being developed for educational and research purpose.**

 1. [Getting Started](#getting-started)
 2. [Features Docs](#features-docs)
 3. [Actions](#actions)
    1. [HashDB](#hashdb)
    2. [Workspace](#workspace)
    3. [Container](#container)
    4. [Dissection](#dissection)
    5. [DissectionDB](#dissectiondb)

## Getting started

Get some help about datashark CLI arguments:

```bash
> $ datashark -h
```

Get some help about datashark actions:

```bash
> $ datashark help
```

## Features Docs

 + [Core Features](core/docs/FEATURES.md)
 + [GUI Features](ui/docs/FEATURES.md)

## Actions

### HashDB

 + `hashdb.create`:

```
> $ datashark --include-files="*.py" hashdb.create volatility.json volatility

[snip]

[INFO]{14067:datashark} - loading configuration...
[INFO]{14067:datashark} - configuration loaded.
[INFO]{14067:hashdatabase} - scanning for files...
[INFO]{14067:hashdatabase} - start hashing processes...
[INFO]{14070:hashdatabase} - processing file: /[snip]/volatility/setup.py
[INFO]{14070:hashdatabase} - processing file: /[snip]/volatility/vol.py
[INFO]{14067:hashdatabase} - aggregating results...
[INFO]{14067:hashdatabase} - writing database...
[INFO]{14067:hashdatabase} - done.

> $ cat volatility.json
{"9c66137f7745fbe0758c8e3b54a5975752414f5b8bd4917821a3f16f1e80762b":"/[snip]/volatility/setup.py","5d68a0d6e3c48a90607a9ad114a8cfde8e9a56906faeadc93d2164ef9f028d27":"/[snip]/volatility/vol.py"}
```

 + `hashdb.merge`:

```
> $ datashark hashdb.merge whitelist.json windows-7-system32.json windows-7-program-files-x86.json
```

### Workspace

 + `workspace.list`:

```
> $ datashark workspace.list

[snip]

[INFO]{10688:datashark} - loading configuration...
[INFO]{10688:datashark} - configuration loaded.
[INFO]{10688:workspace} -
workspaces:
    + /tmp/ds.ws.63253c56
    + /tmp/ds.ws.88c52cf2
    [snip]
    + /tmp/ds.ws.4784be8d
    + /tmp/ds.ws.1f7a5b3f

total: 9
```

 + `workspace.clean`:

```
> $ datashark workspace.clean

[snip]

[INFO]{10729:datashark} - loading configuration...
[INFO]{10729:datashark} - configuration loaded.
[INFO]{10729:workspace} - removing /tmp/ds.ws.63253c56...
[INFO]{10729:workspace} - removing /tmp/ds.ws.88c52cf2...
[snip]
[INFO]{10729:workspace} - removing /tmp/ds.ws.4784be8d...
[INFO]{10729:workspace} - removing /tmp/ds.ws.1f7a5b3f...
```

### Container

 + `container.hash`:
```
> $ datashark container.hash Windows\ 7.vdi

[snip]

[INFO]{13772:datashark} - loading configuration...
[INFO]{13772:datashark} - configuration loaded.
[INFO]{13772:datashark} - Windows 7.vdi: a7738611c276a15f819817cfd8a499c1ab448a0189165bc13fd05fb79589386f
```

 + `container.mimes`:
```
> $ datashark container.mimes Windows\ 7.vdi

[snip]

[INFO]{13816:datashark} - loading configuration...
[INFO]{13816:datashark} - configuration loaded.
[INFO]{13816:datashark} - Windows 7.vdi:
    mime: application/octet-stream
    text: VirtualBox Disk Image, major 1, minor 1 (<<< Oracle VM VirtualBox Disk Image >>>), 41943040000 bytes
```

### Dissection

Dissector-related actions can be used to dissect a container. The dissection
process is recursive and is as precise as internal dissectors are.

 + `dissector.list`:

```
> $ datashark dissection.list

[snip]

[INFO]{10828:datashark} - loading configuration...
[INFO]{10828:datashark} - configuration loaded.
[INFO]{10828:dissection} - loading dissectors...
[INFO]{10828:dissection} - <dissection.dissectors.disk_images.qcow> imported successfully.
[INFO]{10828:dissection} - <dissection.dissectors.disk_images.vmdk> imported successfully.
[INFO]{10828:dissection} - <dissection.dissectors.disk_images.qed> imported successfully.
[INFO]{10828:dissection} - <dissection.dissectors.disk_images.vhd> imported successfully.
[INFO]{10828:dissection} - <dissection.dissectors.disk_images.qcow2> imported successfully.
[INFO]{10828:dissection} - <dissection.dissectors.disk_images.vdi> imported successfully.
[INFO]{10828:dissection} - dissectors loaded.
[INFO]{10828:dissection} - dissectors:
[INFO]{10828:dissection} -  + application/octet-stream
[INFO]{10828:dissection} -      + qcow
[INFO]{10828:dissection} -      + qcow2
[INFO]{10828:dissection} -      + qed
[INFO]{10828:dissection} -      + vdi
[INFO]{10828:dissection} -      + vhd
[INFO]{10828:dissection} -      + vmdk
[INFO]{10828:dissection} -  + text/plain
[INFO]{10828:dissection} -      + vmdk

```

 + `dissector.dissector.xxx.xxx`: call specific service offered by a specific
   dissector.

```
> $ datashark dissection.dissector.vdi.header Windows\ 7.vdi

[snip]

[INFO]{11054:datashark} - loading configuration...
[INFO]{11054:datashark} - configuration loaded.
[INFO]{11054:dissection} - loading dissectors...
[INFO]{11054:dissection} - <dissection.dissectors.disk_images.qcow> imported successfully.
[INFO]{11054:dissection} - <dissection.dissectors.disk_images.vmdk> imported successfully.
[INFO]{11054:dissection} - <dissection.dissectors.disk_images.qed> imported successfully.
[INFO]{11054:dissection} - <dissection.dissectors.disk_images.vhd> imported successfully.
[INFO]{11054:dissection} - <dissection.dissectors.disk_images.qcow2> imported successfully.
[INFO]{11054:dissection} - <dissection.dissectors.disk_images.vdi> imported successfully.
[INFO]{11054:dissection} - dissectors loaded.
[INFO]{11054:vdi} -
VDIHeader(size=512):
    + magic: b'<<< Oracle VM VirtualBox Disk Image >>>\n\x00\x00[snip]\x00'
    + signature: b'\x7f\x10\xda\xbe'
    + vmajor: 1
    + vminor: 1
    + hdrSz: 400
    + imgType: 1
    + imgFlags: 0
    + imgDesc: b'\x00[snip]\x00'
    + oftBlk: 1048576
    + oftDat: 2097152
    + numCylinders: 0
    + numHeads: 0
    + numSectors: 0
    + sectorSz: 512
    + pad0: None
    + diskSz: 41943040000
    + blkSz: 1048576
    + blkExtraDat: 0
    + numBlkInHdd: 40000
    + numBlkAllocated: 35763
    + vdiUuid: b'r\xfe\xce\xb5M\x8euC\x8b\xe1Z\x13\xac\xab\xf9o'
    + lastSnapUuid: b'h\xbc\x83\x80;0\xd2D\xb2q.>\xb2\xc2\xcb\xe7'
    + linkUuid: b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    + parentUuid: b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    + pad1: None

```

 + `dissector.dissect`:

```
> $ datashark dissector.dissect Windows\ 7.vdi
```

### DissectionDB

 + `dissectiondb.list`:

```
> $ datashark dissectiondb.list

[snip]

[INFO]{11143:datashark} - loading configuration...
[INFO]{11143:datashark} - configuration loaded.
[INFO]{11143:dissectiondb} -
Adaptaters:
    + json
    + sqlite
```
