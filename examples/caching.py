'''

Setup
~~~~~

    >>> from datafs.managers.manager_mongo import MongoDBManager
    >>> from datafs import DataAPI
    >>> from fs.tempfs import TempFS
    >>> from fs.s3fs import S3FS
    >>> import os
    >>> import tempfile
    >>> import shutil

Create an API and attach a manager

    >>> api = DataAPI(
    ...      username='My Name',
    ...      contact = 'my.email@example.com')
    >>>
    >>> manager = MongoDBManager(
    ...     database_name = 'MyDatabase',
    ...     table_name = 'DataFiles')
    >>>
    >>> manager.create_archive_table('DataFiles', raise_if_exists=False)
    >>> api.attach_manager(manager)
    >>>

For this example we'll use an AWS S3 store. Any filesystem will work, though:

    >>> s3 = S3FS(
    ...     'test-bucket',
    ...     aws_access_key='MY_KEY',
    ...     aws_secret_key='MY_SECRET_KEY')
    >>>
    >>> api.attach_authority('aws', s3)

Create an archive

    >>> var = api.create_archive(
    ...     'caching_archive',
    ...     metadata = dict(description = 'My cached remote archive'), 
    ...     authority_name='aws')
    >>>
    >>> with var.open('w+') as f:
    ...     res = f.write(u'hello')
    ...
    >>>
    >>> with var.open('r') as f:
    ...     print(f.read())
    hello

Let's peek under the hood to see where this data is stored:

    >>> var.authority.fs.getpathurl('caching/archive') # doctest: +ELLIPSIS
    'https://test-bucket.s3.amazonaws.com/caching/archive?...AWSAccessKeyId=MY_KEY'

Now let's set up a cache. This would typically be a local or networked directory 
but we'll use a temporary filesystem for this example:

    >>> cache = TempFS()
    >>> api.attach_cache(cache)

Now we can activate caching for our archive:

    >>> var.cache = True

When we read the data from the cache, it downloads the file for future use:


    >>> with var.open('r') as f:
    ...     print(f.read())
    hello

Cleanup
~~~~~~~

    >>> var.delete()

'''

