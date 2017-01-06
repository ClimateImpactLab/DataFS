.. _configure-api:

Specifying API objects
======================

Specifying API objects manually from within python
--------------------------------------------------

.. code-block:: python

    >>> from datafs.managers.manager_mongo import MongoDBManager
    >>> from datafs import DataAPI
    >>> from fs.osfs import OSFS
    >>> import tempfile
    >>> 
    >>> api = DataAPI(
    ...      username='My Name',
    ...      contact = 'my.email@example.com')
    ... 
    >>> manager = MongoDBManager(
    ...     database_name = 'MyDatabase',
    ...     table_name = 'DataFiles')
    ... 
    >>> manager.create_archive_table('DataFiles')
    >>> 
    >>> api.attach_manager(manager)
    >>> 
    >>> local = OSFS('~/datafs/my_data/')
    >>> 
    >>> api.attach_authority('local', local)


Specifying an API object with a specifcation file
-------------------------------------------------

Alternatively, you can do the other thing.