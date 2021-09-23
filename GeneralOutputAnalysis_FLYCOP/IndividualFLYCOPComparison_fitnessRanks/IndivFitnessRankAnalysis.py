#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 09:41:22 2021

@author: Iván Martín Martín

OUTPUT ANALYSIS AFTER FLYCOP
DESCRIPTION - OUTPUT PARAMETER ANALYSIS FOR PARTICULAR FITNESS RANKS IN A FLYCOP RUN (individual per rank)

    Individual Rank Analysis: consider one or several ranks in a particular FLYCOP run,
        and perform an analysis of different output parameters for the fitness ranks selected (individually).
    
EXPECTED INPUT

    'configurationsResults_Scenario0_analysis.xlsx' from "OutputParametersAnalysis.py" script (OutputAnalysis) 
    for the particular FLYCOP run to be considered OR other excel (dataframe) suitable file
        
OUTPUT

    Folder: ./OuputParam_IndivFitnessRankComparison
    
        "finalNH4_fitrank1_scatter.png"
        "finalpi_fitrank1_scatter.png"
        "finalsucr_fitrank1_scatter.png"
        "DT_cycles_fitrank1_scatter.png"
        
        "finalNH4_fitrank2_scatter.png"
        "finalpi_fitrank2_scatter.png"
        "finalsucr_fitrank2_scatter.png"
        "DT_cycles_fitrank2_scatter.png"
        
        [...]
        
    
NOTE THAT:
    
    The number of fitness ranks in the FLYCOP run to be analyzed can be variable and should be extended if desired.
        Key parameters to define a fitness rank:
            - Name for plotting (fitRank_nameX)
            - Fitness ranks limits for plotting (fitRank_limitsX)
            
        Code adaptation to complete the plotting of the new fitness rank:
            - Obtain the correspondent section of the original dataframe (with the fitness rank limits)
            - Add code chunck for plotting
            
        
    It is also important to CHANGE / ADAPT the x,y-variables to be used in the 'PLOTTING' section
        (CHANGE keyword)
    
"""

# import re
import pandas as pd
import os.path
# import numpy as np
# import seaborn as sns
# import matplotlib.pyplot as plt

scripts_path = os.getcwd()
os.chdir("../Utilities")

# from FitnessRanks import when_death_starts
import Plotting as myplt
script_path = os.getcwd()
os.chdir(scripts_path)



# -----------------------------------------------------------------------------
# REFERENCE PATH
# -----------------------------------------------------------------------------

ref_path = "../../Project3_EcPp2_LimNut_M9/NP_LimNutFinal_29Mar/NP3"  # CHANGE path
os.chdir(ref_path)


# DATAFRAME IN FLYCOP CONFIGURATION TO BE TAKEN
# -----------------------------------------------------------------------------
configResults = pd.read_excel("configurationsResults_Scenario0_acceptableBiomassLoss_analysis.xlsx", sheet_name="Product_ratios", engine="openpyxl")
configResults_copy = configResults.copy()

configResults_copy = configResults_copy[configResults_copy["ID_SD"] != 1]  #  Only those values for configurations with an acceptable SD



# FITNESS RANK IN DATAFRAME TO BE CONSIDERED
# -----------------------------------------------------------------------------
# Define associated limits for the fitness ranks to be considered - CHANGE 

fitRank_name1 = "0-30"
fitRank_limits1 = [0, 30]

fitRank_name2 = "30-55"
fitRank_limits2 = [30, 55]

fitRank_name3 = "75-100"
fitRank_limits3 = [75, 100]


configResults_fitRank1 = configResults_copy[configResults_copy["fitFunc"] < fitRank_limits1[1]]
configResults_fitRank1 = configResults_fitRank1[configResults_fitRank1["fitFunc"] > fitRank_limits1[0]]

configResults_fitRank2 = configResults_copy[configResults_copy["fitFunc"] < fitRank_limits2[1]]
configResults_fitRank2 = configResults_fitRank2[configResults_fitRank2["fitFunc"] > fitRank_limits2[0]]

configResults_fitRank3 = configResults_copy[configResults_copy["fitFunc"] < fitRank_limits3[1]]
configResults_fitRank3 = configResults_fitRank3[configResults_fitRank3["fitFunc"] > fitRank_limits3[0]]


# -----------------------------------------------------------------------------
# PLOTTING
# -----------------------------------------------------------------------------
if not os.path.isdir("IndivFitnessRankAnalysis"):
    os.mkdir("IndivFitnessRankAnalysis")  # Create "IndivFitnessRankAnalysis" directory
os.chdir("IndivFitnessRankAnalysis")
# -----------------------------------------------------------------------------

# y-VARIABLES (output parameters to be compared)
y_variables = ["NH4_mM", "pi_mM", "FinalSucr", "DT_cycles_init"]

# x-VARIABLES (usually the fitness rank, but the independent variable can also be any other ouput parameter)
# Interesting if desired to analyze further dependencies between output parameters
x_variables = ["fitFunc", "NH4_mM", "DT_cycles_init"]


# SCATTERPLOTS FOR RANK 1

myplt.one_plot(x_variables[0], y_variables[0], configResults_fitRank1, x_variables[0]+y_variables[0], "Final NH4 vs. fitness")
myplt.one_plot(x_variables[0], y_variables[1], configResults_fitRank1, x_variables[0]+y_variables[1], "Final Pi vs. fitness")
myplt.one_plot(x_variables[0], y_variables[2], configResults_fitRank1, x_variables[0]+y_variables[2], "Final Sucr vs. fitness")
# myplt.one_plot(x_variables[0], y_variables[3], configResults_fitRank1, x_variables[0]+y_variables[3], "Init Death Cycle vs. fitness")

myplt.one_plot(x_variables[1], y_variables[1], configResults_fitRank1, x_variables[1]+y_variables[1], "Final Pi vs. Final NH4")
myplt.one_plot(x_variables[1], y_variables[2], configResults_fitRank1, x_variables[1]+y_variables[2], "Final Sucrose vs. Final NH4")

# myplt.one_plot(x_variables[2], y_variables[1], configResults_fitRank1, x_variables[2], y_variables[1], "Final Pi vs. Death Init Cycle")
# myplt.one_plot(x_variables[2], y_variables[2], configResults_fitRank1, x_variables[2], y_variables[2], "Final Sucrose vs. Death Init Cycle")


# SCATTERPLOTS FOR RANK 2
# [...]

# SCATTERPLOTS FOR RANK 3
# [...]


# Es poco práctico imponer títulos de plot que van a tener que ser cambiados con cada ejecución de usuario, de forma manual
# Y crear un parámetro de título para cada plot incrementa en exceso el número de parámetros que incluir en una potencial función
# Necesito otra solución a este nivel



















