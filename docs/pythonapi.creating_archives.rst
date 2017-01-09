.. _pythonapi-creating-archives:

======================
Creating Data Archives
======================

Archives are the basic unit of a DataFS filesystem. They are essentially files, metadata, history, versions, and dependencies wrapped into a single object.

You can create archives from within python or using the :ref:`command line interface <cli-creating-archives>`.

Create an archive using the :py:meth:`datafs.DataAPI.create` command.

.. code-block:: python

    >>> archive = api.create('my/archive/name')

Naming Archives
---------------

Archives can be named anything, as long as the data service you use can handle the name.

For example, Amazon's S3 storage cannot handle underscores in object names. If you create an archive with underscores in the name, you will receive an error on write (rather than on archive creation). Since this is an error specific to the storate service, we do not catch this error on creation.


Specifying an Authority
-----------------------

If you have more than one authority, you will need to specify an authority on archive creation:

.. code-block:: python

    >>> archive = api.create(
    ...     'my_archive_name',
    ...     authority_name='my_authority')

Alternatively, you can set the :py:attr:`~datafs.core.data_api.DataAPI.DefaultAuthorityName` attribute:

.. code-block:: python

	>>> api.DefaultAuthorityName = 'my_authority'
    >>> archive = api.create('my_archive_name')


Adding Metadata
---------------

Arbitrary metadata can be added using the ``metadata`` dictionary argument:

.. code-block:: python

    >>> archive = api.create(
    ...     'my_archive_name',
    ...     metadata={
    ...         'description': 'my test archive',
    ...         'source': 'Burke et al (2015)',
    ...         'doi': '10.1038/nature15725'})


Required Metadata
~~~~~~~~~~~~~~~~~

Administrators can set up metadata requirements using the manager's :ref:`admin` tools. If these required fields are not provided, an error will be raised on archive creation.

For example, when connected to a manager requiring the `'description'` field:

.. code-block:: python

    >>> archive = api.create(
    ...     'my_archive_name',
    ...     metadata={
    ...         'source': 'Burke et al (2015)',
    ...         'doi': '10.1038/nature15725'})
    Traceback (most recent call last):
    ...
    AssertionError: Required value "description" not found. Use helper=True or the --helper flag for assistance.

Trying again with a "description" field will work as expected.

Using the Helper
~~~~~~~~~~~~~~~~

Instead of providing all fields in the ``create`` call, you can optionally use the ``helper`` argument. Setting ``helper=True`` will start an interactive prompt, requesting each required item of metadata:

.. code-block:: python

    >>> archive = api.create(
    ...     'my_archive_name',
    ...     metadata={
    ...         'source': 'Burke et al (2015)',
    ...         'doi': '10.1038/nature15725'},
    ...         helper=True)
	Enter a description: 


