"""

Using DataFS Locally
====================

Use this tutorial to build a DataFS server using MongoDB and the local filesystem


Running this example
--------------------

To run this example:

1. Create a MongoDB server by following the 
   `MongoDB's Tutorial <https://docs.mongodb.com/manual/tutorial/>`_ 
   installation and startup instructions. 

2. Start the MongoDB server (e.g. `mongod  --dbpath . --nojournal`)

3. Run ``local.py`` with DataFS installed, or as a module from the repo root:

    .. code-block:: bash

        python -m examples.local

"""

# Set up the workspace
# ~~~~~~~~~~~~~~~~~~~~

# We need a few things for this example:

from __future__ import absolute_import

from datafs.managers.manager_mongo import MongoDBManager
from datafs import DataAPI
from tests.utils import using_tmp_dir, expect
from fs.osfs import OSFS
from ast import literal_eval
import os
import tempfile
import shutil

# Additionally, you'll need MongoDB and pymongo installed 
# and a MongoDB instance running.


def get_api():
    '''
    Create an API
    ~~~~~~~~~~~~~

    Begin by creating an API instance:
    '''

    api = DataAPI(
         username='My Name',
         contact = 'my.email@example.com')

    return api


def attach_manager(api):
    '''
    Attach Manager
    ~~~~~~~~~~~~~~~

    Next, we'll choose an archive manager. DataFS currently 
    supports MongoDB and DynamoDB managers. In this example 
    we'll use a MongoDB manager. Make sure you have a MongoDB 
    server running, then create a MongoDBManager instance:
    
    '''

    manager = MongoDBManager()

    api.attach_manager(manager)


def attach_service(api, local_dir):
    '''
    Attach Service
    ~~~~~~~~~~~~~~

    Now we need a storage service. DataFS is designed to be 
    used with remote storage (S3, FTP, etc), but it can also 
    be run on your local filesystem. In this tutorial we'll 
    use a local service.
    '''

    # We got a local directory from the arguments to this 
    # function:
    
    print(local_dir)

    # Now we'll create a local file service using the fs 
    # package:

    local = OSFS(local_dir)

    # We attach this file to the api and give it a name:

    api.attach_service('local', local)

def create_archive(api):
    '''
    Create archives
    ~~~~~~~~~~~~~~~

    Next we'll create our first archive. An archive must 
    have an archive_name. In addition, you can supply any 
    additional keyword arguments, which will be stored as 
    metadata. To suppress errors on re-creation, use the 
    ``raise_if_exists=False`` flag.
    '''

    api.create_archive(
        'my_first_archive',
        description = 'My test data archive')


@expect.stdout(test=lambda x: literal_eval(x)['description'] == 'My test data archive')
def retrieve_archive(api):
    '''
    Retrieve archive metadata
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Now that we have created an archive, we can retrieve it 
    from anywhere as long as we have access to the correct 
    service. When we retrieve the archive, we can see the 
    metadata that was created when it was initialized.
    '''
       
    var = api.get_archive('my_first_archive')

    print(var.metadata)

def add_to_archive(api):
    '''
    Add a file to the archive
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    An archive is simply a versioned history of data files. 
    So let's get started adding data!

    '''
    
    var = api.get_archive('my_first_archive')

    # First, we'll create a local file, ``test.txt``, and put 
    # some data in it:

    with open('test.txt', 'w+') as f:
         f.write('this is a test')

    # Now we can add this file to the archive:

    var.update('test.txt')

    # This file just got sent into our archive! Now we can delete the local copy:

    os.remove('test.txt')


@expect.stdout(test=lambda x: len(literal_eval(x)) == 1)
def query_archive(api):
    '''
    Query archive
    ~~~~~~~~~~~~~
    '''

    # Let's make sure the file is still in the archive:

    var = api.get_archive('my_first_archive')

    # List the archive's version IDs

    print(var.version_ids)


@expect.stdout('this is a test')
def retrieve_from_archive(api):
    '''
    Reading from the archive
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Next we'll read from the archive. That file object returned by 
    ``var.versions`` can be opened and read just like a regular file
    '''
    
    var = api.get_archive('my_first_archive')

    with var.versions[0].open() as f:
         print(f.read())


@expect.stdout(test=lambda x: len(literal_eval(x)) == 2)
def update_archive(api):
    '''
    Updating the archive
    ~~~~~~~~~~~~~~~~~~~~

    If you write to the file objects in the archive, you'll overwrite the old 
    versions. Instead, you should create a new version and upload it to the 
    archive.
    '''

    # Write a file to your current directory

    with open('newversion.txt', 'w+') as f:
         f.write('this is the next test')

    # Add this file to the archive

    var = api.get_archive('my_first_archive')
    var.update('newversion.txt')

    # Remove the file from the current directory

    os.remove('newversion.txt')

    # List the archive's version IDs

    print(var.version_ids)


@expect.stdout('this is the next test')
def retrieving_the_latest_version(api):
    '''
    Retrieving the latest version
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Now let's make sure we're getting the latest version. This time, we'll use 
    the ``latest`` property.
    '''

    var = api.get_archive('my_first_archive')

    with var.latest.open() as f:
         print(f.read())

    # Looks good!

    # Because we used the @using_tmp_dir decorator, the temporary file 
    # service will be cleaned up automatically.


@using_tmp_dir
def run_local_example(local_dir):
    '''
    Run all of the functions in this example
    '''
    
    api = get_api()
    attach_manager(api)
    attach_service(api, local_dir)
    create_archive(api)
    retrieve_archive(api)
    add_to_archive(api)
    query_archive(api)
    retrieve_from_archive(api)
    update_archive(api)
    retrieving_the_latest_version(api)


def main():
    run_local_example()

def test_local():
    run_local_example()

if __name__ == '__main__':
    main()