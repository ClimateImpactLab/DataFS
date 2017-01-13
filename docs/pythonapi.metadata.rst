.. _pythonapi-metadata:

=================
Managing Metadata
=================


Metadata management is one of the core components of DataFS. Metadata is managed at the Archive level and the version level. This documentation will refer to the Archive level metadata. 


We'll assume that your manager and authority have been set up already. Depending on usage, metadata requirements can be enforced and archive creation will be possible only with inclusion of the required metadata. 

.. code-block:: python

	>>> sample_archive = api.create('sample_archive', 
	...     metadata=dict(
	..          oneline_description='tas by admin region', 
	...         long_description='daily average temperature (kelvin) '
	...             'by admin region2 as defined by the united nations', 
	...         source='NASA BCSD', 
	...         notes='important note'))
	>>>

Let's check to see if we have any other archives. It looks like we only have our ``sample_archive``. 

.. code-block:: python

	>>> api.list()
	... ['sample_archive']

Nope just this one. So let's have a look at the metadata using :py:meth:`~datafs.core.data_archive.DataArchive.get_metadata`. 

.. code-block:: python 

	>>> sample_archive.get_metadata() # doctest: +SKIP
	{u'long_description': u'daily average temperature (kelvin) by admin region2',
 	u'notes': u'important note',
 	u'oneline_description': u'daily average temp by admin region',
 	u'source': u'NASA BCSD'}


Let's say you later on realize that you want to add another field to the archive metadata and that you also want to update on of the required fields. The archive metadata is modified in place and so you'll be able to do both at the same time with :py:meth:`~datafs.core.data_archive.DataArchive.update_metadata`

.. code-block:: python 

	>>> sample_archive.update_metadata(dict(source='NOAAs better temp data', related_links='http://wwww.noaa.gov'))


As you can see the source was updated and the ``related_links`` key and value were added.


.. code-block:: python 

	>>> sample_archive.get_metadata() # doctest: +SKIP
	{u'long_description': u'daily average temperature (kelvin) by admin region2',
 	u'notes': u'important note that should be remembered when using this archive',
 	u'oneline_description': u'daily annual temp by admin region',
 	u'related_links': u'http://wwww.noaa.gov',
 	u'source': u'NOAAs better temp data'}




As long as a particular metadata key-value pair is not a required field, you can remove it. If you want to remove a particular key-value pair from the archive metadata, set the value to None:

.. code-block:: python 

	>>> sample_archive.update_metadata(dict(related_links=None))
	>>>
	>>> sample_archive.get_metadata() # doctest: +SKIP
	{u'long_description': u'daily average temperature (kelvin) by admin region2',
 	u'notes': u'important note that should be remembered when using this archive',
 	u'oneline_description': u'daily annual temp by admin region',
 	u'source': u'NOAAs better temp data'}


Now our ``related_links`` key-value pair has been removed. To edit the required metadata fields, please 
see :ref:`admin`. 












