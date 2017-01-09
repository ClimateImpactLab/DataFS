.. _cli-creating-archives:

======================
Creating Data Archives
======================

Archives are the basic unit of a DataFS filesystem. They are essentially files, metadata, history, versions, and dependencies wrapped into a single object.

You can create archives from the command line interface or from :ref:`python <pythonapi-creating-archives>`.

Create an archive using the ``create`` command:

.. code-block:: bash
	
	datafs create my_archive_name 

Naming Archives
---------------

Archives can be named anything, as long as the data service you use can handle the name.

For example, Amazon's S3 storage cannot handle underscores in object names. If you create an archive with underscores in the name, you will receive an error on write (rather than on archive creation). Since this is an error specific to the storate service, we do not catch this error on creation.


Specifying an Authority
-----------------------

If you have more than one authority, you will need to specify an authority on archive creation:

.. code-block:: bash
	
	datafs create my_archive_name --authority_name "my_authority"


Adding Metadata
---------------

Arbitrary metadata can be added as keyword arguments:

.. code-block:: bash

    $ datafs create my_archive_name --source 'Burke et al (2015)' --doi '10.1038/nature15725' --description 'my test archive'

Required Metadata
~~~~~~~~~~~~~~~~~

Administrators can set up metadata requirements using the manager's :ref:`admin` tools. If these required fields are not provided, an error will be raised on archive creation.

For example, when connected to a manager requiring the `'description'` field:

.. code-block:: bash

    $ datafs create my_archive_name --source 'Burke et al (2015)' --doi '10.1038/nature15725'
    Traceback (most recent call last):
    ...
    AssertionError: Required value "description" not found. Use helper=True or the --helper flag for assistance.

Trying again with a ``--description "[desc]"`` argument will work as expected.


Using the Helper
~~~~~~~~~~~~~~~~

Instead of providing all fields in the ``create`` call, you can optionally use the ``helper`` flag. Using the flag ``--helper`` will start an interactive prompt, requesting each required item of metadata:

.. code-block:: bash

    $ datafs create my_archive_name --source 'Burke et al (2015)' --doi '10.1038/nature15725' --helper
	Enter a description: 



