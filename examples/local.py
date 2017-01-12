'''

Use this tutorial to build a DataFS server using MongoDB and the local filesystem


Running this example
--------------------

To run this example:

1. Create a MongoDB server by following the
   `MongoDB's Tutorial <https://docs.mongodb.com/manual/tutorial/>`_
   installation and startup instructions.

2. Start the MongoDB server (e.g. `mongod  --dbpath . --nojournal`)

3. Follow the steps below


Set up the workspace
~~~~~~~~~~~~~~~~~~~~

We need a few things for this example:

.. code-block:: python

    >>> from datafs.managers.manager_mongo import MongoDBManager
    >>> from datafs import DataAPI
    >>> from fs1.osfs import OSFS
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
we'll use a MongoDB manager. Make sure you have a MongoDB
server running, then create a MongoDBManager instance:

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

Now we need a storage service. DataFS is designed to be
used with remote storage (S3, FTP, etc), but it can also
be run on your local filesystem. In this tutorial we'll
use a local service.

First, let's create a temporary filesystem to use for this
example:

.. code-block:: python

    >>> temp = tempfile.mkdtemp()
    >>> local = OSFS(temp)

We attach this file to the api and give it a name:

.. code-block:: python

    >>> api.attach_authority('local', local)
    >>> api.default_authority # doctest: +ELLIPSIS
    <DataService:OSFS object at ...>

Create archives
~~~~~~~~~~~~~~~

Next we'll create our first archive. An archive must
have an archive_name. In addition, you can supply any
additional keyword arguments, which will be stored as
metadata. To suppress errors on re-creation, use the
``raise_on_err=False`` flag.

.. code-block:: python

    >>> api.create(
    ...     'my_first_archive',
    ...     metadata = dict(description = 'My test data archive'))
    <DataArchive local://my_first_archive>


Retrieve archive metadata
~~~~~~~~~~~~~~~~~~~~~~~~~

Now that we have created an archive, we can retrieve it
from anywhere as long as we have access to the correct
service. When we retrieve the archive, we can see the
metadata that was created when it was initialized.

.. code-block:: python

    >>> var = api.get_archive('my_first_archive')

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

    >>> var.update('test.txt', remove=True)

This file just got sent into our archive! And we deleted the
local copy:

.. code-block:: python

    >>> os.path.isfile('test.txt')
    False

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
    ...


Retrieving the latest version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now let's make sure we're getting the latest version:

.. code-block:: python

    >>> with var.open('r') as f:
    ...     print(f.read())
    ...
    this is the next test

Looks good!

Cleaning up
~~~~~~~~~~~

.. code-block:: python

    >>> var.delete()
    >>> api.manager.delete_table('DataFiles')
    >>> shutil.rmtree(temp)


Next steps
~~~~~~~~~~

The :ref:`next tutorial <examples-aws>` describes setting up DataFS for remote obejct stores, such as with AWS storage.

'''
