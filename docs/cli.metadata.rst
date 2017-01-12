.. _cli-metadata:

=================
Managing Metadata
=================



In this section we'll take a look at how to access archive metadata from the command line. There is also a
:ref:`python <pythonapi-metadata>` version. 

Viewing Metadata
----------------


We'll keep working with our ``sample_archive`` that we created earlier. Right now we'll take a look at our metadata. Depending 

.. code-block:: bash
	
	datafs sample_archive metadata
	{u'acta non verba': u'deeds not words', 
	 u'actiones secundum fidei': 'action follows belief',
	 u'ad undas': u'to the waves',
	 u'as victoriam': 'for victory'}


Let's say that we want to change one and add another entry. How can we do this?


Updating Metadata
-----------------


.. code-block:: bash

	datafs update_metadata sample_archive 'acta non verba' 'Action is better than words' 'ad atrumque paratas' 'prepared for either alternative'



We'll need to read the metadata again to check to see if we succeeded


.. code-block:: bash

	datafs metadata sample_archive

	{u'acta non verba': u'Action is better than words', 
	 u'actiones secundum fidei': u'action follows belief',
	 u'ad undas': u'to the waves',
	 u'as victoriam': u'for victory', 
	 u'ad atrumque paratas': u'prepared for either alternative'}


Great!

It should be noted that the command line tool does not deal with whitespaces well so you'll need to wrap text in quotes if it refers to a single entry. The command line tool is looking for key value pairs. To preserve this symmetry you'll need to use quotations around some entries. 


