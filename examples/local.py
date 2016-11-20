"""
Use this tutorial to build a DataFS server using MongoDB and the local filesystem


Running this example
--------------------

To run this example:

1. Create a MongoDB server by following the 
   `MongoDB's Tutorial <https://docs.mongodb.com/manual/tutorial/>`_ 
   installation and startup instructions. 

2. Start the MongoDB server (e.g. `mongodb  --dbpath . --nojournal`)

3. Run ``local.py`` with DataFS installed, or as a module from the repo root:

    .. code-block:: bash

        python -m examples.local

"""

from __future__ import absolute_import

from datafs import DataAPI
from datafs.managers.manager_mongo import MongoDBManager

from fs.osfs import OSFS

import os

def get_api(local_dir):
    '''
    Create an api instance with your personal information
    '''


    api = DataAPI(
        username='My Name',
        contact = 'my.email@example.com')
    
    manager = MongoDBManager(api=api)
    local = OSFS(local_dir)

    api.attach_manager(manager)
    api.attach_service('local', local)

    return api

def create_archive(api, archive_name):
    '''
    Create an archive
    '''

    archive_name = 'myproject.myteam.var1.type1'
    api.create_archive(
        archive_name, 
        description='My test data archive',
        raise_if_exists=False)

    print('created archive "{}"'.format(archive_name))

def retrieve_archive(api, archive_name):
    '''
    Retrieve and use archive
    '''

    # Retrieve the archive
    var = api.get_archive(archive_name)
    return var


def main():
    '''
    Create a connection to the API and create an archive
    '''
    local_dir = '~/datafs/'
    
    if not os.path.isdir(local_dir):
        os.makedirs(local_dir)

    api = get_api(local_dir)

    archive_name = 'myproject.myteam.var1.type1'
    create_archive(api, archive_name)
    var = retrieve_archive(api, archive_name)
    
    print('retrieved archive "{}"'.format(var.archive_name))
    print(var.metadata)

    with open('test.txt', 'w+') as test:
        test.write('this is a test')

    var.update('test.txt')

    os.remove('test.txt')




if __name__ == '__main__':
    main()