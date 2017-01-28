#!/bin/bash
# this script uses the ANACONDA_TOKEN env var. 
# to create a token:
# >>> anaconda login
# >>> anaconda auth -c -n travis --max-age 307584000 --url https://anaconda.org/ClimateImpactLab/DataFS --scopes "api:write api:read"
set -e

echo "Converting conda package..."
conda convert --platform all $HOME/miniconda2/conda-bld/linux-64/DataFS-*.tar.bz2 --output-dir conda-bld/

echo "Deploying to Anaconda.org..."
anaconda -t $ANACONDA_TOKEN upload conda-bld/**/DataFS-*.tar.bz2

echo "Successfully deployed to Anaconda.org."
exit 0