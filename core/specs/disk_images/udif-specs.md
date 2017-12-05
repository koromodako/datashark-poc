# UDIF data format

Apple disk image files are essentially raw disk images (i.e. contain block data) with some added metadata, optionally with one or two layers applied that provide compression and encryption. In hdiutil these layers are called CUDIFEncoding and CEncryptedEncoding.[1]

UDIF supports ADC (an old proprietary compression format by Apple), zlib, bzip2 (as of Mac OS X v10.4), and LZFSE (as of Mac OS X v10.11)[5] compression internally.

## Trailer

The trailer can be described using the following C structure.[6] All values are big-endian (PowerPC byte ordering)

```
typedef struct {
    uint8_t     Signature[4];
    uint32_t Version;
    uint32_t HeaderSize;
    uint32_t Flags;                 
    uint64_t RunningDataForkOffset;
    uint64_t DataForkOffset;
    uint64_t DataForkLength;
    uint64_t RsrcForkOffset;     
    uint64_t RsrcForkLength;        
    uint32_t SegmentNumber;
    uint32_t SegmentCount;
    uuid_t   SegmentID;
    uint32_t DataChecksumType;
    uint32_t DataChecksumSize;
    uint32_t DataChecksum[32];
    uint64_t XMLOffset; 
    uint64_t XMLLength; 
    uint8_t  Reserved1[120];
    uint32_t ChecksumType;
    uint32_t ChecksumSize;
    uint32_t Checksum[32];
    uint32_t ImageVariant;
    uint64_t SectorCount;
    uint32_t reserved2;
    uint32_t reserved3;
    uint32_t reserved4;
} __attribute__((__packed__)) UDIFResourceFile;
```

Here is an explanation:

|  Offset |  Length (bytes) | Description                                            |
|:-------:|:---------------:|:-------------------------------------------------------|
|  `000`  |  4              | Magic bytes ('koly').                                  |
|  `004`  |  4              | File version (current is 4)                            |
|  `008`  |  4              | The length of this header, in bytes. Should be 512.    |
|  `00C`  |  4              | Flags.                                                 |
|  `010`  |  8              | Unknown.                                               |
|  `018`  |  8              | Data fork offset (usually 0, beginning of file)        |
|  `020`  |  8              | Size of data fork (usually up to the XMLOffset, below) |
|  `028`  |  8              | Resource fork offset, if any                           |
|  `030`  |  8              | Resource fork length, if any                           |
|  `038`  |  4              | Segment number. Usually 1, may be 0                    |
|  `03C`  |  4              | Segment count. Usually 1, may be 0                     |
|  `040`  |  16             | 128-bit GUID identifier of segment                     |
|  `050`  |  4              | Data fork checksum type                                |
|  `054`  |  4              | Data fork checksum size                                |
|  `058`  |  128            | Data fork checksum                                     |
|  `0D8`  |  8              | Offset of XML property list in DMG, from beginning     |
|  `0E0`  |  8              | Length of XML property list                            |
|  `0E8`  |  120            | Reserved bytes                                         |
|  `160`  |  4              | Master checksum type                                   |
|  `164`  |  4              | Master checksum size                                   |
|  `168`  |  128            | Master checksum                                        |
|  `1E8`  |  4              | Unknown, commonly 1                                    |
|  `1EC`  |  8              | Size of DMG when expanded, in sectors                  |
|  `1F4`  |  12             | Reserved bytes (zeroes)                                |