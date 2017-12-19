# FVD Disk Image Format

## Image Format

Below is the layout of an FVD image.

|  **Chunks**  |
|:------------:|
|    Header    |
|    Bitmap    |
|   Journal    |
|    Table     |
| Data Chunk 1 |
| Data Chunk 2 |
|     ...      |

## Header

```
struct FvdHeader {
   uint32_t magic; /* FVD\0 */
   uint32_t version;

   uint64_t virtual_disk_size; /* in bytes. The disk size perceived by VM. */
   uint64_t data_offset; /* in bytes. Where data chunks start. */

   /* Data can be optionally stored in a different file. */
   char data_file[1024];
   char data_file_fmt[16];

   /* Base image. */
   char base_img[1024];
   char base_img_fmt[16];
   uint64_t base_img_size; /* in bytes. */

  /* Bitmap for base image. */
   uint64_t bitmap_offset; /* in bytes. */
   uint64_t bitmap_size; /* in bytes. */
   uint64_t block_size; /* in bytes. One bit represents the state of one block. */

   /* Table for compact image. */
   uint64_t table_offset; /* in bytes. */
   uint64_t table_size; /* in bytes. */
   uint64_t chunk_size; /* in bytes. One table entry maps the address of one chunk. */
   uint64_t storage_grow_unit; /* in bytes. */
   char add_storage_cmd[1024];

   /* Journal */
   uint64_t journal_offset; /* in bytes. */
   uint64_t journal_size; /* in bytes. */
   uint64_t stable_journal_epoch;
   uint32_t clean_shutdown; /* true if the disk was closed gracefully last time. */

   /* Copy-on-read and prefetching. */
   uint32_t copy_on_read; /* true or false */
   uint64_t max_outstanding_copy_on_read_data; /* in bytes. */
   int64_t prefetch_start_delay; /* in seconds. */
   uint32_t base_img_fully_prefetched;
   uint32_t num_prefetch_slots;
   uint64_t bytes_per_prefetch;
   uint64_t prefetch_min_read_throughput; /* in KB/second. */
   uint64_t prefetch_max_read_throughput; /* in KB/second. */
   uint64_t prefetch_min_write_throughput;  /* in KB/second. */
   uint64_t prefetch_max_write_throughput;  /* in KB/second. */
   uint64_t prefetch_throttle_time;
   uint64_t prefetch_read_throughput_measure_time;  /* in milliseconds. */
   uint64_t prefetch_write_throughput_measure_time;  /* in milliseconds. */

   int32_t need_zero_init; /* Support optional bitmap optimization. */
   uint8_t reserved[4096]; /* Future extension. */
} FvdHeader;
```

Explanation of some header fields:

 + `data_file` and `data_file_fmt`. Header, bitmap, table, and journal are
   stored in the FVD file. The data chunks can be stored in the FVD file,
   or optionally stored in a separate data file using any image format. This
   provides several benefits. First, it allows FVD to disable its lookup table
   and use any other image formats to do storage allocation (assuming they are
   better in doing that). Second, e.g., assuming the data file uses the RAW
   format, once prefetching finishes, the FVD file can be discarded (as it is no
   longer needed), and the data file can be treated as a self-contained RAW
   image, which is most efficient and easy to manipulate with existing tools.

 + `storage_grow_unit` and `add_storage_cmd`. When FVD uses the lookup table to
   do storage allocation, `storage_grow_unit` specifies how much additional storage
   space FVD requests from the underlying layer each time. If the image is stored
   on a host file system, `add_storage_cmd` is not needed because the storage space
   is allocated automatically. If the image is stored on a logical volume, e.g.,
   with `storage_grow_unit=5GB`, FVD initially gets 5GB storage space from the logical
   volume manager (LVM) and uses it to host many 1MB chunks. When the first 5GB is
   used up, FVD gets another 5GB, and so forth. Different methods can be used by
   FVD to get additional storage space. The support for growing a logical volume
   using lvextend is built in FVD, but FVD is flexible in that it can invoke any
   external command specified in `add_storage_cmd` to acquire additional storage
   space needed. The external command is invoked as `add_storage_cmd
   storage_grow_unit image_file`, e.g., `/path/add-storage-script.sh 1048576
   /dev/lvm/img1`.

 + `stable_journal_epoch`. FVD maintains a monotonically increasing journal
   epoch number. When a new record is written into the journal, the epoch is
   incremented and the record is annotated with that epoch number. When the
   journal is full, FVD flushes the entire bitmap and the entire lookup table to
   disk, increment epoch, and store it in `stable_journal_epoch`. If the host
   crashes, during the journal recovery process, FVD ignores journal records whose
   epoch numbers are smaller than `stable_journal_epoch`. This feature is needed only
   if the lookup table maps a chunk to different addresses at different times, e.g.,
   FVD relocates a chunk during defragmentation. If FVD never relocates a chunk,
   data integrity is guaranteed even without this feature.

 + `clean_shutdown`. This field is set to false when a VM boots. When the VM
   shuts down gracefully, FVD flushes the entire bitmap and the entire lookup table
   to disk, and resets clean_shutdown to true. When the VM reboots, FVD skips
   journal recovery if clean_shutdown is true.

 + `copy_on_read`. This field controls whether to perform copy-on-read.

 + `max_outstanding_copy_on_read_data`. If not-yet-saved copy-on-read data exceed
   this threshold, which indicates the disk is slow, FVD temporarily halts
   copy-on-read.

 + `prefetch_start_delay`. This field controls when to start prefetching. If the
   value is negative, prefetching is disabled.

 + `base_img_fully_prefetched`. This field is set to true if all data have been
   prefetched from the base image to the FVD image. If `base_img_fully_prefetched`
   is true, copy-on-write, copy-on-read, and prefetching are all disabled as they
   are no longer needed.

 + `num_prefetch_slots`. Prefetching uses a pipeline model. This field specifies
   how many outstanding prefetching requests are allowed.

 + `bytes_per_prefetch`. This field specifies how much data to prefetch each time.

 + `prefetch_min_read_throughput` and `prefetch_max_read_throughput`. They specify
   the min and max throughput of reading data from the base image. If the throughput
   is too low, which indicates a congestion in the network or the disk storing the
   base image, prefetching is paused for a random period of time in `[0,
   prefetch_throttle_time]`, and resumed later.

 + `prefetch_min_write_throughput` and `prefetch_max_write_throughput`. They
   specify the min and max throughput of reading data from the base image. If the
   throughput is too low, which indicates a congestion in the disk storing the FVD
   image, prefetching is paused for a random period of time in `[0,
   prefetch_throttle_time]`, and resumed later.

 + `prefetch_throttle_time`. See above.

 + `prefetch_read_throughput_measure_time` and
   `prefetch_write_throughput_measure_time`. These fields control how long to
   measure the prefetching throughput.

 + `need_zero_init`. This field is related to one optimization in copy-on-write,
   copy-on-read, and adaptive prefetching. Often a base image is a sparse file,
   with many data contents as zeros. When creating a copy-on-write FVD image,
   qemu-img can optionally be told to search for those zero-filled sectors and
   set their corresponding bits in the bitmap. At runtime, FVD behaves as if
   those zero-filled sectors are already in the FVD image and does not read them
   from the base image. This optimization, however, requires that the FVD image is
   stored on a host file system that supports sparse files. If this optimization
   is enabled, `need_zero_init` is set to true and FVD will refuse to open the image
   if the image is stored on a logical volume or a file system that does not
   support sparse files.

## Bitmap

The storage space for the bitmap is preallocated in the image. A bit is 0 if the corresponding block is in the base image, and the bit is 1 if the block is in the FVD image. The default size of a block is 64KB. To represent the state of a 1TB base image, FVD only needs a 2MB bitmap.

## Lookup Table

The storage space for the lookup table is preallocated in the image. One entry in the lookup table maps the virtual disk address of a chunk to an offset in the FVD image where the chunk is stored. The default size of a chunk is 1MB. For a 1TB virtual disk, the size of the lookup table is 4MB.

## Journal

The storage space for the journal is preallocated in the image. The default size of the journal is 16MB. Each sector in the journal is used independently so that it can be updated atomically. A journal sector can contain one or more journal records. Currently, there are two types of journal records, and other types can be added.

```
struct BitmapUpdateRecord {
     uint32_t type;            /* BITMAP_JRECORD = 0x3F2AB8ED */
     uint32_t num_dirty_sectors;
     uint64_t dirty_sector_begin;
}

struct TableUpdateRecord {
     uint32_t type;            /* TABLE_JRECORD = 0xB4E6F7AC */
     uint64_t journal_epoch;
     uint32_t num_dirty_table_entries;
     uint32_t dirty_table_begin;
     uint32_t dirty_table_entries [num_dirty_table_entries];
}
```
