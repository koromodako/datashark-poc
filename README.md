# Datashark

## Getting started 

```
datashark -h
```

## Actions

### Container

Container-related action can be used to extract information from a container. A 
container can be any type of file except a directory. A raw HDD image produced with `dd`
is a container as a memory dump or any other bytearray. 

 + `container.hash`:
```
> $ datashark container.hash Windows\ 7.vdi                                 

Datashark  Copyright (C) 2017  Paul Dautry
This program comes with ABSOLUTELY NO WARRANTY; for details use command `--warranty'.
This is free software, and you are welcome to redistribute it
under certain conditions; use command `--conditions' for details.

[INFO]{13772:datashark} - loading configuration...
[INFO]{13772:datashark} - configuration loaded.
[INFO]{13772:datashark} - Windows 7.vdi: a7738611c276a15f819817cfd8a499c1ab448a0189165bc13fd05fb79589386f
```

 + `container.mimes`:
```
> $ datashark container.mimes Windows\ 7.vdi                   

Datashark  Copyright (C) 2017  Paul Dautry
This program comes with ABSOLUTELY NO WARRANTY; for details use command `--warranty'.
This is free software, and you are welcome to redistribute it
under certain conditions; use command `--conditions' for details.

[INFO]{13816:datashark} - loading configuration...
[INFO]{13816:datashark} - configuration loaded.
[INFO]{13816:datashark} - Windows 7.vdi:
    mime: application/octet-stream
    text: VirtualBox Disk Image, major 1, minor 1 (<<< Oracle VM VirtualBox Disk Image >>>), 41943040000 bytes
```

### Dissector

Dissector-related actions can be used to dissect a container. The dissection 
process is recursive and is as precise as internal dissectors are.

 + `dissector.list`:
```
> $ datashark dissector.list                                   

Datashark  Copyright (C) 2017  Paul Dautry
This program comes with ABSOLUTELY NO WARRANTY; for details use command `--warranty'.
This is free software, and you are welcome to redistribute it
under certain conditions; use command `--conditions' for details.

[INFO]{13923:datashark} - loading configuration...
[INFO]{13923:datashark} - configuration loaded.
[INFO]{13923:dissector} - loading dissectors...
[INFO]{13923:dissector} - dissectors loaded.
[INFO]{13923:datashark} - dissectors:
[INFO]{13923:datashark} -   + application/octet-stream
[INFO]{13923:datashark} -       + octet_stream_dissector
```

 + `dissector.dissect`:
```
> $ datashark dissector.dissect Windows\ 7.vdi
```

### Hash Database

Hash database-related actions can be used to produce hash databases from files 
to improve dissection process making it faster (whitelist and blacklist).

 + `hdb.create`:
```
> $ datashark --include-files="*.py" hdb.create volatility.json volatility

Datashark  Copyright (C) 2017  Paul Dautry
This program comes with ABSOLUTELY NO WARRANTY; for details use command `--warranty'.
This is free software, and you are welcome to redistribute it
under certain conditions; use command `--conditions' for details.

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

 + `hdb.merge`:
```
> $ datashark hdb.merge whitelist.json windows-7-system32.json windows-7-program-files-x86.json
```
