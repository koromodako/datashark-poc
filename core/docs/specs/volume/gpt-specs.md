# GPT Format

## Partition Table Header

| **Size** | **Content**                                                                                                                 |
|:--------:|:----------------------------------------------------------------------------------------------------------------------------|
|    8     | Signature ("EFI PART", 45h 46h 49h 20h 50h 41h 52h 54h or 0x5452415020494645ULL[a] on little-endian machines)               |
|    4     | Revision (for GPT version 1.0 (through at least UEFI version 2.7 (May 2017)), the value is 00h 00h 01h 00h)                 |
|    4     | Header size in little endian (in, usually 5Ch 00h 00h 00h or 92)                                                            |
|    4     | CRC32/zlib of header (offset +0 up to header size) in little endian, with this field zeroed during calculation              |
|    4     | Reserved; must be zero                                                                                                      |
|    8     | Current LBA (location of this header copy)                                                                                  |
|    8     | Backup LBA (location of the other header copy)                                                                              |
|    8     | First usable LBA for partitions (primary partition table last LBA + 1)                                                      |
|    8     | Last usable LBA (secondary partition table first LBA - 1)                                                                   |
|    16    | Disk GUID (also referred as UUID on UNIXes)                                                                                 |
|    8     | Starting LBA of array of partition entries (always 2 in primary copy)                                                       |
|    4     | Number of partition entries in array                                                                                        |
|    4     | Size of a single partition entry (usually 80h or 128)                                                                       |
|    4     | CRC32/zlib of partition array in little endian                                                                              |
|    *     | Reserved; must be zeroes for the rest of the block (420 for a sector size of 512; but can be more with larger sector sizes) |

## Partition Entry

| **Size** | **Content**                                     |
|:--------:|:------------------------------------------------|
|    16    | Partition type GUID                             |
|    16    | Unique partition GUID                           |
|    8     | First LBA (little endian)                       |
|    8     | Last LBA (inclusive, usually odd)               |
|    8     | Attribute flags (e.g. bit 60 denotes read-only) |
|    72    | Partition name (36 UTF-16LE code units)         |

### Partition attributes

| **Bit** | **Content**                                                                                                                                                 |
|:-------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------|
|  0      | Platform required (required by the computer to function properly, OEM partition for example, disk partitioning utilities must preserve the partition as is) |
|  1      | EFI firmware should ignore the content of the partition and not try to read from it                                                                         |
|  2      | Legacy BIOS bootable (equivalent to active flag (typically bit 7 set) at offset +0h in partition entries of the MBR partition table)[9]                     |
|  3–47   | Reserved for future use                                                                                                                                     |
|  48–63  | Defined and used by the individual partition type                                                                                                           |

### Basic data partition attributes

| **Bit** | **Content**                             |
|:-------:|:----------------------------------------|
|   60    | Read-only                               |
|   61    | Shadow copy (of another partition)      |
|   62    | Hidden                                  |
|   63    | No drive letter (i.e. do not automount) |

### ChromeOS kernel partition attributes

| **Bit** | **Content**                                           |
|:-------:|:------------------------------------------------------|
| 56      | Successful Boot Flag                                  |
| 55-52   | Tries Remaining                                       |
| 51-48   | Priority (15 = highest, 1 = lowest, 0 = not bootable) |

## Partition Types

|  **OS**     | **Content Type**                     |                 **GUID**               |
|:-----------:|:-------------------------------------|:--------------------------------------:|
|   _none_    | Unused entry                         | `00000000-0000-0000-0000-000000000000` |
|   _none_    | MBR partition scheme                 | `024DEE41-33E7-11D3-9D69-0008C781F39F` |
|   _none_    | EFI System partition                 | `C12A7328-F81F-11D2-BA4B-00A0C93EC93B` |
|   _none_    | BIOS boot partition                  | `21686148-6449-6E6F-744E-656564454649` |
|   _none_    | iFFS partition                       | `D3BFE2DE-3DAF-11DF-BA40-E3A556D89593` |
|   _none_    | Sony boot partition                  | `F4019732-066E-4E12-8273-346C5641494F` |
|   _none_    | Lenovo boot partition                | `BFBFAFE7-A34F-448A-9A5B-6213EB736C22` |
|   Windows   | Microsoft Reserved Partition         | `E3C9E316-0B5C-4DB8-817D-F92DF00215AE` |
|   Windows   | Basic data partition                 | `EBD0A0A2-B9E5-4433-87C0-68B6B72699C7` |
|   Windows   | LDM metadata partition               | `5808C8AA-7E8F-42E0-85D2-E1E90434CFB3` |
|   Windows   | LDM data partition                   | `AF9B60A0-1431-4F62-BC68-3311714A69AD` |
|   Windows   | Windows Recovery Environment         | `DE94BBA4-06D1-4D40-A16A-BFD50179D6AC` |
|   Windows   | IBM GPFS partition                   | `37AFFC90-EF7D-4E96-91C3-2D7AE055B174` |
|   Windows   | Storage Spaces partition             | `E75CAF8F-F680-4CEE-AFA3-B001E56EFC2D` |
|    HP-UX    | Data partition                       | `75894C1E-3AEB-11D3-B7C1-7B03A0000000` |
|    HP-UX    | Service Partition                    | `E2A1E728-32E3-11D6-A682-7B03A0000000` |
|    Linux    | Linux filesystem data                | `0FC63DAF-8483-4772-8E79-3D69D8477DE4` |
|    Linux    | RAID partition                       | `A19D880F-05FC-4D3B-A006-743F0F84911E` |
|    Linux    | Root partition (x86)                 | `44479540-F297-41B2-9AF7-D131D5F0458A` |
|    Linux    | Root partition (x86-64)              | `4F68BCE3-E8CD-4DB1-96E7-FBCAF984B709` |
|    Linux    | Root partition (32-bit ARM)          | `69DAD710-2CE4-4E3C-B16C-21A1D49ABED3` |
|    Linux    | Root partition (64-bit ARM/AArch64)  | `B921B045-1DF0-41C3-AF44-4C6F280D3FAE` |
|    Linux    | Swap partition                       | `0657FD6D-A4AB-43C4-84E5-0933C84B4F4F` |
|    Linux    | LVM partition                        | `E6D6D379-F507-44C2-A23C-238F2A3DF928` |
|    Linux    | /home partition                      | `933AC7E1-2EB4-4F13-B844-0E14E2AEF915` |
|    Linux    | /srv (server data) partition         | `3B8F8425-20E0-4F3B-907F-1A25A76F98E8` |
|    Linux    | Plain dm-crypt partition             | `7FFEC5C9-2D00-49B7-8941-3EA10A5586B7` |
|    Linux    | LUKS partition                       | `CA7D7CCB-63ED-4C53-861C-1742536059CC` |
|    Linux    | Reserved                             | `8DA63339-0007-60C0-C436-083AC8230908` |
|    Linux    | Boot partition                       | `83BD6B9D-7F41-11DC-BE0B-001560B84F0F` |
|    Linux    | Data partition                       | `516E7CB4-6ECF-11D6-8FF8-00022D09712B` |
|    Linux    | Swap partition                       | `516E7CB5-6ECF-11D6-8FF8-00022D09712B` |
|    Linux    | UFS partition                        | `516E7CB6-6ECF-11D6-8FF8-00022D09712B` |
|    Linux    | Vinum volume manager partition       | `516E7CB8-6ECF-11D6-8FF8-00022D09712B` |
|    Linux    | ZFS partition                        | `516E7CBA-6ECF-11D6-8FF8-00022D09712B` |
|     Mac     | HFS+ partition                       | `48465300-0000-11AA-AA11-00306543ECAC` |
|     Mac     | Apple APFS                           | `7C3457EF-0000-11AA-AA11-00306543ECAC` |
|     Mac     | Apple UFS container                  | `55465300-0000-11AA-AA11-00306543ECAC` |
|     Mac     | ZFS                                  | `6A898CC3-1DD2-11B2-99A6-080020736631` |
|     Mac     | Apple RAID partition                 | `52414944-0000-11AA-AA11-00306543ECAC` |
|     Mac     | Apple RAID partition, offline        | `52414944-5F4F-11AA-AA11-00306543ECAC` |
|     Mac     | Apple Boot partition (Recovery HD)   | `426F6F74-0000-11AA-AA11-00306543ECAC` |
|     Mac     | Apple Label                          | `4C616265-6C00-11AA-AA11-00306543ECAC` |
|     Mac     | Apple TV Recovery partition          | `5265636F-7665-11AA-AA11-00306543ECAC` |
|     Mac     | Lion FileVault partition             | `53746F72-6167-11AA-AA11-00306543ECAC` |
|     Mac     | SoftRAID_Status                      | `B6FA30DA-92D2-4A9A-96F1-871EC6486200` |
|     Mac     | SoftRAID_Scratch                     | `2E313465-19B9-463F-8126-8A7993773801` |
|     Mac     | SoftRAID_Volume                      | `FA709C7E-65B1-4593-BFD5-E71D61DE9B02` |
|     Mac     | SoftRAID_Cache                       | `BBBA6DF5-F46F-4A89-8F59-8765B2727503` |
|   Solaris   | Boot partition                       | `6A82CB45-1DD2-11B2-99A6-080020736631` |
|   Solaris   | Root partition                       | `6A85CF4D-1DD2-11B2-99A6-080020736631` |
|   Solaris   | Swap partition                       | `6A87C46F-1DD2-11B2-99A6-080020736631` |
|   Solaris   | Backup partition                     | `6A8B642B-1DD2-11B2-99A6-080020736631` |
|   Solaris   | /usr partition                       | `6A898CC3-1DD2-11B2-99A6-080020736631` |
|   Solaris   | /var partition                       | `6A8EF2E9-1DD2-11B2-99A6-080020736631` |
|   Solaris   | /home partition                      | `6A90BA39-1DD2-11B2-99A6-080020736631` |
|   Solaris   | Alternate sector                     | `6A9283A5-1DD2-11B2-99A6-080020736631` |
|   Solaris   | Reserved partition                   | `6A945A3B-1DD2-11B2-99A6-080020736631` |
|   Solaris   | Reserved partition                   | `6A9630D1-1DD2-11B2-99A6-080020736631` |
|   Solaris   | Reserved partition                   | `6A980767-1DD2-11B2-99A6-080020736631` |
|   Solaris   | Reserved partition                   | `6A96237F-1DD2-11B2-99A6-080020736631` |
|   Solaris   | Reserved partition                   | `6A8D2AC7-1DD2-11B2-99A6-080020736631` |
|    NetBSD   | Swap partition                       | `49F48D32-B10E-11DC-B99B-0019D1879648` |
|    NetBSD   | FFS partition                        | `49F48D5A-B10E-11DC-B99B-0019D1879648` |
|    NetBSD   | LFS partition                        | `49F48D82-B10E-11DC-B99B-0019D1879648` |
|    NetBSD   | RAID partition                       | `49F48DAA-B10E-11DC-B99B-0019D1879648` |
|    NetBSD   | Concatenated partition               | `2DB519C4-B10F-11DC-B99B-0019D1879648` |
|    NetBSD   | Encrypted partition                  | `2DB519EC-B10F-11DC-B99B-0019D1879648` |
|  ChromeOS   | ChromeOS kernel                      | `FE3A2A5D-4F32-41A7-B725-ACCC3285A309` |
|  ChromeOS   | ChromeOS rootfs                      | `3CB8E202-3B7E-47DD-8A3C-7FF2A13CFCEC` |
|  ChromeOS   | ChromeOS future use                  | `2E0A753D-9E48-43B0-8337-B15192CB1B5E` |
|    Haiku    | Haiku BFS                            | `42465331-3BA3-10F1-802A-4861696B7521` |
| MidnightBSD | Boot partition                       | `85D5E45E-237C-11E1-B4B3-E89A8F7FC3A7` |
| MidnightBSD | Data partition                       | `85D5E45A-237C-11E1-B4B3-E89A8F7FC3A7` |
| MidnightBSD | Swap partition                       | `85D5E45B-237C-11E1-B4B3-E89A8F7FC3A7` |
| MidnightBSD | UFS partition                        | `0394EF8B-237E-11E1-B4B3-E89A8F7FC3A7` |
| MidnightBSD | Vinum volume manager partition       | `85D5E45C-237C-11E1-B4B3-E89A8F7FC3A7` |
| MidnightBSD | ZFS partition                        | `85D5E45D-237C-11E1-B4B3-E89A8F7FC3A7` |
|    Ceph     | Journal                              | `45B0969E-9B03-4F30-B4C6-B4B80CEFF106` |
|    Ceph     | dm-crypt journal                     | `45B0969E-9B03-4F30-B4C6-5EC00CEFF106` |
|    Ceph     | OSD                                  | `4FBD7E29-9D25-41B8-AFD0-062C0CEFF05D` |
|    Ceph     | dm-crypt OSD                         | `4FBD7E29-9D25-41B8-AFD0-5EC00CEFF05D` |
|    Ceph     | Disk in creation                     | `89C57F98-2FE5-4DC0-89C1-F3AD0CEFF2BE` |
|    Ceph     | dm-crypt disk in creation            | `89C57F98-2FE5-4DC0-89C1-5EC00CEFF2BE` |
|    Ceph     | Block                                | `CAFECAFE-9B03-4F30-B4C6-B4B80CEFF106` |
|    Ceph     | Block DB                             | `30CD0809-C2B2-499C-8879-2D6B78529876` |
|    Ceph     | Block write-ahead log                | `5CE17FCE-4087-4169-B7FF-056CC58473F9` |
|    Ceph     | Lockbox for dm-crypt keys            | `FB3AABF9-D25F-47CC-BF5E-721D1816496B` |
|    Ceph     | Multipath OSD                        | `4FBD7E29-8AE0-4982-BF9D-5A8D867AF560` |
|    Ceph     | Multipath journal                    | `45B0969E-8AE0-4982-BF9D-5A8D867AF560` |
|    Ceph     | Multipath block                      | `CAFECAFE-8AE0-4982-BF9D-5A8D867AF560` |
|    Ceph     | Multipath block                      | `7F4A666A-16F3-47A2-8445-152EF4D03F6C` |
|    Ceph     | Multipath block DB                   | `EC6D6385-E346-45DC-BE91-DA2A7C8B3261` |
|    Ceph     | Multipath block write-ahead log      | `01B41E1B-002A-453C-9F17-88793989FF8F` |
|    Ceph     | dm-crypt block                       | `CAFECAFE-9B03-4F30-B4C6-5EC00CEFF106` |
|    Ceph     | dm-crypt block DB                    | `93B0052D-02D9-4D8A-A43B-33A3EE4DFBC3` |
|    Ceph     | dm-crypt block write-ahead log       | `306E8683-4FE2-4330-B7C0-00A917C16966` |
|    Ceph     | dm-crypt LUKS journal                | `45B0969E-9B03-4F30-B4C6-35865CEFF106` |
|    Ceph     | dm-crypt LUKS block                  | `CAFECAFE-9B03-4F30-B4C6-35865CEFF106` |
|    Ceph     | dm-crypt LUKS block DB               | `166418DA-C469-4022-ADF4-B30AFD37F176` |
|    Ceph     | dm-crypt LUKS block write-ahead log  | `86A32090-3647-40B9-BBBD-38D8C573AA86` |
|    Ceph     | dm-crypt LUKS OSD                    | `4FBD7E29-9D25-41B8-AFD0-35865CEFF05D` |
|  OpenBSD    | Data partition                       | `824CC7A0-36A8-11E3-890A-952519AD3F61` |
|    QNX      | Power-safe (QNX6) file system        | `CEF5A9AD-73BC-4601-89F3-CDEEEEE321A1` |
|   Plan 9    | Plan 9 partition                     | `C91818F9-8025-47AF-89D2-F030D7000C2C` |
| VMware ESX  | vmkcore (coredump partition)         | `9D275380-40AD-11DB-BF97-000C2911D1B8` |
| VMware ESX  | VMFS filesystem partition            | `AA31E02A-400F-11DB-9590-000C2911D1B8` |
| VMware ESX  | VMware Reserved                      | `9198EFFC-31C0-11DB-8F78-000C2911D1B8` |
| Android-IA  | Bootloader                           | `2568845D-2332-4675-BC39-8FA5A4748D15` |
| Android-IA  | Bootloader2                          | `114EAFFE-1552-4022-B26E-9B053604CF84` |
| Android-IA  | Boot                                 | `49A4D17F-93A3-45C1-A0DE-F50B2EBE2599` |
| Android-IA  | Recovery                             | `4177C722-9E92-4AAB-8644-43502BFD5506` |
| Android-IA  | Misc                                 | `EF32A33B-A409-486C-9141-9FFB711F6266` |
| Android-IA  | Metadata                             | `20AC26BE-20B7-11E3-84C5-6CFDB94711E9` |
| Android-IA  | System                               | `38F428E6-D326-425D-9140-6E0EA133647C` |
| Android-IA  | Cache                                | `A893EF21-E428-470A-9E55-0668FD91A2D9` |
| Android-IA  | Data                                 | `DC76DDA9-5AC1-491C-AF42-A82591580C0D` |
| Android-IA  | Persistent                           | `EBC597D0-2053-4B15-8B64-E0AAC75F4DB1` |
| Android-IA  | Vendor                               | `C5A0AEEC-13EA-11E5-A1B1-001E67CA0C3C` |
| Android-IA  | Config                               | `BD59408B-4514-490D-BF12-9878D963F378` |
| Android-IA  | Factory                              | `8F68CC74-C5E5-48DA-BE91-A0C8C15E9C80` |
| Android-IA  | Factory (alt)                        | `9FDAA6EF-4B3F-40D2-BA8D-BFF16BFB887B` |
| Android-IA  | Fastboot / Tertiary                  | `767941D0-2085-11E3-AD3B-6CFDB94711E9` |
| Android-IA  | OEM                                  | `AC6D7924-EB71-4DF8-B48D-E267B27148FF` |
|    ONIE     | Boot                                 | `7412F7D5-A156-4B13-81DC-867174929325` |
|    ONIE     | Config                               | `D4E6E2CD-4469-46F3-B5CB-1BFF57AFC149` |
|  PowerPC    | PReP boot                            | `9E1A2D38-C612-4316-AA26-8B49521E5A8B` |
| Linux, etc. | Shared boot loader configuration     | `BC13C2FF-59E6-4262-A352-B275FD6F7172` |
|  Atari TOS  | Basic data partition (GEM, BGM, F32) | `734E5AFE-F61A-11E6-BC64-92361F002671` |
