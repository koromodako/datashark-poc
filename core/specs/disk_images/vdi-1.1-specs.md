# VDI 1.1 Specs

_source : [https://forums.virtualbox.org/viewtopic.php?t=8046](https://forums.virtualbox.org/viewtopic.php?t=8046)_

## How are VDI files structured?

All VDIs essentially have the same structure. The VDI has four sections:

 + A Standard header descriptor [512 bytes]

 + An image block map. If the (maximum) size of the virtual HDD is N MByte,
   then this map is 4N bytes long.

 + Block alignment padding. The header format allows for padding between the
   image block map and the image blocks, and (as of version 1.6.2) the
   CreateVDI function adds padding after the map to ensure that the first
   image block begins on a 512byte sector boundary. Since the allocation unit
   on both NTFS and Ext3 file systems is 4096 bytes, you will therefore get
   slightly better performance (typically a few %) if you make your VDIs
   (1024N – 128) MByte long.

 + Up to N x 1MByte image blocks.

## What’s in the Header Descriptor

```
0000      3C 3C 3C 20 53 75 6E 20 78 56 4D 20 56 69 72 74    <<< Sun xVM Virt
0010      75 61 6C 42 6F 78 20 44 69 73 6B 20 49 6D 61 67    ualBox Disk Imag
0020      65 20 3E 3E 3E 0A 00 00 00 00 00 00 00 00 00 00    e >>>
0030      00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00

0040      7F 10 DA BE                                        Image Signature
                      01 00 01 00                            Version 1.1
                                  90 01 00 00                Size of Header(0x190)
                                              01 00 00 00    Image Type (Dynamic VDI)
0050      00 00 00 00                                        Image Flags
                      00 00 00 00 00 00 00 00 00 00 00 00    Image Description
0060-001F 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0150      00 00 00 00
                      00 02 00 00                            offsetBlocks
                                  00 20 00 00                offsetData
                                              00 00 00 00    #Cylinders (0)
0160      00 00 00 00                                        #Heads (0)
                      00 00 00 00                            #Sectors (0)
                                  00 02 00 00                SectorSize (512)
                                              00 00 00 00     -- unused --
0170      00 00 00 78 00 00 00 00                            DiskSize (Bytes)
                                  00 00 10 00                BlockSize
                                              00 00 00 00    Block Extra Data (0)
0180      80 07 00 00                                        #BlocksInHDD
                      0B 02 00 00                            #BlocksAllocated
                                  5A 08 62 27 A8 B6 69 44    UUID of this VDI
0190      A1 57 E2 B2 43 A5 8F CB
                                  0C 5C B1 E3 C5 73 ED 40    UUID of last SNAP
01A0      AE F7 06 D6 20 69 0C 96
                                  00 00 00 00 00 00 00 00    UUID link
01B0      00 00 00 00 00 00 00 00
                                  00 00 00 00 00 00 00 00    UUID Parent
01C0      00 00 00 00 00 00 00 00
                                  CF 03 00 00 00 00 00 00    -- garbage / unused --
01D0      3F 00 00 00 00 02 00 00 00 00 00 00 00 00 00 00    -- garbage / unused --
01E0      00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00    -- unused --
01F0      00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00    -- unused –
```

## So how are virtual bytes in my Virtual HDD mapped into physical bytes in my VDI?

The underlying virtual HDD is divided into 1 Mbyte pages. These are mapped onto
image blocks in the VDI. Remember that the zeroth image block starts at an
offset and that all image blocks are 1Mbyte long. Any virtual HDD byte address
is converted into a block number and block offset. The block number is then
mapped to a physical image block in the VDI file by means of the image block
mapping table, so for byte Z in the virtual HDD:

 + Hsize = 512 + 4N + (508 + 4N) mod 512
 + Zblock = int( Z / BlockSize )
 + Zoffset = Z mod BlockSize
 + Fblock = IndexMap[Zblock]
 + Fposition = Hsize + ( Fblock * BlockSize ) + ZOffset

However the VDI can be sparse. What this means is that zero blocks (that is
1Mbytes of 0x00) may not be allocated. In such a case, the image map entry is
set to -1, and this tells the driver that the corresponding block is not
allocated. Reading from an unallocated block returns zeros. If you write to an
unallocated block then a new block is allocated at the end of the VDI with the
rest of it filled with zeros. Note that this map is small in size (40 Kbytes in
the case of a 10 GByte VDI), so all such VDI maps and VDI header info are
cached into the VMM memory, so this translation of virtual addresses into
physical addresses does not incur additional read/write operations except in
the relatively rare case where the I/O transfer cuts across a 1Mbyte boundary).

 + In the case of a dynamic VDI (Type 1) as “new” 1Mbyte blocks in the virtual
   HDD are written to, these are mapped to new 1Mbyte blocks which are
   allocated at the end of the VDI file; that is a dynamic VDI is initially
   ordered in chronological not physical order. The initial size of an N Mbyte
   dynamic VDI is 512+4N+F bytes with all N image map entries set to -1.
   F = (508+4N) mod 512, that is the packing necessary to round up to a sector
   boundary.

 + In the case of a static (Type 2) VDI all blocks are pre-allocated so no
   dynamic allocation is necessary. The create utility also writes zeros to the
   entire file because many file systems themselves adopt a just-in-time
   allocation policy. The initial size of an N Mbyte static VDI is
   512+4N+F+1048576N bytes, where F is as in the dynamic case.

The pros and cons of deciding whether choosing whether to use a static or
dynamic VDI are complex. Static drives are fragmentation free at a file level,
and since you also take the ‘pain’ of file allocation up-front in one hit, you
know that you aren’t going to have continuous growth of your VDIs slowly
filling up your host file system. VirtualBox recommend the use of static VDIs
primarily because fragmentation can degrade performance. I personally disagree
and prefer using dynamic VDIs myself for the following reasons:

 + If you are going to use your VDI as an immutable drive or a baseline for
   snapshots, then there is little point in allocating space that is never
   going to be written to, so why waste the HDD space?

 + As long as your process for creating the disk in the first place is not too
   fragmented then the more compact dynamic VDI will actually give you better
   performance. (I now defragment the dynamic VDIs that I am going to use, and
   I’ve posted the utility I use in this topic: Example VDI Defragmentation
   Utility.)
