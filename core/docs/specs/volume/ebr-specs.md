
# EBR

## Structure Description

EBRs have essentially the same structure as the MBR; except only the first two
entries of the partition table are supposed to be used, besides having the
mandatory boot record signature (or magic number) of 0xAA55 at the end of the
sector. This 2-byte signature appears in a disk editor as 0x55 first and 0xAA
last, because IBM-compatible PCs store hexadecimal words in little-endian order.

The partition type of an extended partition is 0x05 (CHS addressing) or 0x0F
(LBA addressing). DR DOS 6.0 and higher support secured extended partitions
using 0xC5, which are invisible to other operating systems. Since
non-LBA-enabled versions of DR-DOS up to including 7.03 do not recognize the
0x0F partition type and other operating systems do not recognize the 0xC5 type,
this can also be utilized to occupy space up to the first 8 GB of the disk for
use under DR-DOS (for logical drives in secured or non-secured partitions), and
still use 0x0F to allocate the remainder of the disk for LBA-enabled operating
systems in a non-conflictive fashion. Similar, Linux supports the concept of a
second extended partition chain with type 0x85 — this type is hidden (unknown)
for other operating systems supporting only one chain. Other extended
partition types which may hold EBRs include the deliberately hidden types 0x15,
0x1F, 0x91 and 0x9B, the access-restricted types 0x5E and 0x5F, and the secured
types 0xCF and 0xD5. However, these should be treated private to the operating
systems and tools supporting them and should not be mounted otherwise.

## Entries Description

The first entry of an EBR partition table points to the logical partition
belonging to that EBR:

Starting sector = relative offset between this EBR sector and the first sector
of the logical partition

Note: This is often the same value for each EBR on the same hard disk; usually
63 for Windows XP or older.

Number of sectors = total count of sectors for this logical partition

Note: Any unused sectors between EBR and logical drive are not considered part
of the logical drive.

The second entry of an EBR partition table will contain zero-bytes if it's the
last EBR in the extended partition; otherwise, it points to the next EBR in the
EBR chain.

Starting sector = relative address of next EBR within extended partition

In other words: Starting sector = LBA address of next EBR minus LBA address of
extended partition's first EBR

Number of sectors = total count of sectors for next logical partition, but
count starts from the next EBR sector

Note: Unlike the first entry in an EBR's partition table, this number of
sectors count includes the next logical partition's EBR sector along with the
other sectors in its otherwise unused track. (Compare Diagram 1 and 2 below.)

## Source

[Look here](https://en.wikipedia.org/wiki/Extended_boot_record)
