'''

Use this tutorial to build a DataFS server system using MongoDB and a Simple
Storage Service such as AWS's S3.


Running this example
--------------------

To run this example:

1. Create a MongoDB server by following the
   `MongoDB's Tutorial <https://docs.mongodb.com/manual/tutorial/>`_
   installation and startup instructions.

2. Start the MongoDB server (e.g. ``mongod  --dbpath . --nojournal``)

3. Follow the steps below


Set up the workspace
~~~~~~~~~~~~~~~~~~~~

We need a few things for this example:

.. code-block:: python

    >>> from datafs.managers.manager_mongo import MongoDBManager
    >>> from datafs import DataAPI
    >>> from fs.tempfs import TempFS
    >>> import os
    >>> import tempfile
    >>> import shutil
    >>>
    >>> # overload unicode for python 3 compatability:
    >>>
    >>> try:
    ...     unicode = unicode
    ... except NameError:
    ...     unicode = str


This time, we'll import PyFilesystem's S3 Filesystem abstraction:

.. code-block:: python

    >>> from fs.s3fs import S3FS

Additionally, you'll need MongoDB and pymongo installed
and a MongoDB instance running.

Create an API
~~~~~~~~~~~~~

Begin by creating an API instance:

.. code-block:: python

    >>> api = DataAPI(
    ...      username='My Name',
    ...      contact = 'my.email@example.com')


Attach Manager
~~~~~~~~~~~~~~~

Next, we'll choose an archive manager. DataFS currently
supports MongoDB and DynamoDB managers. In this example
we'll use a local MongoDB manager. Make sure you have
a MongoDB server running, then create a
MongoDBManager instance:

.. code-block:: python

    >>> manager = MongoDBManager(
    ...     database_name = 'MyDatabase',
    ...     table_name = 'DataFiles')

If this is the first time you've set up this database, you'll need to create a
table:

.. code-block:: python

    >>> manager.create_archive_table('DataFiles', raise_on_err=False)


All set. Now we can attach the manager to our DataAPI object:

.. code-block:: python

    >>> api.attach_manager(manager)


Attach Service
~~~~~~~~~~~~~~

Now we need a storage service. Let's attach the S3FS
filesystem we imported:

.. code-block:: python

    >>> s3 = S3FS(
    ...     'test-bucket',
    ...     aws_access_key='MY_KEY',
    ...     aws_secret_key='MY_SECRET_KEY')
    >>>
    >>> api.attach_authority('aws', s3)

Create archives
~~~~~~~~~~~~~~~

Now we can create our first archive. An archive must
have an archive_name. In addition, you can supply any
additional keyword arguments, which will be stored as
metadata. To suppress errors on re-creation, use the
``raise_on_err=False`` flag.

.. code-block:: python

    >>> api.create(
    ...     'my_remote_archive',
    ...     metadata = dict(description = 'My test data archive'))
    <DataArchive aws://my_remote_archive>


View all available archives
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's see what archives we have available to us.

.. code-block:: python

    >>> api.list() # doctest: +SKIP
    ['my_remote_archive']


Retrieve archive metadata
~~~~~~~~~~~~~~~~~~~~~~~~~

Now that we have created an archive, we can retrieve it
from anywhere as long as we have access to the correct
service. When we retrieve the archive, we can see the
metadata that was created when it was initialized.

.. code-block:: python

    >>> var = api.get_archive('my_remote_archive')

We can access the metadata for this archive through the archive's 
:py:meth:`~datafs.core.DataArchive.get_metadata` method:

.. code-block:: python

    >>> print(var.get_metadata()['description'])
    My test data archive

Add a file to the archive
~~~~~~~~~~~~~~~~~~~~~~~~~

An archive is simply a versioned history of data files.
So let's get started adding data!

First, we'll create a local file, ``test.txt``, and put
some data in it:

.. code-block:: python

    >>> with open('test.txt', 'w+') as f:
    ...     f.write('this is a test')

Now we can add this file to the archive:

.. code-block:: python

    >>> var.update('test.txt')

This file just got sent into our archive! Now we can delete the local copy:

.. code-block:: python

    >>> os.remove('test.txt')

Reading from the archive
~~~~~~~~~~~~~~~~~~~~~~~~

Next we'll read from the archive. That file object returned by
``var.open()`` can be read just like a regular file

.. code-block:: python

    >>> with var.open('r') as f:
    ...     print(f.read())
    ...
    this is a test

Updating the archive
~~~~~~~~~~~~~~~~~~~~

Open the archive and write to the file:

.. code-block:: python

    >>> with var.open('w+') as f:
    ...     res = f.write(unicode('this is the next test'))


Retrieving the latest version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now let's make sure we're getting the latest version:

.. code-block:: python

    >>> with var.open() as f:
    ...     print(f.read())
    ...
    this is the next test

Looks good!




Cleaning up
~~~~~~~~~~~

.. code-block:: python

    >>> var.delete()
    >>> api.manager.delete_table('DataFiles')


Next steps
~~~~~~~~~~

:ref:`examples-other` describes setting up DataFS for
other filesystems, such as sftp or http.

'''
