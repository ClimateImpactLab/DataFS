
Using DataFS Locally
====================

:download:`example: local.py <../examples/local.py>`

.. automodule:: examples.local

Creating your own DataFS API
----------------------------

Begin by subclassing datafs.DataAPI:

.. literalinclude:: ../examples/local.py
    :pyobject: MyLocalDataAPI


You can use this class create archives and track data versions:
    
.. literalinclude:: ../examples/local.py
    :pyobject: get_api

.. code-block:: python
    
    >>> api = get_api()
    
.. literalinclude:: ../examples/local.py
    :pyobject: create_archive

.. code-block:: python
    
    >>> archive_name = 'myproject.myteam.var1.type1'
    >>> create_archive(api, archive_name)
    created archive "myproject.myteam.var1.type1"

.. literalinclude:: ../examples/local.py
    :pyobject: retrieve_archive

.. code-block:: python
    
    >>> var = retrieve_archive(api, archive_name)
    >>> print(var.archive_name)
    myproject.myteam.var1.type1
    >>> print(var.metadata)
    {u'creation_date': u'20161120-021415', u'contact': u'my.email@example.com', u'description': u'My test data archive', u'creator': u'My Name'}