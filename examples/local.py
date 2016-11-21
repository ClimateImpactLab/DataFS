"""
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

from __future__ import absolute_import

from datafs import DataAPI
from datafs.managers.manager_mongo import MongoDBManager

from fs.osfs import OSFS

import os

def get_api():
    '''
    Create an api instance with your personal information
    '''

    api = DataAPI(
        username='My Name',
        contact = 'my.email@example.com')

    return api

def create_and_attach_services(api):
    
    # Create manager
    manager = MongoDBManager()
    

    # Set up local archive service in ~/datafs
    local_dir = '~/datafs/'
    
    if not os.path.exists(os.path.expanduser(local_dir)):
        os.makedirs(os.path.expanduser(local_dir))
        
    local = OSFS(local_dir)


    # Attach manager and service to API
    api.attach_manager(manager)
    api.attach_service('local', local)


def create_archive(api):
    '''
    Create an archive
    '''

    archive_name = 'my_first_archive'
    description = 'My test data archive'

    api.create_archive(
        archive_name, 
        description=description,
        raise_if_exists=False)

    # add some other archives for testing

    api.create_archive('archive_2', raise_if_exists=False)

    api.create_archive('archive_3', raise_if_exists=False)


def retrieve_archive(api):
    '''
    Retrieve and use archive
    '''

    archive_name = 'my_first_archive'
    
    # Retrieve the archive
    var = api.get_archive(archive_name)

    return var

def add_to_archive(api):
    '''
    Add file to archive
    '''

    archive_name = 'my_first_archive'

    var = api.get_archive(archive_name)

    with open('test.txt', 'w+') as test:
        test.write('this is a test')

    var.update('test.txt')

    os.remove('test.txt')

    print('Archive "{}" versions:\n{}'.format(var.archive_name, var.versions))


def retrieve_file(api):

    archive_name = 'my_first_archive'

    var = api.get_archive(archive_name)

    file_object = var.latest

    with file_object.open() as fp:
        print('Archive "{}" latest version contents:\n{}'.format(archive_name, fp.read()))

def update_file(api):

    archive_name = 'my_first_archive'

    var = api.get_archive(archive_name)

    with open('newversion.txt', 'w+') as test:
        test.write('this is the next test')

    var.update('newversion.txt')
    os.remove('newversion.txt')

    print('Archive "{}" versions:\n{}'.format(var.archive_name, var.versions))

    with var.latest.open() as f:
        print(f.read())

def main():
    '''
    Create a connection to the API and create an archive
    '''

    api = get_api()
    create_and_attach_services(api)

    create_archive(api)

    print('\n')
    var = retrieve_archive(api)
    print('Retrieved archive "{}"'.format(var.archive_name))
    print(var.metadata)


    print('\n')
    add_to_archive(api)

    print('\n')
    retrieve_file(api)

    print('\n')
    update_file(api)

if __name__ == '__main__':
    main()