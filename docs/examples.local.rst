
.. _tutorial-local:

Using DataFS Locally
====================

:download:`example: local.py <../examples/local.py>`

.. automodule:: examples.local

Creating your own DataFS Archive
--------------------------------

Set up the workspace
~~~~~~~~~~~~~~~~~~~~

We need a few things for this example:

.. code-block:: python

    >>> from datafs import DataAPI
    >>> import os

Additionally, you'll need MongoDB and pymongo installed and a MongoDB instance running.


Create an API
~~~~~~~~~~~~~

Begin by creating an API instance:
    
.. code-block:: python
    
    >>> api = DataAPI(
    ...     username='My Name',
    ...     contact = 'my.email@example.com')

Attach services
~~~~~~~~~~~~~~~

Next, we'll choose an archive manager. DataFS currently supports MongoDB and DynamoDB managers. In this example we'll use a MongoDB manager. Make sure you have a MongoDB server running, then create a :py:class:`~datafs.managers.manager_mongo.MongoDBManager` instance:

.. code-block:: python

    >>> from datafs.managers.manager_mongo import MongoDBManager
    >>> manager = MongoDBManager()
    >>> api.attach_manager(manager)

Now we need a storage service. DataFS is designed to be used with remote storage (S3, FTP, etc), but it can also be run on your local filesystem. In this tutorial we'll use a local service:

To do this, pick a directory to use as a local store. We'll use a temporary directory:

.. code-block:: python

    >>> import tempfile
    >>> local_dir = tempfile.mkdtemp()


Now we'll create a local file service using the fs package:

.. code-block:: python

    >>> from fs.osfs import OSFS
    >>> local = OSFS(local_dir)
    >>> api.attach_service('local', local)


Create archives
~~~~~~~~~~~~~~~

Next we'll create our first archive. An archive must 
have an archive_name. In addition, you can supply any 
additional keyword arguments, which will be stored as 
metadata. To suppress errors on re-creation, use the 
``raise_if_exists=False`` flag.


.. code-block:: python
    
    >>> api.create_archive(
    ...     'my_first_archive',
    ...     description = 'My test data archive')


Retrieve archive metadata
~~~~~~~~~~~~~~~~~~~~~~~~~

Now that we have created an archive, we can retrieve it 
from anywhere as long as we have access to the correct 
service. When we retrieve the archive, we can see the 
metadata that was created when it was initialized.

.. code-block:: python
    
    >>> var = api.get_archive('my_first_archive')
    >>> var.metadata
    {u'creation_date': u'20161122-175114', u'contact': u'my.email@example.com', u'description': u'My test data archive', u'creator': u'My Name'}


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

Let's make sure it's still in the archive:

.. code-block:: python

    >>> var.version_ids
    [u'20161122-175114']


Reading from the archive
~~~~~~~~~~~~~~~~~~~~~~~~

Next we'll read from the archive. That file object returned by ``var.versions`` can be opened and read just like a regular file:

.. code-block:: python

    >>> with var.versions[0].open() as f:
    ...     print(f.read())
    ... 
    this is a test


Updating the archive
~~~~~~~~~~~~~~~~~~~~

.. todo::
    
    Change this so that you can't overwrite old data

If you write to the file objects in the archive, you'll overwrite the old versions. Instead, you should create a new version and upload it to the archive:

.. code-block:: python

    >>> with open('newversion.txt', 'w+') as f:
    ...     f.write('this is the next test')
    ... 
    >>> var.update('newversion.txt')
    >>> os.remove('newversion.txt')
    >>> var.versions
    [u'20161122-175114', u'20161122-175114']

Now let's make sure we're getting the latest version. This time, we'll use the ``latest`` property:

.. code-block:: python


    >>> with var.latest.open() as f:
    ...     print(f.read())
    ... 
    this is the next test


Cleanup
~~~~~~~

You might want to delete the local directory:

.. code-block:: python


    >>> import shutil
    >>> shutil.rmtree(local_dir)


Next steps
~~~~~~~~~~

The :ref:`next tutorial <tutorial-aws>` describes setting up DataFS for remote obejct stores, such as with AWS storage.