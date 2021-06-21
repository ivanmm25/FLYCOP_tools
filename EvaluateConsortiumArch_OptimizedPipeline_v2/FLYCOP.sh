#!/bin/bash

############ FLYCOP ############
# Author: Beatriz García-Jiménez, Iván Martín Martín
# April 2018, June 2021
################################

# Call: sh FLYCOP.sh <consortiumPrefix> <Y> V<A> <fitnessFunction> <numberOfConfigurations> <cons_architectures>
# Example: sh FLYCOP.sh 'EcPp3' 0 V0 'MaxNaringenin' 20 '2_models 3_models'

domainName=$1  # EcPp3
id=$2 # '20', '21', ...
templateID=$3 # 'V0', 'V1', 'V2', 'V5' ...
fitness=$4 # 'MaxGR', 'MaxYield', 'MaxNaringenin'
numOfRuns=$5 # 5, 20, 100
cons_arch=$6  # '2_models 3_models'

logFile=FLYCOP_${domainName}_${id}_log.txt

cd MicrobialCommunities
python3 -W ignore ../Scripts/${domainName}_define_SMAC_conditionals_arch.py ${domainName}_TemplateOptimizeConsortium${templateID}/SMAC_conditionals_arch.txt ../Scripts/${domainName}_confFLYCOP_params_v0_generalized.pcs
smac --scenario-file ../Scripts/${domainName}_confFLYCOP_scenario_v${id}_generalized.txt --validation false --numberOfRunsLimit ${numOfRuns} > $logFile
bash ../Scripts/FLYCOPanalyzingResults_${domainName}.sh $id $templateID $fitness $numOfRuns $domainName "$cons_arch"
cd ..  # FLYCOP folder


