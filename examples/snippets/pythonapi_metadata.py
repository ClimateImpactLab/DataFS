'''

## SETUP-START

    >>> from datafs.managers.manager_mongo import MongoDBManager
    >>> from datafs import DataAPI
    >>> from fs.osfs import OSFS
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
    ...
    >>> api = DataAPI(
    ...      username='My Name',
    ...      contact = 'my.email@example.com')
    ...
    >>> manager = MongoDBManager(
    ...     database_name = 'MyDatabase',
    ...     table_name = 'TestFiles')
    ...
    >>> manager.create_archive_table('TestFiles', raise_on_err=False)
    >>> api.attach_manager(manager)
    >>> temp = tempfile.mkdtemp()
    >>> local = OSFS(temp)
    >>> api.attach_authority('local', local)
    >>> api.default_authority # doctest: +ELLIPSIS
    <DataService:OSFS object at ...>
    >>> try:
    ...     api.delete_archive('sample_archive')
    ... except KeyError:
    ...     pass
    ...

## SETUP-END


## EXAMPLE-BLOCK-1-START

.. code-block:: python

    >>> sample_archive = api.create(
    ...    'sample_archive',
    ...     metadata = {
    ...         'oneline_description': 'tas by admin region',
    ...         'source': 'NASA BCSD',
    ...         'notes': 'important note'})
    ...

## EXAMPLE-BLOCK-1-END


## EXAMPLE-BLOCK-2-START

.. code-block:: python

    >>> for archive_name in api.filter():
    ...     print(archive_name)
    ...
    sample_archive


## EXAMPLE-BLOCK-2-END


## EXAMPLE-BLOCK-3-START

.. code-block:: python

    >>> sample_archive.get_metadata() # doctest: +SKIP
    {u'notes': u'important note', u'oneline_description': u'tas by admin region
    ', u'source': u'NASA BCSD'}

## EXAMPLE-BLOCK-3-END


# Check this just to make sure

.. code-block:: python

    >>> sample_archive.get_metadata() == {
    ...     u'notes': u'important note',
    ...     u'oneline_description': u'tas by admin region',
    ...     u'source': u'NASA BCSD'}
    ...
    True


## EXAMPLE-BLOCK-4-START

.. code-block:: python

    >>> sample_archive.update_metadata(dict(
    ...     source='NOAAs better temp data',
    ...     related_links='http://wwww.noaa.gov'))
    ...

## EXAMPLE-BLOCK-4-END


## EXAMPLE-BLOCK-5-START

.. code-block:: python

    >>> sample_archive.get_metadata() # doctest: +SKIP
    {u'notes': u'important note', u'oneline_description': u'tas by admin region
    ', u'source': u'NOAAs better temp data', u'related_links': u'http://wwww.no
    aa.gov'}

## EXAMPLE-BLOCK-5-END


# Check this just to make sure

.. code-block:: python

    >>> sample_archive.get_metadata() == {
    ...     u'notes': u'important note',
    ...     u'oneline_description': u'tas by admin region',
    ...     u'source': u'NOAAs better temp data',
    ...     u'related_links': u'http://wwww.noaa.gov'}
    ...
    True


## EXAMPLE-BLOCK-6-START

.. code-block:: python

    >>> sample_archive.update_metadata(dict(related_links=None))
    >>>
    >>> sample_archive.get_metadata() # doctest: +SKIP
    {u'notes': u'important note', u'oneline_description': u'tas by admin region
    ', u'source': u'NOAAs better temp data'}

## EXAMPLE-BLOCK-6-END


# Check this just to make sure

.. code-block:: python

    >>> sample_archive.get_metadata() == {
    ...     u'notes': u'important note',
    ...     u'oneline_description': u'tas by admin region',
    ...     u'source': u'NOAAs better temp data'}
    ...
    True


## TEARDOWN-START

.. code-block:: python

    >>> try:
    ...     api.delete_archive('sample_archive')
    ... except KeyError:
    ...     pass
    ...

    >>> api.manager.delete_table('TestFiles')
    >>> shutil.rmtree(temp)

## TEARDOWN-END

'''
