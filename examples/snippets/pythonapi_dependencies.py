r'''

.. _snippets-pythonapi-dependencies:

Python API: Dependencies
========================

This is the tested source code for the snippets used in
:ref:`pythonapi-dependencies`. The config file we're using in this example can
be downloaded :download:`here <../examples/snippets/resources/datafs.yml>`.
Later on in the script, we use a requirements file. That file can be downloaded
:download:`here <../examples/snippets/resources/requirements_data.txt>`.


Setup
-----

.. code-block:: python

    >>> import datafs

We test with the following setup:

.. code-block:: python

    >>> api = datafs.get_api(
    ...     config_file='examples/snippets/resources/datafs.yml')
    ...

This assumes that you have the provided config file at the above location.

clean up any previous test failures

.. code-block:: python

    >>> try:
    ...     api.delete_archive('my_archive')
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

    >>> my_archive = api.create('my_archive')
    >>> with my_archive.open('w+',
    ...     dependencies={'archive2': '1.1', 'archive3': None}) as f:
    ...
    ...     res = f.write(u'contents depend on archive 2 v1.1')
    ...
    >>> my_archive.get_dependencies() # doctest: +SKIP
    {'archive2': '1.1', 'archive3': None}

.. EXAMPLE-BLOCK-1-END


The last line of this test cannot be tested directly (exact dictionary
formatting is unstable), so is tested in a second block:


.. code-block:: python

    >>> my_archive.get_dependencies() == {
    ...     'archive2': '1.1', 'archive3': None}
    ...
    True



Example 2
---------

Displayed example 2 code


.. EXAMPLE-BLOCK-2-START

.. code-block:: python

    >>> with my_archive.open('w+') as f:
    ...
    ...     res = f.write(u'contents depend on archive 2 v1.2')
    ...
    >>> my_archive.set_dependencies({'archive2': '1.2'})
    >>> my_archive.get_dependencies() # doctest: +SKIP
    {'archive2': '1.2'}

.. EXAMPLE-BLOCK-2-END


The last line of this test cannot be tested directly (exact dictionary
formatting is unstable), so is tested in a second block:


.. code-block:: python

    >>> my_archive.get_dependencies() == {'archive2': '1.2'}
    True


Example 3
---------

The following text is displayed to demonstrate the file contents:


.. EXAMPLE-BLOCK-3-START

.. code-block:: text
    :linenos:

    dep1==1.0
    dep2==0.4.1a3

.. EXAMPLE-BLOCK-3-END


The following code creates the actual file contents

Example 4
---------

We test with the following setup:

.. code-block:: python

    >>> api = datafs.get_api(
    ...     config_file='examples/snippets/resources/datafs.yml',
    ...     requirements='examples/snippets/resources/requirements_data.txt')
    ...


Example:

.. EXAMPLE-BLOCK-4-START

.. code-block:: python

    >>> api = datafs.get_api(
    ...     requirements = 'requirements_data.txt')
    ... # doctest: +SKIP
    >>>
    >>> my_archive = api.get_archive('my_archive')
    >>> with my_archive.open('w+') as f:
    ...     res = f.write(u'depends on dep1 and dep2')
    ...
    >>> my_archive.get_dependencies() # doctest: +SKIP
    {'dep1': '1.0', 'dep2': '0.4.1a3'}

.. EXAMPLE-BLOCK-4-END


The last line of this test cannot be tested directly (exact dictionary
formatting is unstable), so is tested in a second block:

.. code-block:: python

    >>> my_archive.get_dependencies() == {'dep1': '1.0', 'dep2': '0.4.1a3'}
    True


Example 5
---------

.. EXAMPLE-BLOCK-5-START

.. code-block:: python

    >>> my_archive.get_dependencies() # doctest: +SKIP
    {'dep1': '1.0', 'dep2': '0.4.1a3'}

.. EXAMPLE-BLOCK-5-END


The last line of this test cannot be tested directly (exact dictionary
formatting is unstable), so is tested in a second block:

.. code-block:: python

    >>> my_archive.get_dependencies() == {'dep1': '1.0', 'dep2': '0.4.1a3'}
    True


Example 6
---------


.. EXAMPLE-BLOCK-6-START

.. code-block:: python

    >>> my_archive.get_dependencies(version='0.0.1') # doctest: +SKIP
    {'archive2': '1.1', 'archive3': None}

.. EXAMPLE-BLOCK-6-END


The last line of this test cannot be tested directly (exact dictionary
formatting is unstable), so is tested in a second block:


.. code-block:: python

    >>> my_archive.get_dependencies(version='0.0.1') == {
    ...     'archive2': '1.1', 'archive3': None}
    True


Teardown
--------

.. code-block:: python

    >>> try:
    ...     api.delete_archive('my_archive')
    ... except KeyError:
    ...     pass
    ...

    >>> api.manager.delete_table('DataFiles')

'''
