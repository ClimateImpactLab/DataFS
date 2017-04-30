import pytest


@pytest.mark.examples
@pytest.mark.cli_snippets
def test_cli_listdir(cli_validator_listdir):
    cli_validator_listdir(r'''


Snippet 1

.. EXAMPLE-BLOCK-1-START

.. code-block:: bash

    $ datafs listdir impactlab
    labor
    climate
    conflict
    mortality

.. EXAMPLE-BLOCK-1-END

Snippet 2

.. EXAMPLE-BLOCK-2-START

.. code-block:: bash

    $ datafs listdir impactlab/conflict
    global

.. EXAMPLE-BLOCK-2-END

Snippet 3

.. EXAMPLE-BLOCK-3-START

.. code-block:: bash

    $ datafs listdir impactlab/conflict/global
    conflict_global_daily.csv
    $ datafs listdir impactlab/conflict/global/conflict_global_daily.csv
    0.0.1

.. EXAMPLE-BLOCK-3-END

''')


@pytest.mark.examples
@pytest.mark.cli_snippets
def test_cli_filter(cli_validator_manager_various):
    cli_validator_manager_various(r'''


Snippet 4

.. EXAMPLE-BLOCK-4-START

.. code-block:: bash

    $ datafs filter --prefix project1_variable1_ # doctest: +SKIP
    project1_variable1_scenario5.nc
    project1_variable1_scenario1.nc
    project1_variable1_scenario4.nc
    project1_variable1_scenario2.nc
    project1_variable1_scenario3.nc

.. EXAMPLE-BLOCK-4-END

Snippet 5

.. EXAMPLE-BLOCK-5-START

.. code-block:: bash

    $ datafs filter --pattern *_variable4_scenario4.nc --engine path \
    # doctest: +SKIP
    project1_variable4_scenario4.nc
    project2_variable4_scenario4.nc
    project3_variable4_scenario4.nc
    project5_variable4_scenario4.nc
    project4_variable4_scenario4.nc

.. EXAMPLE-BLOCK-5-END

Snippet 6

.. EXAMPLE-BLOCK-6-START

.. code-block:: bash

    $ datafs filter --pattern variable2 --engine str # doctest: +ELLIPSIS +SKIP
    project1_variable2_scenario1.nc
    project1_variable2_scenario2.nc
    project1_variable2_scenario3.nc
    ...
    project5_variable2_scenario3.nc
    project5_variable2_scenario4.nc
    project5_variable2_scenario5.nc

.. EXAMPLE-BLOCK-6-END

''')


@pytest.mark.examples
@pytest.mark.cli_snippets
def test_cli_search(cli_validator_manager_various):

    cli_validator_manager_various(r'''


Snippet 7

.. EXAMPLE-BLOCK-7-START

.. code-block:: bash

    $ datafs search team3 # doctest: +ELLIPSIS +SKIP
    project2_variable2_scenario2.nc
    project5_variable4_scenario1.nc
    project1_variable5_scenario4.nc
    project3_variable2_scenario1.nc
    project2_variable1_scenario1.nc
    ...
    project5_variable1_scenario2.nc
    project2_variable5_scenario5.nc
    project5_variable2_scenario5.nc
    project3_variable2_scenario5.nc

.. EXAMPLE-BLOCK-7-END


Snippet 8

.. EXAMPLE-BLOCK-8-START

.. code-block:: bash

    $ datafs get_tags project2_variable2_scenario2.nc
    team3
.. EXAMPLE-BLOCK-8-END


Snippet 9

.. EXAMPLE-BLOCK-9-START

.. code-block:: bash

    $ datafs search team1 # doctest: +ELLIPSIS +SKIP
    project1_variable1_scenario4.nc
    project1_variable2_scenario2.nc
    project1_variable2_scenario5.nc
    project1_variable3_scenario3.nc
    project1_variable4_scenario1.nc
    project1_variable4_scenario4.nc
    ...
    project5_variable3_scenario2.nc
    project5_variable3_scenario5.nc
    project5_variable4_scenario3.nc
    project5_variable5_scenario1.nc
    project5_variable5_scenario4.nc


.. EXAMPLE-BLOCK-9-END

Snippet 10

.. EXAMPLE-BLOCK-10-START

.. code-block:: bash

    $ datafs get_tags project2_variable5_scenario1.nc
    team1

.. EXAMPLE-BLOCK-10-END
''')
