#!/bin/bash

# FLYCOP 
# Author: Iván Martín Martín
# August 2021

# Original Location (to be run from): ./MainFolder folder
# call: sh general_output_analysis.sh '2_models 3_models' ../FLYCOP_analysis ./InputFiles configAnalysis_ratios.txt GeneralAnalysis_input.txt PairwiseVariableAnalysis_input.txt BiomassNutrientAnalysis_input.txt

# ----------------------------------------------------------------------------------------------------
# Basic file "configurationResults_consArchitecture.xlsx" should be placed at ./FLYCOP_analysis folder
# The main output folders would be finally located in the ./FLYCOP_analysis folder
# ----------------------------------------------------------------------------------------------------

# INPUT PARAMETERS
# ----------------
cons_arch=$1  # '2_models 3_models'
output_folder=$2  # e.g. './FLYCOP_analysis' (complete path)
input_files_folder=$3  # e.g. './InputFiles' (path with respect to output_folder variable)
ratios_file=$4  # e.g. 'configAnalysis_ratios.txt' (just the filename)
generalAnalysis_input=$5  # e.g. 'GeneralAnalysis_input.txt' (just the filename)
pairwiseVariableAnalysis_input=$6  # e.g. 'PairwiseVariableAnalysis_input.txt' (just the filename)
biomassproductionanalysis_input=$7  # e.g. 'BiomassNutrientAnalysis_input.txt' (just the filename)


# OUTPUT FOLDER
# -------------
cd  ./FLYCOP_analysis  # Accessing to the input analysis folder


# GENERAL ANALYSIS
# ----------------
python3 ../Scripts/GeneralAnalysis.py "$cons_arch" $output_folder $input_files_folder $ratios_file $generalAnalysis_input

# PAIRWISE VARIABLE ANALYSIS
# --------------------------
python3 ../Scripts/PairwiseVariableAnalysis.py "$cons_arch" $output_folder $input_files_folder $pairwiseVariableAnalysis_input

# BIOMASS & NUTRIENT ANALYSIS
# ---------------------------
python3 ../Scripts/BiomassProductionAnalysis.py "$cons_arch" $output_folder $input_files_folder $biomassproductionanalysis_input

cd ..


