r'''

## SETUP-START

    >>> from datafs.managers.manager_mongo import MongoDBManager
    >>> from datafs import DataAPI
    >>> from fs.osfs import OSFS
    >>> import datafs
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
    ...     api.delete_archive('my_archive')
    ... except KeyError:
    ...     pass
    ...

## SETUP-END


## EXAMPLE-BLOCK-1-START

.. code-block:: python

    >>> my_archive = api.create('my_archive')
    >>> with my_archive.open('w+', 
    ...     dependencies={'archive2': '1.1', 'archive3': None}) as f:
    ...
    ...     res = f.write(u'contents depend on archive 2 v1.1')
    ...
    >>> my_archive.get_dependencies() # doctest: +SKIP
    {'archive2': '1.1', 'archive3': None}

## EXAMPLE-BLOCK-1-END

.. code-block:: python

    >>> my_archive.get_dependencies() == {
    ...     'archive2': '1.1', 'archive3': None}
    ...
    True



## EXAMPLE-BLOCK-2-START

.. code-block:: python

    >>> with my_archive.open('w+') as f:
    ...
    ...     res = f.write(u'contents depend on archive 2 v1.2')
    ...
    >>> my_archive.set_dependencies({'archive2': '1.2'})
    >>> my_archive.get_dependencies()
    {'archive2': '1.2'}

## EXAMPLE-BLOCK-2-END


## EXAMPLE-BLOCK-3-START

.. code-block:: python

.. code-block:: text
    :linenos:

    dep1==1.0
    dep2==0.4.1a3

## EXAMPLE-BLOCK-3-END

.. code-block:: python

    >>> with open('requirements_data.txt', 'w+') as f:
    ...     res = f.write(u'dep1==1.0\ndep2==0.4.1a3')
    ...

## EXAMPLE-BLOCK-4-START

.. code-block:: python

    >>> api = datafs.get_api(
    ...     requirements_file='requirements_data.txt')
    >>>
    >>> archive = api.get_archive('my_archive')
    >>> with archive.open('w+') as f:
    ...     res = f.write(u'depends on dep1 and dep2')
    ...
    >>> archive.get_dependencies()
    {'dep1': '1.0', 'dep2': '0.4.1a3'}

## EXAMPLE-BLOCK-4-END


## EXAMPLE-BLOCK-5-START

.. code-block:: python
    >>> archive.get_dependencies()
    {'dep1': '1.0', 'dep2': '0.4.1a3'}

## EXAMPLE-BLOCK-5-END


## EXAMPLE-BLOCK-6-START

.. code-block:: python

    >>> archive.get_dependencies()
    {'dep1': '1.0', 'dep2': '0.4.1a3'}

## EXAMPLE-BLOCK-6-END


## EXAMPLE-BLOCK-7-START

.. code-block:: python

    >>> archive.get_dependencies(version='0.0.1') # doctest: +SKIP
    {'archive2': '1.1', 'archive3': None}

## EXAMPLE-BLOCK-7-END

.. code-block:: python

    >>> archive.get_dependencies(version='0.0.1') == {
    ...     'archive2': '1.1', 'archive3': None}
    True


## TEARDOWN-START

.. code-block:: python

    >>> try:
    ...     os.remove('requirements_data.txt')
    ... except:
    ...     pass
    ...
    >>> try:
    ...     api.delete_archive('my_archive')
    ... except KeyError:
    ...     pass
    ...

    >>> api.manager.delete_table('TestFiles')
    >>> local.close()
    >>> shutil.rmtree(temp)

## TEARDOWN-END

'''
'''
'''
