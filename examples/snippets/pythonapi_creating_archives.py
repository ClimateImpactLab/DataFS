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
    >>> api.attach_authority('my_authority', local)
    >>> api.default_authority # doctest: +ELLIPSIS
    <DataService:OSFS object at ...>
    >>> try:
    ...     api.delete_archive('my_archive_name')
    ... except KeyError:
    ...     pass
    ...

## SETUP-END


## EXAMPLE-BLOCK-1-START

.. code-block:: python

    >>> archive = api.create('my/archive/name')

## EXAMPLE-BLOCK-1-END


.. code-block:: python

    >>> try:
    ...     api.delete_archive('my_archive_name')
    ... except KeyError:
    ...     pass
    ...

    >>> local2 = OSFS(temp)
    >>> api.attach_authority('local2', local)


## EXAMPLE-BLOCK-2-START

.. code-block:: python

    >>> archive = api.create('my_archive_name')# doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: Authority ambiguous. Set authority or DefaultAuthorityName.

## EXAMPLE-BLOCK-2-END


## EXAMPLE-BLOCK-3-START

.. code-block:: python

    >>> archive = api.create(
    ...     'my_archive_name',
    ...     authority_name='my_authority')
    ...

## EXAMPLE-BLOCK-3-END

.. code-block:: python

    >>> try:
    ...     api.delete_archive('my_archive_name')
    ... except KeyError:
    ...     pass
    ...


## EXAMPLE-BLOCK-4-START

.. code-block:: python

    >>> api.DefaultAuthorityName = 'my_authority'
    >>> archive = api.create('my_archive_name')

## EXAMPLE-BLOCK-4-END


.. code-block:: python

    >>> try:
    ...     api.delete_archive('my_archive_name')
    ... except KeyError:
    ...     pass
    ...


## EXAMPLE-BLOCK-5-START

.. code-block:: python

    >>> archive = api.create(
    ...     'my_archive_name',
    ...     metadata={
    ...         'description': 'my test archive',
    ...         'source': 'Burke et al (2015)',
    ...         'doi': '10.1038/nature15725'})
    ...

## EXAMPLE-BLOCK-5-END


.. code-block:: python

    >>> try:
    ...     api.delete_archive('my_archive_name')
    ... except KeyError:
    ...     pass
    ...
    >>> api.manager.set_required_archive_metadata(
    ...     {'description': 'Enter a description'})
    ...


## EXAMPLE-BLOCK-6-START

.. code-block:: python

    >>> archive = api.create(
    ...     'my_archive_name',
    ...     metadata = {
    ...         'source': 'Burke et al (2015)',
    ...         'doi': '10.1038/nature15725'})
    ... # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    AssertionError: Required value "description" not found. Use helper=True or
    the --helper flag for assistance.

## EXAMPLE-BLOCK-6-END


.. code-block:: python

    >>> try:
    ...     api.delete_archive('my_archive_name')
    ... except KeyError:
    ...     pass
    ...


## EXAMPLE-BLOCK-7-START

.. code-block:: python

    >>> archive = api.create(
    ...     'my_archive_name',
    ...     metadata={
    ...         'source': 'Burke et al (2015)',
    ...         'doi': '10.1038/nature15725'},
    ...         helper=True) # doctest: +SKIP
    ...
    Enter a description: 

## EXAMPLE-BLOCK-7-END


## TEARDOWN-START

.. code-block:: python

    >>> try:
    ...     api.delete_archive('my_archive_name')
    ... except KeyError:
    ...     pass
    ...

    >>> api.manager.delete_table('TestFiles')
    >>> local.close()
    >>> local2.close()
    >>> shutil.rmtree(temp)

## TEARDOWN-END

'''