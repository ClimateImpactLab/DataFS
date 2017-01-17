'''

Here is an example API that you could implement:
:download:`download my_api.py <../examples/subclassing/my_api.py>`

.. literalinclude:: ../examples/subclassing/my_api.py

A user can now use your custom version of the DataFS API:

.. code-block:: python

    >>> from my_api import MyAPI
    >>>
    >>> my_api = MyAPI(
    ...   username='my name',
    ...   contact='my_email@example.com',
    ...   AWS_ACCESS_KEY='my_access_key',
    ...   AWS_SECRET_KEY='my_secret_key')

The user of this API will have access to the more limited set of archive
operations:

.. code-block:: python

    >>> archive = my_api.create('archive_name', authority_name='s3-1')
    >>>
    >>> archive.delete()                             # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    IOError: Data archives cannot be deleted
    >>> my_api.attach_authority('s3-1', None)        # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    PermissionError: Authorities locked

However, users of this api still have access to all other features:

.. code-block:: python

    >>> archive_2 = my_api.create(
    ...     'another archive',
    ...     authority_name='NAT-1',
    ...     metadata={
    ...         'description':
    ...             'data file to be stored on network-attached-storage'})
    ...
    >>> with archive_2.open('w+') as f:
    ...     res = f.write(u'my new data')
    ...
    >>> with archive_2.open('r') as f:
    ...     print(f.read())
    my new data
    >>>

Cleanup
~~~~~~~~~~~~~~

.. code-block::python

    >>> from my_api import teardown
    >>> teardown()

'''
