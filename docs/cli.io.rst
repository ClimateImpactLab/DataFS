.. _cli-io:

=========================
Reading and Writing Files
=========================



Reading from and writing to files is straight forward in DataFS. In this section we'll cover the command-line implementation of this. The :ref:`python <pythonapi-io>` implementation is also available.

We'll assume you have your api configured with a manager and an authority. Check the :ref:`configure <configure>` documentation for more information on how to set up DataFS.


Listing Archives
----------------

If I want to first check to see if I have any archives I can use the `list` command. Here we see we don't currently have any archives


.. code-block:: bash

	datafs list
	[]

So let's create an archive so we have something to work with. 

.. code-block:: bash

	datafs create sample_archive 
	created versioned archive <DataArchive osfs://sample_archive>


Now when we list we see our archive. Great!

.. code-block:: bash

	datafs list
	[<DataArchive osfs://sample_archive>]



Writing to Archives
-------------------

This time we will simply demonstrate how you can 

.. code-block:: bash

	datafs update sample_archive --string 'barba crescit caput nescit'
	uploaded data to <DataArchive osfs://sample_archive>. new version 0.0.1 created.


Great! 



Reading from Archives
---------------------


.. code-block:: bash

	datafs download sample_archive '~/data/sample_archive.txt'
	downloaded  v0.0.1 to /Users/data/sample_archive.txt



Now let's read this to make sure we got what we want

.. code-block:: bash
	
	cat ~/data/sample_archive.txt
	barba crescit caput nescit



Writing to Archives with Filepaths
----------------------------------

Let's say we made some major edits to our sample_archive locally and we want to update them in the manager and at our authority. We can update the same as before but this time we'll add the filepath that points to our file.

.. code-block:: bash

	datafs update sample_archive ~/data/sample_archive.txt
	uploaded data to <DataArchive osfs://sample_archive>. version bumped 0.0.1 --> 0.0.2


And now to read this file, let's download to a different spot and read from there.


.. code-block:: bash

	datafs download sample_archive ~/data/sample_archive_placeholder.txt
	downloaded  v0.0.2 to /Users/data/sample_archive_placeholder.txt
	
	cat ~/data/sample_archive_placeholder.txt
	barba crescit caput nescit
	luctuat nec mergitur


We can see that our updates have been added and that they are reflected in a new version number. 






	









