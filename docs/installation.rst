.. _installation:

.. highlight:: shell

============
Installation
============

To use DataFS, you'll need to install DataFS and a working combination of :ref:`installation-additional-managers` and :ref:`installation-additional-services`.

.. _installation-datafs:

Installing DataFS
-----------------

Stable release
~~~~~~~~~~~~~~

To install DataFS Data Management System, run this command in your terminal:

.. code-block:: console

    $ pip install datafs

This is the preferred method to install DataFS Data Management System, as it will always install the most recent stable release. 

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
~~~~~~~~~~~~

The sources for DataFS Data Management System can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code~block:: console

    $ git clone git://github.com/ClimateImpactLab/datafs

Or download the `tarball`_:

.. code~block:: console

    $ curl  ~OL https://github.com/ClimateImpactLab/datafs/tarball/master

Once you have a copy of the source, you can install it with:

.. code~block:: console

    $ python setup.py install


.. _Github repo: https://github.com/ClimateImpactLab/datafs
.. _tarball: https://github.com/ClimateImpactLab/datafs/tarball/master


.. _installation-additional:

Additional dependencies
-----------------------

In addition to DataFS, you'll need to install and configure a manager and any services you'd like to use.

See the :ref:`examples` to see managers and services in use.

.. _installation-additional-managers:

Managers
~~~~~~~~

You'll need to connect to a MongoDB or DynamoDB database to use DataFS. These can be local installs for demos/testing/personal use or full installations for teams.

You can download the local installations here:

* `MongoDB local <https://docs.mongodb.com/manual/installation/>`_
* `DynamoDB local <https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html>`_

To connect to these databases, you'll need to install the python interfaces to them:

* MongoDB: ``pip install pymongo``
* DynamoDB: ``pip install boto3``

To `configure a manager for datafs <configure.manager>`_, you'll need to be able to connect to the database using these interfaces. For help, check out their documentation:

* `MongoDB Tutorial <https://api.mongodb.com/python/current/tutorial.html>`_
* `DynamoDB Quickstart <http://boto3.readthedocs.io/en/latest/guide/quickstart.html>`_


.. _installation-additional-services:

Services
~~~~~~~~

Similar to :ref:`installation-additional-managers`, you'll need data at least one storage service to use DataFS. For local/testing/personal use, a local directory can be useful, and is the easiest to set up.

* Ready out-of-the-box:

  - local
  - shared
  - mounted
  - zip
  - ftp
  - http/https
  - in-memory

* Requiring additional packages:

  - AWS/S3: ``pip install boto``
  - SFTP: ``pip install paramiko``
  - XMLRPC: ``pip install xmlrpclib``



