.. _cli-dependencies:

==========================
Managing Data Dependencies
==========================

Dependency graphs can be tracked explicitly in datafs, and each version can have its own dependencies.

You specify dependencies from the command line interface or from within :ref:`python <pythonapi-dependencies>`.

.. note::

    Dependencies are not currently validated in any way, so entering a dependency that is not a valid archive name or version will not raise an error.


Specifying Dependencies
-----------------------

On write
~~~~~~~~

Dependencies can be set when using the ``--dependency`` option to the ``update`` command. To specify several dependencies, use multiple ``--dependency archive[==version]`` arguments.

Each ``--dependency`` value should have the syntax ``archive_name==version``. Supplying only the archive name will result in a value of ``None``. A value of ``None`` is a valid dependency specification, where the version is treated as unpinned and is always interpreted as the dependency's latest version.

For example:

.. code-block:: bash

    $ datafs create my_archive
    
    $ echo "contents depend on archive 2 v1.1" >> arch.txt
    
    $ datafs update my_archive arch.txt  --dependency "archive2==1.1" --dependency "archive3"
    
    $ datafs get_dependencies my_archive
    {'archive2': '1.1', 'archive3': None}


After write
~~~~~~~~~~~

Dependencies can also be added to the latest version of an archive using the ``set_dependencies`` command:

.. code-block:: bash

    $ datafs set_dependencies my_archive --dependency archive2==1.2

    $ datafs get_dependencies my_archive
    {'archive2': '1.2'}


Using a requirements file
~~~~~~~~~~~~~~~~~~~~~~~~~

If a requirements file is present at api creation, all archives written with that api object will have the specified dependencies by default.

For example, with the following requirements file as ``requirements_data.txt``:

.. code-block:: text
    :linenos:

    dep1==1.0
    dep2==0.4.1a3

Archives written while in this working directory will have these requirements:

.. code-block:: bash

    $ echo "depends on dep1 and dep2" > arch.txt

    $ datafs update my_archive arch.txt --requirements_file 'requirements_data.txt'

    $ datafs get_dependencies my_archive
    {'dep1': '1.0', 'dep2': '0.4.1a3'}


Using Dependencies
------------------

Retrieve dependencies with the ``dependencies`` command:

.. code-block:: bash

    datafs get_dependencies my_archive
    {'dep1': '1.0', 'dep2': '0.4.1a3'}

Get dependencies for older versions using the ``--version`` argument:

.. code-block:: bash

    $ datafs get_dependencies my_archive --version 0.0.1
    {'archive2': '1.1', 'archive3': None}