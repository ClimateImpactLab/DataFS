.. _examples-other:

Using Other Services
====================

Because the file operations in DataFS are backed by pyFilesystem, DataFS supports any of the following remote storage services:


:FTP:
    
    An interface to FTP servers. See :py:mod:`fs.ftpfs`

:Memory:
    
    A filesystem that exists entirely in memory. See :py:mod:`fs.memoryfs`

:OS:
    
    An interface to the OS Filesystem. See :py:mod:`fs.osfs`

:RPCFS:
    
    An interface to a file-system served over XML RPC, See :py:mod:`fs.rpcfs` and :py:mod:`fs.expose.xmlrpc`

:SFTP:
    
    A secure FTP filesystem. See :py:mod:`fs.sftpfs`

:S3:
    
    A filesystem to access an Amazon S3 service. See :py:mod:`fs.s3fs`

:Temporary:
    
    Creates a temporary filesystem in an OS provided location. See :py:mod:`fs.tempfs`

:Zip:
    
    An interface to zip files. See :py:mod:`fs.zipfs`

