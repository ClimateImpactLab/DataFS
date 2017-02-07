'''

.. _snippets-pythonapi-metadata:

Python API: Managing Metadata
=============================

This is the tested source code for the snippets used in
:ref:`pythonapi-metadata`. The config file we're using in this example
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
    ...     api.delete_archive('sample_archive')
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

Displayed example 1 code

.. EXAMPLE-BLOCK-1-START

.. code-block:: python

    >>> sample_archive = api.create(
    ...    'sample_archive',
    ...     metadata = {
    ...         'oneline_description': 'tas by admin region',
    ...         'source': 'NASA BCSD',
    ...         'notes': 'important note'})
    ...

.. EXAMPLE-BLOCK-1-END


Example 2
---------

Displayed example 2 code

.. EXAMPLE-BLOCK-2-START

.. code-block:: python

    >>> for archive_name in api.filter():
    ...     print(archive_name)
    ...
    sample_archive


.. EXAMPLE-BLOCK-2-END


Example 3
---------

Displayed example 3 code

.. EXAMPLE-BLOCK-3-START

.. code-block:: python

    >>> sample_archive.get_metadata() # doctest: +SKIP
    {u'notes': u'important note', u'oneline_description': u'tas by admin region
    ', u'source': u'NASA BCSD'}

.. EXAMPLE-BLOCK-3-END

The last line of this test cannot be tested directly (exact dictionary
formatting is unstable), so is tested in a second block:

.. code-block:: python

    >>> sample_archive.get_metadata() == {
    ...     u'notes': u'important note',
    ...     u'oneline_description': u'tas by admin region',
    ...     u'source': u'NASA BCSD'}
    ...
    True



Example 4
---------

Displayed example 4 code

.. EXAMPLE-BLOCK-4-START

.. code-block:: python

    >>> sample_archive.update_metadata(dict(
    ...     source='NOAAs better temp data',
    ...     related_links='http://wwww.noaa.gov'))
    ...

.. EXAMPLE-BLOCK-4-END


Example 5
---------

Displayed example 5 code

.. EXAMPLE-BLOCK-5-START

.. code-block:: python

    >>> sample_archive.get_metadata() # doctest: +SKIP
    {u'notes': u'important note', u'oneline_description': u'tas by admin region
    ', u'source': u'NOAAs better temp data', u'related_links': u'http://wwww.no
    aa.gov'}

.. EXAMPLE-BLOCK-5-END

The last line of this test cannot be tested directly (exact dictionary
formatting is unstable), so is tested in a second block:

.. code-block:: python

    >>> sample_archive.get_metadata() == {
    ...     u'notes': u'important note',
    ...     u'oneline_description': u'tas by admin region',
    ...     u'source': u'NOAAs better temp data',
    ...     u'related_links': u'http://wwww.noaa.gov'}
    ...
    True


Example 6
---------

Displayed example 6 code

.. EXAMPLE-BLOCK-6-START

.. code-block:: python

    >>> sample_archive.update_metadata(dict(related_links=None))
    >>>
    >>> sample_archive.get_metadata() # doctest: +SKIP
    {u'notes': u'important note', u'oneline_description': u'tas by admin region
    ', u'source': u'NOAAs better temp data'}

.. EXAMPLE-BLOCK-6-END


The last line of this test cannot be tested directly (exact dictionary
formatting is unstable), so is tested in a second block:

.. code-block:: python

    >>> sample_archive.get_metadata() == {
    ...     u'notes': u'important note',
    ...     u'oneline_description': u'tas by admin region',
    ...     u'source': u'NOAAs better temp data'}
    ...
    True



Teardown
--------

.. code-block:: python

    >>> try:
    ...     api.delete_archive('sample_archive')
    ... except KeyError:
    ...     pass
    ...

    >>> api.manager.delete_table('DataFiles')


'''
