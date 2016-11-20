
from __future__ import absolute_import
'''
Runs a local version of DataFS using MongoDB and the local filesystem

Usage
-----

To run this example:

1. create a MongoDB server by following the 
   `MongoDB's Tutorial <https://docs.mongodb.com/manual/tutorial/>`_ 
   installation and startup instructions. 

2. Run this example with DataFS installed, or as a module from the repo root:

    .. code-block:: bash

        python -m examples.local

'''

from datafs import DataAPI
from datafs.managers.mongo import MongoDBManager
from datafs.services.service_os import OSService

def main():
    MyDataAPI = DataAPI
    MyDataAPI.Manager = MongoDBManager
    MyDataAPI.Services['local'] = OSService

    api = MyDataAPI(
        username='My Name',
        contact = 'my.email@example.com')


    # Create an archive
    archive_name = 'myproject.myteam.var1.type1'
    api.create_archive(
        archive_name, 
        description='My test data archive')
    print('created archive "{}"'.format(archive_name))


    # Retrieve the archive
    var1 = api.get_archive(archive_name)
    print('retrieved archive "{}"'.format(var1.archive_name))

    # Print metadata from the archive
    print(var1.metadata)

if __name__ == '__main__':
    main()