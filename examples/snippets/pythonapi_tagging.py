'''
.. _snippets-pythonapi-tagging:

Python API: Tagging
===================

This is the tested source code for the snippets used in
:ref:`pythonapi-tagging`. The config file we're using in this example
can be downloaded :download:`here <../examples/snippets/resources/datafs.yml>`.

Setup
-----

.. code-block:: python

    >>> import datafs
    >>> from fs.tempfs import TempFS

We test with the following setup:

.. code-block:: python

    >>> api = datafs.get_api(
    ...     config_file='examples/snippets/resources/datafs.yml')
    ...

This assumes that you have a config file at the above location. The config file
we're using in this example can be downloaded
:download:`here <../examples/snippets/resources/datafs.yml>`.

clean up any previous test failures

.. code-block:: python

    >>> try:
    ...     api.delete_archive('archive1')
    ... except (KeyError, OSError):
    ...     pass
    ...
    >>> try:
    ...     api.delete_archive('archive2')
    ... except (KeyError, OSError):
    ...     pass
    ...
    >>> try:
    ...     api.delete_archive('archive3')
    ... except (KeyError, OSError):
    ...     pass
    ...
    >>> try:
    ...     api.manager.delete_table('DataFiles')
    ... except KeyError:
    ...     pass
    ...

Add a fresh manager table:

.. code-block:: python

    >>> api.manager.create_archive_table('DataFiles')

Example 1
---------

Displayed example 1 code:

.. EXAMPLE-BLOCK-1-START

.. code-block:: python

    >>> archive1 = api.create(
    ...      'archive1',
    ...      tags=["foo", "bar"],
    ...      metadata={'description': 'tag test 1 has bar'})
    ...
    >>> archive2 = api.create(
    ...      'archive2',
    ...      tags=["foo", "baz"],
    ...      metadata={'description': 'tag test 1 has baz'})
    ...

.. EXAMPLE-BLOCK-1-END


Example 2
---------

.. EXAMPLE-BLOCK-2-START

.. code-block:: python

    >>> list(api.search('bar')) # doctest: +SKIP
    ['archive1']

    >>> list(api.search('baz')) # doctest: +SKIP
    ['archive2']

    >>> list(api.search('foo')) # doctest: +SKIP
    ['archive1', 'archive2']

.. EXAMPLE-BLOCK-2-END

Actual Example Block 2 Test

.. code-block:: python

    >>> assert set(api.search('bar')) == {'archive1'}
    >>> assert set(api.search('baz')) == {'archive2'}
    >>> assert set(api.search('foo')) == {'archive1', 'archive2'}


Example 3
---------

.. EXAMPLE-BLOCK-3-START

.. code-block:: python

    >>> archive3 = api.create(
    ...      'archive3',
    ...      tags=["foo", "bar", "baz"],
    ...      metadata={'description': 'tag test 3 has all the tags!'})
    ...

    >>> list(api.search('bar', 'foo')) # doctest: +SKIP
    ['archive1', 'archive3']

    >>> list(api.search('bar', 'foo', 'baz')) # doctest: +SKIP
    ['archive3']

.. EXAMPLE-BLOCK-3-END

Actual example block 3 search test:

.. code-block:: python

    >>> assert set(api.search('bar', 'foo')) == {'archive1', 'archive3'}
    >>> assert set(api.search('bar', 'foo', 'baz')) == {'archive3'}

Example 4
---------

.. EXAMPLE-BLOCK-4-START

.. code-block:: python

    >>> list(api.search('qux')) # doctest: +SKIP
    []
    >>> list(api.search('foo', 'qux')) # doctest: +SKIP
    []

.. EXAMPLE-BLOCK-4-END

Actual example block 4 test

.. code-block:: python

    >>> assert set(api.search('qux')) == set([])

Example 5
---------

.. EXAMPLE-BLOCK-5-START

.. code-block:: python

    >>> archive1.get_tags() # doctest: +SKIP
    ['foo', 'bar']


.. EXAMPLE-BLOCK-5-END

Actual example block 5 test

.. code-block:: python

    >>> assert set(archive1.get_tags()) == {'foo', 'bar'}


Example 6
---------

.. EXAMPLE-BLOCK-6-START

.. code-block:: python

    >>> archive1.add_tags('qux')
    >>>
    >>> list(api.search('foo', 'qux')) # doctest: +SKIP
    ['archive1']


.. EXAMPLE-BLOCK-6-END


Actual example block 6 search test

.. code-block:: python

    >>> assert set(api.search('foo', 'qux')) == {'archive1'}

Example 7
---------

.. EXAMPLE-BLOCK-7-START

.. code-block:: python

    >>> archive1.delete_tags('foo', 'bar')
    >>>
    >>> list(api.search('foo', 'bar')) # doctest: +SKIP
    ['archive3']


.. EXAMPLE-BLOCK-7-END

Actual example block 7 search test

.. code-block:: python

    >>> assert set(api.search('foo', 'bar')) == {'archive3'}

Teardown
--------

.. code-block:: python

    >>> archive1.delete()
    >>> archive2.delete()
    >>> archive3.delete()

'''
