'''

Here is an example API that you could implement: :download:`download my_api.py <../examples/subclassing/my_api.py>`

.. literalinclude:: ../examples/subclassing/my_api.py


A user of this API will have access to the more limited set of archive 
operations:

.. code-block:: python

    >>> from my_api import MyAPI
    >>>
    >>> my_api = MyAPI('my name')
    >>>
    >>> my_api.create_archive('archive_name')
    >>>
    >>> archive = my_api.get_archive('archive_name')
    >>> 
    >>> archive.delete()                             # doctest: +ELLIPSIS
    Traceback (most recent call first):
    ...
    IOError: Data archives cannot be deleted
    >>> archive.attach_authority('s3-1', None)       # doctest: +ELLIPSIS
    Traceback (most recent call first):
    ...
    PermissionError: Authorities locked

However, users of this api still have access to all other features:

.. code-block:: python

    >>> with archive.open('w+') as f:
    ...     res = f.write('my new data')
    ...
    >>> with archive.open('r') as f:
    ...     print(res.read())
    my new data
    >>> with snacks in my mouth:
    ...     talk


'''