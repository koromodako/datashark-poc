# ISO/IMG/UDF Image Formats

There is no standard definition for ISO image files. ISO disc images are 
uncompressed and do not use a particular container format; they are a 
sector-by-sector copy of the data on an optical disc, stored inside a binary 
file. ISO images are expected to contain the binary image of an optical media 
file system (usually ISO 9660 and its extensions or UDF), including the data in 
its files in binary format, copied exactly as they were stored on the disc. The 
data inside the ISO image will be structured according to the file system that 
was used on the optical disc from which it was created.

ISO files store only the user data from each sector on an optical disc, 
ignoring the control headers and error correction data, and are therefore 
slightly smaller than a raw disc image of optical media. Since the size of the 
user data portion of a sector (logical sector) in data optical discs is 2,048 
bytes, the size of an ISO image will be a multiple of 2,048.

The .iso file extension is the one most commonly used for this type of disc 
images. The .img extension can also be found on some ISO image files, such as 
in some images from Microsoft DreamSpark; however, IMG files, which also use 
the .img extension, tend to have slightly different contents. The .udf file 
extension is sometimes used to indicate that the file system inside the ISO 
image is actually UDF and not ISO 9660.

Any single-track CD-ROM, DVD or Blu-ray disc can be archived in ISO format as a 
true digital copy of the original. Unlike a physical optical disc, an image can 
be transferred over any data link or removable storage medium. An ISO image can 
be opened with almost every multi-format file archiver. Native support for 
handling ISO images varies from operating system to operating system.

_source: [https://en.wikipedia.org/wiki/ISO_image](https://en.wikipedia.org/wiki/ISO_image)_
