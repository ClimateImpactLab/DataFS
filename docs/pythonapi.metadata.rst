.. _pythonapi-metadata:

=================
Managing Metadata
=================


Metadata management is one of the core components of DataFS. Metadata is managed at the Archive level and the version level. This documentation will refer to the Archive level metadata. 


We'll assume that your manager and authority have been set up already. Depending on usage, metadata requirements will be enforced and archive creation will be possible only with inclusion of the required metadata. 





.. code-block:: python

	>>> sample_archive = api.create('sample_archive', 
	...		metadata=dict(oneline_description='daily annual temp by admin region', 
	...		long_description='daily annual temperature in degrees kelvin, organized
	...		by admin region2 as defined by the united nations', 
	...		source='NASA BCSD', 
	...		notes='important note that should be remembered when using this archive'))
	>>>

Let's check to see if we have any other archives.

.. code-block:: python

	>>> api.archives
	>>> [<DataArchive fs://sample_archive>]

Nope just this one. So let's have a look at the metadata. 

.. code-block:: python 

	>>>sample_archive.get_metadata()
	>>>
	>>> {u'long_description': u'daily annual temperature in degrees kelvin, organized by admin region2 as defined by the united nations',
 	... u'notes': u'important note that should be remembered when using this archive',
 	... u'oneline_description': u'daily annual temp by admin region',
 	... u'source': u'NASA BCSD'}


Let's say you later on realize that you want to add another field to the archive metadata and that you also want to update on of the required fields. The archive metadata is modified in place and so you'll be able to do both at the same time. 

.. code-block:: python 

	>>> sample_archive.update_metadata(dict(source='NOAAs better temp data', related_links='http://wwww.noaa.gov'))


As you can see the source was updated and the ``related_links`` key and value were added.


.. code-block:: python 

	>>> sample_archive.get_metadata()
	>>>
	>>> {u'long_description': u'daily annual temperature in degrees kelvin, organized by admin region2 as defined by the united nations',
 	... u'notes': u'important note that should be remembered when using this archive',
 	... u'oneline_description': u'daily annual temp by admin region',
 	... u'related_links': u'http://wwww.noaa.gov',
 	... u'source': u'NOAAs better temp data'}


 If you want to remove a particular key value from the metadata you do the following:

 








