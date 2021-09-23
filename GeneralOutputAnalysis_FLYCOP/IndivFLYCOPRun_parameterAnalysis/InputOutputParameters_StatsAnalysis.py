#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 27 23:02:18 2020

@author: Iván Martín Martín
"""

"""
OUTPUT ANALYSIS AFTER FLYCOP
DESCRIPTION - STATISTICAL ANALYSIS

    Statistical analysis for the data obtained from previous analysis of INPUT / OUTPUT PARAMETERS.
        Scripts: InputParametersAnalysis.py, OutputParametersAnalysis.py
    
    The main idea for this script is analyzing certain parameters from FLYCOP output
        considering the fitness ranks previously selected by the user. Thus the column
        'fitFunc' is the pivotal parameter for the organization of the statistical analysis.
    
EXPECTED INPUT

    'dataTable_AcceptedRatios_SDlt.xlxs' from "InputParametersAnalysis.py" script.
    'configurationsResults_Scenario0_analysis.xlsx' from "OutputParametersAnalysis.py" script
        
OUTPUT

    Statistical description (on screen) of selected variables.
    
NOTE THAT:
    
    The order of the fitness_ranks_set should be: higher to lower rank; (lower_bound, upper_bound).
    
    The variables to be displayed and the fitness ranks to be analyzed can be adapted if desired.
        (CHANGE keyword)
    
"""

# import re
import pandas as pd
import os.path

scripts_path = os.getcwd()
os.chdir("../Utilities")
from FitnessRanks import describe_fitness_ranks

os.chdir(scripts_path)  # Creo que esto va a fallar, hace falta: os.chdir("../IndividualFLYCOPAnalysis")
path = "../../Project3_EcPp2_LimNut_M9/NP_LimNutFinal_29Mar/NP3"  # CHANGE path
os.chdir(path)


# -----------------------------------------------------------------------------
# CHANGE fitness ranks if desired
fitness_ranks_set = ((0, 30), (30, 55), (75, 100))  


# """
# -----------------------------------------------------------------------------
# STATISTICAL ANALYSIS OF INPUT PARAMETERS
# -----------------------------------------------------------------------------
# INPUT: dataTable_AcceptedRatios_SDlt.xlsx, sorted descending by 'fitFunc'
dataTable = pd.read_excel("dataTable_AcceptedRatios_SDlt.xlsx", sheet_name="Uptake_initBiomass_r", engine="openpyxl")
dataTable = dataTable[dataTable["ID_SD"] != 1]  #  Only those values for configurations with an acceptable SD

# CHANGE columns to be analyzed in the statistical analysis
describe_fitness_ranks(fitness_ranks_set, dataTable, descr_columns = ["fitFunc", "sucr1_frc2", "Ecbiomass_KTbiomass"], ref_column = "fitFunc")
# """


# -----------------------------------------------------------------------------
# STATISTICAL ANALYSIS OF OUTPUT PARAMETERS
# -----------------------------------------------------------------------------
# INPUT: 'configurationsResults_Scenario0_analysis.txt', sorted descending by 'fitness'
dataTable = pd.read_excel("configurationsResults_Scenario0_analysis_fitnessOK.xlsx", sheet_name="Product_ratios", engine="openpyxl")
dataTable = dataTable[dataTable["ID_SD"] != 1]  #  Only those values for configurations with an acceptable SD

# CHANGE columns to be analyzed in the statistical analysis
ratios = ["sucr1_frc2", "Ecbiomass_KTbiomass"]  # Names for new column_ratios to be plotted, in order
input_parameters = ["sucr1_IP", "frc1_IP", "EcInit_IP", "KTInit_IP", "NH4_Ec", "NH4_KT", "Pi_Ec", "Pi_KT"]
output_parameters = ["fitFunc", "Nar_mM", "pCA_mM", "FinalEc_gL", "FinalKT_gL", "FinalSucr"]

describe_fitness_ranks(fitness_ranks_set, dataTable, descr_columns = input_parameters[0:4], ref_column = "fitFunc")















