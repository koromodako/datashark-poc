# MBR Format

## MBR

### Common structure

MBR is always 512-byte long. Many kinds of MBR exists, yet the PPT

|        **element**       | **size** | **value** |
|:-------------------------|:--------:|:---------:|
| Boostrap Code Area       |    440   |   _N/A_   |
| [Signature]              |    4     |   _N/A_   |
| [pad]                    |    2     | `0x0000`  |
| Primary Partitions Table |    64    |   _N/A_   |
| Boot Signature           |    2     | `0x55AA`  |

### Partition Entry

A partition entry in the PPT is 16-byte long and contains the following
information.

|        **element**       | **size** |
|:-------------------------|:--------:|
| Status                   |    1     |
| First Abs. Sector CHS    |    3     |
| Type                     |    1     |
| Last Abs. Sector CHS     |    3     |
| First Abs. Sector LBA    |    4     |
| Number of Sectors        |    4     |

### CHS Addressing

CHS address is the physical addressing of a sector. C, H and S values can be
obtained using the following equations, with CHS a 3-byte value.

```
C = ((CHS >> 6) & 0x300) | (CHS & 0xff)
H = (CHS >> 16) & 0xff
S = (CHS >> 8) & 0x3f
```

### Partition Type

See Appendix I - Partition Type Table

### LBA Addressing

Linear addressing of data blocks.

CHS tuples can be mapped to LBA address with the following formula:

```
LBA = (C * HPC + H) * SPT + (S - 1)
```

where

```
C, H and S are the cylinder number, the head number, and the sector number
LBA is the logical block address
HPC is the maximum number of heads per cylinder (typically 16 for 28-bit LBA)
SPT is the maximum number of sectors per track (typically 63 for 28-bit LBA)
```

LBA addresses can be mapped to CHS tuples with the following formula:

```
C = LBA / (HPC * SPT)
H = (LBA / SPT) mod HPC
S = (LBA mod SPT) + 1
```

# Appendicies

## Appendix I - Partition Type Table

Incomplete list of partition types and the data which can be found inside.

| **ID** | **Description**                                                    |
|:------:|:-------------------------------------------------------------------|
|  `00`  | **can be** Empty partition entry |
|  `01`  | **can be** FAT12 |
|  `02`  | **can be** XENIX root |
|  `03`  | **can be** XENIX usr |
|  `04`  | **can be** FAT16 |
|  `05`  | **can be** Extended partition with CHS |
|  `06`  | **can be** FAT16B _or_ FAT12 _or_ FAT16 |
|  `07`  | **can be** IFS _or_ HPFS _or_ NTFS _or_ exFAT _or_ QNX (`qnx`) |
|  `08`  | **can be** FAT12 _or_ FAT16 _or_ OS/2 _or_ AIX boot/split _or_ QNX (`qny`) |
|  `09`  | **can be** AIX data/boot _or_ QNX (`qnz`) _or_ Coherent file system _or_ OS-9 RBF |
|  `0A`  | **can be** OS/2 Boot Manager _or_ Coherent swap partition |
|  `0B`  | **can be** FAT32 with CHS |
|  `0C`  | **can be** FAT32 with LBA |
|  `0E`  | **can be** FAT16B with LBA |
|  `0F`  | **can be** Extended partition with LBA |
|  `10`  | **can be** _none_ |
|  `11`  | **can be** FAT12 _or_ FAT16 _or_ Hidden FAT12 |
|  `12`  | **can be** bootable FAT
|  `13`  | **?** |
|  `14`  | **can be** FAT12 _or_ FAT16 _or_ Hidden FAT16 _or_ Omega file system |
|  `15`  | **can be** Hidden extended partition with CHS _or_ Swap |
|  `16`  | **can be** Hidden FAT16B |
|  `17`  | **can be** Hidden IFS _or_ Hidden HPFS _or_ Hidden NTFS _or_ Hidden exFAT |
|  `18`  | **can be** AST Zero Volt Suspend or SmartSleep |
|  `19`  | **can be** Willowtech Photon coS |
|  `1B`  | **can be** Hidden FAT32 |
|  `1C`  | **can be** Hidden FAT32 with LBA |
|  `1E`  | **can be** Hidden FAT16 with LBA |
|  `1F`  | **can be** Hidden extended partition with LBA |
|  `20`  | **can be** Windows Mobile update XIP _or_ OFS1 |
|  `21`  | **can be** HP Volume Expansion _or_ FSo2 (Oxygen File System) |
|  `22`  | **can be** Oxygen Extended Partition Table |
|  `23`  | **can be** Windows Mobile boot XIP |
|  `24`  | **can be** FAT12 _or_ FAT16 |
|  `25`  | **can be** Windows Mobile IMGFS |
|  `26`  | **?** |
|  `27`  | **can be** Hidden NTFS partition _or_ MirOS partition _or_ RooterBOOT kernel partition |
|  `2A`  | **can be** AthFS _or_ AFS |
|  `2B`  | **can be** SyllableSecure (SylStor) |
|  `31`  | **?** |
|  `32`  | **?** |
|  `33`  | **?** |
|  `34`  | **?** |
|  `35`  | **can be** JFS (OS/2 implementation of AIX Journaling File system) |
|  `36`  | **?** |
|  `38`  | **can be** THEOS version 3.2, 2 GB partition |
|  `39`  | **can be** Plan 9 edition 3 partition _or_ THEOS version 4 spanned partition |
|  `3A`  | **can be** THEOS version 4, 4 GB partition |
|  `3B`  | **can be** THEOS version 4 extended partition |
|  `3C`  | **can be** PqRP |
|  `3D`  | **can be** Hidden NetWare |
|  `40`  | **can be** PICK R83 _or_ Venix 80286 |
|  `41`  | **can be** Personal RISC Boot _or_ Old Linux/Minix _or_ Power PC Reference Platform Boot |
|  `42`  | **can be** Secure File system (SFS) _or_ Old Linux swap _or_ Dynamic extended partition marker |
|  `43`  | **can be** Old Linux native |
|  `44`  | **can be** Norton GoBack, WildFile GoBack, Adaptec GoBack, Roxio GoBack |
|  `45`  | **can be** Priam _or_ Boot-US boot manager _or_ EUMEL/ELAN (L2) |
|  `46`  | **can be** EUMEL/ELAN (L2) |
|  `47`  | **can be** EUMEL/ELAN (L2) |
|  `48`  | **can be** EUMEL/ELAN (L2), ERGOS L3 |
|  `4A`  | **can be** Aquila _or_ ALFS/THIN |
|  `4C`  | **can be** Aos (A2) file system (76) |
|  `4D`  | **can be** Primary QNX POSIX volume on disk |
|  `4E`  | **can be** Secondary QNX POSIX volume on disk |
|  `4F`  | **can be** Tertiary QNX POSIX volume on disk _or_ Boot / native file system (79) |
|  `50`  | **can be** Alternative native file system (80) _or_ Read-only partition (old) _or_ Lynx RTOS |
|  `51`  | **can be** Read-write partition (Aux 1) |
|  `52`  | **can be** CP/M-80 |
|  `53`  | **can be** Auxiliary 3 (WO)
|  `54`  | **can be** Dynamic Drive Overlay (DDO) |
|  `55`  | **can be** EZ-Drive _or_ Maxtor _or_ MaxBlast _or_ DriveGuide INT 13h redirector volume |
|  `56`  | **can be** FAT12 or FAT16 _or_ Disk Manager partition converted to EZ-BIOS _or_ VFeature partitionned volume |
|  `57`  | **can be** VNDI partition |
|  `5C`  | **can be** Priam EDisk Partitioned Volume |
|  `61`  | **?** |
|  `62`  | **?** |
|  `63`  | **?** |
|  `64`  | **can be** NetWare File System 286/2 _or_ PC-ARMOUR |
|  `65`  | **can be** NetWare File System 386 |
|  `66`  | **can be** NetWare File System 386 _or_ Storage Management Services (SMS) |
|  `67`  | **can be** Wolf Mountain |
|  `68`  | **?** |
|  `69`  | **can be** Novell Storage Services (NSS) |
|  `70`  | **can be** DiskSecure multiboot |
|  `71`  | **?** |
|  `72`  | **can be** APTI alternative FAT12 (CHS, SFN) _or_ V7/x86 |
|  `73`  | **?** |
|  `74`  | **can be** Scramdisk |
|  `75`  | **?** |
|  `76`  | **?** |
|  `77`  | **can be** VNDI _or_ M2FS _or_ M2CS |
|  `78`  | **can be** XOSL bootloader file system |
|  `79`  | **can be** APTI alternative FAT16 (CHS, SFN) |
|  `7A`  | **can be** APTI alternative FAT16 (LBA, SFN) |
|  `7B`  | **can be** APTI alternative FAT16B (CHS, SFN) |
|  `7C`  | **can be** APTI alternative FAT32 (LBA, SFN) |
|  `7D`  | **can be** APTI alternative FAT32 (CHS, SFN) |
|  `7E`  | **can be** Level 2 cache |
|  `7F`  | **can be** Reserved for individual or local use and temporary or experimental projects |
|  `80`  | **can be** MINIX file system (old) |
|  `81`  | **can be** MINIX file system _or_ Mitac Advanced Disk Manager |
|  `82`  | **can be** Linux swap space _or_ Solaris x86 |
|  `83`  | **can be** Any native Linux file system |
|  `84`  | **can be** APM hibernation _or_ Hidden FAT16 _or_ Rapid Start technology |
|  `85`  | **can be** Extended partition with CHS |
|  `86`  | **can be** Fault-tolerant FAT16B mirrored volume set _or_ Linux RAID superblock with auto-detect (old)
|  `87`  | **can be** Fault-tolerant HPFS/NTFS mirrored volume set |
|  `88`  | **can be** Linux plaintext partition table |
|  `8A`  | **can be** Linux kernel image |
|  `8B`  | **can be** Legacy fault-tolerant FAT32 mirrored volume set |
|  `8C`  | **can be** Legacy fault-tolerant FAT32 mirrored volume set |
|  `8D`  | **can be** Hidden FAT12 |
|  `8E`  | **can be** Linux LVM |
|  `90`  | **can be** Hidden FAT16 |
|  `91`  | **can be** Hidden extended partition with CHS |
|  `92`  | **can be** Hidden FAT16B |
|  `93`  | **can be** Amoeba native file system _or_ Hidden Linux file system |
|  `94`  | **can be** Amoeba bad block table |
|  `95`  | **can be** EXOPC native |
|  `96`  | **can be** ISO-9660 file system |
|  `97`  | **can be** Hidden FAT32
|  `98`  | **can be** Hidden FAT32 _or_ bootable FAT |
|  `99`  | **can be** Early Unix |
|  `9A`  | **can be** Hidden FAT16 |
|  `9B`  | **can be** Hidden extended partition with LBA |
|  `9E`  | **can be** ForthOS (eForth port) |
|  `9F`  | **can be** BSDI native file system / swap |
|  `A0`  | **can be** Diagnostic partition for HP laptops _or_ Hibernate partition |
|  `A1`  | **can be** Hibernate partition |
|  `A2`  | **can be** Hard Processor System (HPS) ARM preloader |
|  `A3`  | **?** |
|  `A4`  | **?** |
|  `A5`  | **can be** BSD slice |
|  `A6`  | **can be** OpenBSD slice |
|  `A7`  | **?** |
|  `A8`  | **can be** Apple Darwin, Mac OS X UFS
|  `A9`  | **can be** NetBSD slice |
|  `AA`  | **can be** FAT12 |
|  `AB`  | **can be** Apple Darwin, Mac OS X boot _or_ GO! |
|  `AD`  | **can be** ADFS / FileCore format |
|  `AE`  | **can be** ShagOS file system |
|  `AF`  | **can be** HFS and HFS+ _or_ ShagOS swap |
|  `B0`  | **can be** Boot-Star dummy partition |
|  `B1`  | **can be** QNX Neutrino power-safe file system |
|  `B2`  | **can be** QNX Neutrino power-safe file system |
|  `B3`  | **can be** QNX Neutrino power-safe file system |
|  `B4`  | **?** |
|  `B6`  | **can be** Corrupted fault-tolerant FAT16B mirrored master volume (see C6h and 86h, corresponds with 06h)
|  `B7`  | **can be** BSDI native file system / swap _or_ Corrupted fault-tolerant HPFS/NTFS mirrored master volume (see C7h and 87h, corresponds with 07h)
|  `B8`  | **can be** BSDI swap / native file system |
|  `BB`  | **can be** PTS BootWizard 4 / OS Selector 5 for hidden partitions _or_ OEM Secure Zone _or_ Corrupted fault-tolerant FAT32 mirrored master volume |
|  `BC`  | **can be** Backup Capsule _or_ Acronis Secure Zone _or_ Corrupted fault-tolerant FAT32 mirrored master volume |
|  `BD`  | **?** |
|  `BE`  | **can be** Solaris 8 boot |
|  `BF`  | **can be** Solaris x86 |
|  `C0`  | **can be** Secured FAT partition |
|  `C1`  | **can be** Secured FAT12 |
|  `C2`  | **can be** Hidden Linux native file system |
|  `C3`  | **can be** Hidden Linux swap |
|  `C4`  | **can be** Secured FAT16 |
|  `C5`  | **can be** Secured extended partition with CHS |
|  `C6`  | **can be** Secured FAT16B _or_ Corrupted fault-tolerant FAT16B mirrored slave volume |
|  `C7`  | **can be** Syrinx boot _or_ Corrupted fault-tolerant HPFS/NTFS mirrored slave volume |
|  `C8`  | **?** |
|  `C9`  | **?** |
|  `CA`  | **?** |
|  `CB`  | **can be** Secured FAT32 _or_ Corrupted fault-tolerant FAT32 mirrored slave volume |
|  `CC`  | **can be** Secured FAT32 _or_ Corrupted fault-tolerant FAT32 mirrored slave volume |
|  `CD`  | **can be** CTOS Memory dump |
|  `CE`  | **can be** Secured FAT16B |
|  `CF`  | **can be** Secured extended partition with LBA |
|  `D0`  | **can be** Secured FAT partition |
|  `D1`  | **can be** Secured FAT12 |
|  `D4`  | **can be** Secured FAT16 |
|  `D5`  | **can be** Secured extended partition with CHS |
|  `D6`  | **can be** Secured FAT16B |
|  `D8`  | **can be** CP/M-86 |
|  `DA`  | **can be** Non-file system data _or_ Shielded disk |
|  `DB`  | **can be** SCPU boot image _or_ FAT32 |
|  `DD`  | **can be** Hidden memory dump |
|  `DE`  | **can be** FAT16 |
|  `DF`  | **can be** DG/UX virtual disk manager _or_ EMBRM |
|  `E0`  | **can be** ST AVFS |
|  `E1`  | **can be** Extended FAT12 (> 1023 cylinder) |
|  `E2`  | **can be** DOS read-only (XFDISK) (see E3h) |
|  `E3`  | **can be** DOS read-only (see E2h) |
|  `E4`  | **can be** Extended FAT16 (< 1024 cylinder) |
|  `E5`  | **can be** FAT12 _or_ FAT16 |
|  `E6`  | **?** |
|  `E8`  | **can be** Linux Unified Key Setup (LUKS) |
|  `EB`  | **can be** BFS |
|  `EC`  | **can be** SkyFS |
|  `ED`  | **can be** EDC loader _or_ GPT hybrid MBR |
|  `EE`  | **can be** GPT protective MBR |
|  `EF`  | **can be** EFI system partition _or_ any other FS |
|  `F0`  | **can be** PA-RISC Linux boot loader |
|  `F1`  | **can be** |
|  `F2`  | **can be** FAT12 _or_ FAT16 |
|  `F3`  | **?** |
|  `F4`  | **can be** DOS partition _or_ Single volume partition for NGF _or_ TwinFS |
|  `F5`  | **can be** MD0-MD9 multi volume partition for NGF _or_ TwinFS |
|  `F6`  | **?** |
|  `F7`  | **can be** EFAT _or_ Solid State file system |
|  `F9`  | **can be** ext2/ext3 persistent cache
|  `FA`  | **?** |
|  `FB`  | **can be** VMware VMFS file system partition |
|  `FC`  | **can be** VMware swap / VMKCORE kernel dump partition |
|  `FD`  | **can be** Linux RAID superblock with auto-detect _or_ FreeDOS |
|  `FE`  | **can be** IML partition _or_ PS/2 FAT12 _or_ Disk Administration hidden partition _or_ Old Linux LVM |
|  `FF`  | **can be** XENIX bad block table |
