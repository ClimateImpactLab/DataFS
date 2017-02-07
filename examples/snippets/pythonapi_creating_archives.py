'''
.. _snippets-pythonapi-creating-archives:

Python API: Creating Archives
=============================

This is the tested source code for the snippets used in
:ref:`pythonapi-creating-archives`. The config file we're using in this example
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
    ...     api.delete_archive('my_archive_name')
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

    >>> archive = api.create('my_archive_name')

.. EXAMPLE-BLOCK-1-END

Example 1 cleanup:

.. code-block:: python

    >>> api.delete_archive('my_archive_name')


Example 2
---------

Example 2 setup

.. code-block:: python

    >>> api.attach_authority('my_authority', TempFS())


Displayed example 2 code

.. EXAMPLE-BLOCK-2-START

.. code-block:: python

    >>> archive = api.create('my_archive_name')# doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: Authority ambiguous. Set authority or DefaultAuthorityName.

.. EXAMPLE-BLOCK-2-END


Example 3
---------

.. EXAMPLE-BLOCK-3-START

.. code-block:: python

    >>> archive = api.create(
    ...     'my_archive_name',
    ...     authority_name='my_authority')
    ...

.. EXAMPLE-BLOCK-3-END

Example 3 cleanup:

.. code-block:: python

    >>> try:
    ...     api.delete_archive('my_archive_name')
    ... except KeyError:
    ...     pass
    ...


Example 4
---------

.. EXAMPLE-BLOCK-4-START

.. code-block:: python

    >>> api.DefaultAuthorityName = 'my_authority'
    >>> archive = api.create('my_archive_name')

.. EXAMPLE-BLOCK-4-END

Example 4 cleanup:

.. code-block:: python

    >>> try:
    ...     api.delete_archive('my_archive_name')
    ... except KeyError:
    ...     pass
    ...


Example 5
---------

.. EXAMPLE-BLOCK-5-START

.. code-block:: python

    >>> archive = api.create(
    ...     'my_archive_name',
    ...     metadata={
    ...         'description': 'my test archive',
    ...         'source': 'Burke et al (2015)',
    ...         'doi': '10.1038/nature15725'})
    ...

.. EXAMPLE-BLOCK-5-END


Example 5 cleanup:

.. code-block:: python

    >>> try:
    ...     api.delete_archive('my_archive_name')
    ... except KeyError:
    ...     pass
    ...


Example 6
---------

Example 6 setup:

.. code-block:: python

    >>> api.manager.set_required_archive_metadata(
    ...     {'description': 'Enter a description'})
    ...

Displayed example:

.. EXAMPLE-BLOCK-6-START

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

.. EXAMPLE-BLOCK-6-END

Example 6 cleanup:

.. code-block:: python

    >>> try:
    ...     api.delete_archive('my_archive_name')
    ... except KeyError:
    ...     pass
    ...


Example 7
---------

.. EXAMPLE-BLOCK-7-START

.. code-block:: python

    >>> archive = api.create(
    ...     'my_archive_name',
    ...     metadata={
    ...         'source': 'Burke et al (2015)',
    ...         'doi': '10.1038/nature15725'},
    ...         helper=True) # doctest: +SKIP
    ...
    Enter a description:

.. EXAMPLE-BLOCK-7-END


Teardown
--------

.. code-block:: python

    >>> try:
    ...     api.delete_archive('my_archive_name')
    ... except KeyError:
    ...     pass
    ...

    >>> api.manager.delete_table('DataFiles')


'''
