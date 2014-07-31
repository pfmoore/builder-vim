Vim Builder
===========

This is my script to build the latest version of vim. It downloads the
vim repository to a temporary direcory, and builds and packages the program
to a ```vim.zip``` file in the current directory.

Local Patches
-------------

The ```patches``` subdirectory contains a series of local patches. The
```patches.ini``` file defines the patches to apply - the ```patches``` section
lists the names of the patches, and each has a section with a ```message```
entry which gives the commit message to use.

Patches must always use Unix line endings. The ```.gitattributes``` file
ensures that all files with extension ```.patch``` will have LF line endings
retained.
