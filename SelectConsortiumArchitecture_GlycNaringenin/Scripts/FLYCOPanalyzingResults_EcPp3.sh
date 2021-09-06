#!/bin/bash

# FLYCOP 
# Author: Beatriz García-Jiménez, Iván Martín Martín
# April 2018 // Modification: April 2021

# call: FLYCOPanalyzingResults_EcPp3.sh 0 V0 'MaxGlycNar' 100 'EcPp3' '2_models 3_models'

id=$1 # '20', '21', ...
templateID=$2 # 'V1' 'V2' 'V5' ...
fitness=$3  # 'MaxGlycNar'
nRuns=$4  # Nº de ejecuciones SMAC (aleatorización real)
domainName=$5  # 'EcPp3'
cons_arch=$6  # '2_models 3_models'
nmodels_line=$7  # Line number of nmodels parameter in pcs file, e.g. 9


echo "Initializing FLYCOPanalizingResults"
pwd
currDir=`pwd`  # FLYCOP/MicrobialCommunities (folder)
dataAnalysisDir=${currDir}/${domainName}_scenario${id}_FLYCOPdataAnalysis  # FLYCOP folder
mkdir $dataAnalysisDir

seed=123
cd smac-output/${domainName}_confFLYCOP_scenario_v${id}_generalized/state-run${seed}  # FLYCOP foldern_arg_nmodels


# 1.- Get summary statistics file, $nRuns SMAC configurations
# ----------------------------------------------------------

tail -n${nRuns} runs_and_results-it*.csv | awk -F, '{print NR","1-$4}' > $dataAnalysisDir/fitness.csv
paste -d, paramstrings-it*.txt $dataAnalysisDir/fitness.csv > $dataAnalysisDir/paramstrings_withFitness.csv	 # SMAC files
egrep "WARN.*Result of algorithm run|ERROR.*The following algorithm call failed" ../log-warn${seed}.txt | awk -F'Result of algorithm run: ' '{if($2==""){print "X,X,X,1,X,X,1"}else{print $2}}' | cut -d, -f4,7 | awk -F, '{print 1-$1","$2}' > $dataAnalysisDir/avgfitnessAndStdev.txt


# Retrieve configuration
cd ..
param1=`tail log-run${seed}.txt | egrep "p01_sucr1" | awk -F'p01_sucr1' '{print $2}' | cut -d' ' -f2 | sed "s/'//g"`
param2=`tail log-run${seed}.txt | egrep "p01_sucr1" | awk -F'p01_sucr1' '{print $2}' | cut -d' ' -f4 | sed "s/'//g"`
param3=`tail log-run${seed}.txt | egrep "p01_sucr1" | awk -F'p01_sucr1' '{print $2}' | cut -d' ' -f6 | sed "s/'//g"`
param4=`tail log-run${seed}.txt | egrep "p01_sucr1" | awk -F'p01_sucr1' '{print $2}' | cut -d' ' -f8 | sed "s/'//g"`
param5=`tail log-run${seed}.txt | egrep "p01_sucr1" | awk -F'p01_sucr1' '{print $2}' | cut -d' ' -f10 | sed "s/'//g"`
n_models=$( echo ${param5} | cut -d'_' -f1 )


init_biomass=()
for i in $(seq 1 $n_models)
do
	value=$( expr 2 \* ${i} + 2 \* ${nmodels_line} )
	param=$( tail log-run${seed}.txt | egrep "p01_sucr1" | awk -F'p01_sucr1' '{print $2}' | cut -d' ' -f ${value} | sed "s/'//g" )
	init_biomass=$( echo "${init_biomass} ${param}" )
done

echo "Optimal consortium configuration found: " $param1 $param2 $param3 $param4 $param5
echo "Initial biomasses: " $init_biomass
cd ../..


# 2.- Move configurations collection file to data analysis folder
# ---------------------------------------------------------------
mv smac-output/${domainName}_PlotsScenario${id}/ $dataAnalysisDir/
# rm -Rf smac-output/
cd $dataAnalysisDir
mv ${domainName}_PlotsScenario${id}/configurationsResults* .
cd ..

# 3.- Individual Test for the optimal configuration
# -------------------------------------------------

cp -p -R ${domainName}_TemplateOptimizeConsortium${templateID}/Comets ${domainName}_scenario${id}_optimalConfiguration
cd ${domainName}_scenario${id}_optimalConfiguration
python3 -W ignore ../../Scripts/${domainName}_individualTestFLYCOP_v0_generalized.py $param1 $param2 $param3 $param4 $param5 "$init_biomass" $fitness
cd $currDir  # MicrobialCommunities


# 4.- Preliminary analysis of the configurationsResults.txt file
# ---------------------------------------------------------------

mkdir -p $dataAnalysisDir/PreliminaryAnalysis
cp -r FLYCOP_${domainName}_${id}_log.txt $dataAnalysisDir/PreliminaryAnalysis
cp -r ../Scripts/${domainName}_confFLYCOP_params_v0_generalized.pcs $dataAnalysisDir/PreliminaryAnalysis
mv $dataAnalysisDir/configurationsResults* $dataAnalysisDir/PreliminaryAnalysis
cd $dataAnalysisDir/PreliminaryAnalysis

python3 -W ignore ../../../Scripts/${domainName}_preliminaryAnalysis1.py $domainName $id "$cons_arch" ${domainName}_confFLYCOP_params_v0_generalized.pcs
python3 -W ignore ../../../Scripts/${domainName}_preliminaryAnalysis2.py "$cons_arch"

rm -r FLYCOP_${domainName}_${id}_log.txt
cp -r configurationResults_consArchitecture.xlsx ..  # This would be the updated version of the configurationsResults table
cd ../../..
# ---------------------------------------------------------------

echo "Finished FLYCOPanalizingResults"



















