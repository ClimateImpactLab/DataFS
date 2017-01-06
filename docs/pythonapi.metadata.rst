.. _pythonapi-metadata:

=================
Managing Metadata
=================


Metadata management is one of the core components of DataFS. Metadata is managed at the Archive level and the version level. This documentation will refer to the Archive level metadata. 


We'll assume that your manager and authority have been set up already. Depending on usage, metadata requirements will be enforced and archive creation will be possible only with inclusion of the required metadata. 


.. code-block:: python

	>>> sample_archive = api.create('sample_archive', 
	...							  metadata=dict(oneline_description='daily annual temp by admin region', 
	...							  long_description='daily annual temperature in degrees kelvin, organized ...							by admin region2 as defined by the united nations', 
	...							  source='NASA BCSD', 
	...						  	  notes='important note that should be remembered when using this archive'))
	>>>