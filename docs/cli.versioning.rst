.. _cli-versioning:

=================
Tracking Versions
=================


In this section we'll have a look at the archive versioning options available through the command line. 

We'll assume we have our api configured and that our manager and authority is already set-up. We go ahead and creat our sample archive again to demonstrate how versions are managed. 


.. code-block:: bash

	datafs create sample_archive metadata 'useful metadata'
	created versioned archive <DataArchive osfs://sample_archive>


So now we have our archive being tracked by manager. 



.. code-block:: bash

	datafs update sample_archive --string 'barba crescit caput nescit'
	uploaded data to <DataArchive osfs://sample_archive>. new version 0.0.1 created.



Explicit Versioning
-------------------

As we learned in our section on writing and reading archives, the version is set to 0.0.1 on creation by default. 
If you wanted to specify a prerelease or a minor release you would do either of the following

.. code-block:: bash

	datafs update sample_archive --bumpversion patch --string 'Aliquando et insanire iucundum est'
	uploaded data to <DataArchive osfs://sample_archive>. version bumped 0.0.1 --> 0.0.2


.. code-block:: bash

	datafs update sample_archive --bumpversion minor --string 'animum debes mutare non caelum'
	uploaded data to <DataArchive osfs://sample_arch>. version bumped 0.0.2 --> 0.1.


Get Version History
-------------------

What if we want to view our versions? 

.. code-block:: bash

	datafs versions sample_archive 
	['0.0.1', '0.0.2', '0.1']



Downloading Specific Versions
-----------------------------

How can we get a specific version?

.. code-block:: bash

	datafs download sample_archive /Users/data/sample_archive_versioned.txt --version 0.0.2
	downloaded v.0.0.2 to /Users/data/sample_archive_versioned.txt






















