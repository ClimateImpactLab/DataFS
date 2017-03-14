import pytest
import datafs 

@pytest.mark.examples
@pytest.mark.cli_snippets
def test_cli_listdir(cli_validator_dual_manager_listdir):



       cli_validator_dual_manager_listdir(r'''


.. EXAMPLE-BLOCK-1-START

.. code-block:: bash

    $ datafs listdir impactlab
    climate
    conflict
    labor
    mortality

.. EXAMPLE-BLOCK-1-END

''')

# @pytest.mark.examples
# @pytest.mark.cli_snippets
# def test_cli_listdir(cli_validator_dual_manager_various):



#        cli_validator_dual_manager_various(r'''


# .. EXAMPLE-BLOCK-1-START

# .. code-block:: bash

#     $ datafs 

# .. EXAMPLE-BLOCK-1-END

# ''')
