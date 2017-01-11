
.. _quickstart:

==========
Quickstart
==========

Setup
-----

* Create a local working data directory (e.g. ``mkdir ~/datafs``)
* download :download:`this file <../examples/quickstart/config.yml>`
* copy it into the file opened with ``datafs configure --edit``, editing the data directory ``~/datafs`` to match the one you created.
* `install <http://datafs.readthedocs.io/en/latest/installation.html#managers>`_ and `configure <http://datafs.readthedocs.io/en/latest/configure.manager.html>`_ a local manager

Using the command line
----------------------

Create an archive

.. code-block:: bash

    $ datafs create new_archive

Use the archive

.. code-block:: bash

    $ echo "initial contents" | datafs update new_archive --string

    $ datafs cat new_archive
    initial contents

    $ echo "new contents" | datafs update new_archive --string

    $ datafs cat new_archive
    new contents

    $ datafs cat new_archive --version 0.0.1
    initial contents

See the full :ref:`command line documentation <cli>`


Using python
------------

.. code-block:: python

    >>> import datafs

    >>> api = datafs.get_api()

    >>> archive = api.get_archive('new_archive')

    >>> with archive.open('r') as f:
    ...     print(f.read())
    new contents

    >>> with archive.open('w+', bumpversion='major') as f:
    ...     f.write(u'first release')
    ...

    >>> archive.get_versions()
    ['0.0.1', '0.0.2', '1.0']

Use other packages:

.. code-block:: python

    >>> import pandas as pd, numpy as np

    >>> with archive.open('w+b') as f:
    ...     pd.DataFrame(np.random.random(4,5)).to_csv(f)

    >>> with archive.open('w+') as f:
    ...     f.write(u'')

    >>> with archive.open('r', version='1.0.1') as f:
    ...     print(pd.read_csv(f))
    ...
              0         1         2         3         4
    0  0.064340  0.266545  0.739165  0.892549  0.576971
    1  0.586370  0.903017  0.874171  0.046859  0.747309
    2  0.349005  0.628717  0.638336  0.670759  0.493050
    3  0.323830  0.697789  0.006091  0.629318  0.039715

See the full :ref:`python api documentation <pythonapi>`