#!/bin/bash
# INITIAL UPDATE DOCKER
# ---------------------
# This initial Docker update is needed in order to run the pipeline on 'EvaluateConsortiumArch' for FLYCOP.

# 1. Initial Python update
pip install --upgrade pip
pip install optlang
pip install openpyxl
pip install xlrd
apt-get install python3-tk
pip install tk
pip install backend
pip install seaborn
pip install --upgrade pandas
pip install --upgrade seaborn

# 2. Install needed R packages
Rscript --vanilla host/InitializeDocker_R.r


# 3. Automatically copy Gurobi lisence from ./host to the directory where is needed for execution
cp -r host/gurobi.lic gurobi562/linux64/

# 4. Copy files from ./host folder to execution folders in Docker
# cp -r host/EvaluateConsortiumArch/Scripts/* FLYCOP/Scripts/
# mv FLYCOP/Scripts/FLYCOP.sh ./FLYCOP
# cp -r host/EvaluateConsortiumArch/EcPp3_TemplateOptimizeConsortiumV0/ FLYCOP/MicrobialCommunities/
# cd FLYCOP

# 5. Ready for initialize FLYCOP
echo "\n-----------------------------"
echo "Ready for initialize FLYCOP"
echo "-----------------------------\n"
# sh FLYCOP.sh 'EcPp3' 0 V0 'MaxNaringenin' 100
