#!/usr/bin/python3

############ FLYCOP ############
# Author: Iván Martín Martín
# August 2021
################################

"""
DESCRIPTION - PAIRWISE VARIABLE ANALYSIS after a FLYCOP run
Pipeline of Selection of Consortium Architecture
-------------------------------------------------------------------------------
(A priori, this script has to be run by the user once the FLYCOP run has already finished)

The current analysis is centered on the evaluation of the inter-relationship 
between input and output variables, including fitness, of a given FLYCOP run.
This analysis is applied after filtering the configurations according to:
        
        i) Consortium Architecture: i.e. 2_models vs. 3_models
    
        ii) Acceptable vs. suboptimal configurations in COBRA terms: i.e. only 
            Acceptable configurations are considered
            
        iii) effects of biomass loss: i.e. biomass loss cases are usually discarded
    
The analyses are developed by using different types of plots (scatterplot, boxplots, 
                                                              heatmaps, kdeplots, etc)
    
    
GENERAL USE
-----------

    * FILE LOCATION: this script is located at ./MainFolder/Scripts, while the 
    execution files are in ./MainFolder/FLYCOP_analysis (see command line use)
    
    * COMMAND LINE USE: how to run the script. 
    Example: python3 PairwiseVariableAnalysis.py '2_models 3_models' ../FLYCOP_analysis ./InputFiles PairwiseVariableAnalysis_input.txt
    
    * No changes are needed in the current script, for the moment.
    

REQUIRED FILES
--------------

     * configurationResults_consArchitecture.xlsx
    
    * Main files at ./MainFolder/FLYCOP_analysis/InputFiles folder
    ---------------------------------------------------------------------------
      - NO blank spaces, comma as separator character except for the colon
      - Header lines are not considered (those starting by '#'), they have just 
      organizational purposes
      - Avoid use of '_' character except for the ratio parameter names
      
      - RESULT: dictionary type (key:values) or list type
      
    EXAMPLES:
        
        PairwiseVariableAnalysis_input.txt (dictionary type)
        -----------------------------------------------------
        
        # Scatterplot matrix variables (dict format)
        scattermatrix:sucr_upt,frc_upt,nh4_Ec,nh4_KT,global_init_biomass,global_final_biomass,GerNar_mM
        # Heatmap variables (dict format)
        heatmap:sucr_upt,frc_upt,nh4_Ec,nh4_KT,global_init_biomass,global_final_biomass,GerNar_mM
        # FVA analysis as Histogram
        FVAanalysis:FVAfru,FVApCA,FVANar,FVAGerNar


SCRIPT DESIGN
-------------

    * PARSING PARAMETERS
    * WORKING DIRECTORY AND MAIN FILE (configurationResults table)
    * OTHER INPUT FILES
    
    1. SCATTERPLOT: SD vs. fitness
    
    2. SCATTERPLOT MATRIX: pairwise relationships between quantitative variables
    
    3. HEATMAP with input variables values (values of parameters optimized by SMAC)
    
    4. FVA ANALYSIS (currently disabled)
    
    
TO-DO
-----
    
    * Always revisit documentation
    
"""

import re
import sys
import os.path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy import stats
import seaborn as sns
import math
import shutil, errno
# import cobra
# import tabulate
# import getopt
# import copy
# import csv
# import cobra.flux_analysis.variability
# import massedit
# import subprocess
# import statistics
# import importlib
# import optlang
# import spec

sys.path.append('../Utilities')
import MetabolicParameterPlotting as MetPlot


# -----------------------------------------------------------------------------
# PARSING PARAMETERS
# -----------------------------------------------------------------------------

# Reading the arguments given by command line
# COMMAND LINE USE: python3 PairwiseVariableAnalysis.py '2_models 3_models' ../FLYCOP_analysis ./InputFiles PairwiseVariableAnalysis_input.txt

cons_architecture_series = sys.argv[1]  # e.g. '2_models 3_models'
folder_name = sys.argv[2]  # e.g. '../FLYCOP_analysis' (complete path)
input_files_folder = sys.argv[3]  # e.g. './InputFiles' (path with respect to folder_name variable)
input_variables_dictionary_file = sys.argv[4]  # e.g. 'PairwiseVariableAnalysis_input.txt' (just the filename)


# -----------------------------------------------------------------------------
# WORKING DIRECTORY AND MAIN FILE (configurationResults table)
# -----------------------------------------------------------------------------

# ORIGINAL OUTPUT PATH
output_path = f"{folder_name}"  # CHANGE DIR to the FLYCOP run folder where the analysis should be performed
os.chdir(output_path)
output_path = os.getcwd()

# OUTPUT FOLDER
if os.path.isdir("PairwiseVariableAnalysis"): shutil.rmtree("PairwiseVariableAnalysis")
if not os.path.isdir("PairwiseVariableAnalysis"):
    os.mkdir("PairwiseVariableAnalysis")  # Create "PairwiseVariableAnalysis" directory
output_folder = output_path+"/PairwiseVariableAnalysis"

# EXCEL FILE containing configurationResults table
configResults_excel = "configurationResults_consArchitecture.xlsx"  # Common name

# Consortium Architecture options
cons_architecture_list = cons_architecture_series.split()
    
# READ GLOBAL DATAFRAME FOR FURTHER PLOTTING COMPARISON
global_dataframe_architectures = pd.read_excel("global_dataframe_architectures.xlsx", engine="openpyxl")

# SUBSEQUENT FILTERING OF CONFIGURATIONS
# Fitness evaluation: configurations with i) acceptable SD; ii) optimal solutions in COBRA terms (i.e. acceptable); iii) witouth biomass loss
filtered_global_dataframe_architecture = global_dataframe_architectures[(global_dataframe_architectures["ID_SD"] == 0) & 
                                                                        (global_dataframe_architectures["ConfigKey"] == "Acceptable") & 
                                                                        (global_dataframe_architectures["BiomassLoss"] == "nonBL")]


# -----------------------------------------------------------------------------
# INPUT FILE
# -----------------------------------------------------------------------------
# FILE ON INPUT: file to dictionary of variables
input_variables_dictionary = MetPlot.parsing_external_file_to_dict(input_files_folder+"/"+input_variables_dictionary_file)

# CHANGE DIR TO THE OUTPUT FOLDER
os.chdir("PairwiseVariableAnalysis")
###############################################################################


# -----------------------------------------------------------------------------
# (1) SCATTERPLOT: SD vs. fitness
# -----------------------------------------------------------------------------

    # SD acceptable
    # Acceptable configurations in COBRA terms
    # Configurations with and without biomass loss
    # Subdivision by model architecture

# -----------------------------------------------------------------------------

alternative_filtered_global_dataframe_architecture = global_dataframe_architectures[(global_dataframe_architectures["ID_SD"] == 0) & 
                                                                        (global_dataframe_architectures["ConfigKey"] == "Acceptable")] 

sns.set_style("darkgrid")
fit_scatter = plt.figure(num=0, clear=True, figsize=(7, 7))
sns.scatterplot(data=alternative_filtered_global_dataframe_architecture, x="fitFunc", y="SD", hue="Consortium_Arch", style="BiomassLoss")
plt.title("Fitness vs. SD", fontsize = 14)
fit_scatter.savefig("scatter_fitness_SD.png")
plt.close(fit_scatter)

###############################################################################


# -----------------------------------------------------------------------------
# (2) SCATTERPLOT MATRIX: pairwise relationships between quantitative variables
# -----------------------------------------------------------------------------

# Different model architectures are represented in different colours. See lateral legend!

    # SD acceptable
    # Acceptable configurations in COBRA terms
    # Configurations without biomass loss
    # Subdivision by model architecture

# -----------------------------------------------------------------------------

# Scatter variables list
scatter_variables = input_variables_dictionary["scattermatrix"]

adapted_scatter_table = filtered_global_dataframe_architecture[scatter_variables+["Consortium_Arch"]]
adapted_scatter_table_copy = adapted_scatter_table.copy()  # Avoid 'SettingWithCopyWarning'
 
for numeric_variable in scatter_variables: 
    adapted_scatter_table_copy[numeric_variable] = pd.to_numeric(adapted_scatter_table_copy[numeric_variable], errors='coerce') 

sns.set_style("darkgrid")
MetPlot.pairgrid_plot(adapted_scatter_table_copy, plot_name="general", categorical_column="Consortium_Arch")
###############################################################################


# -----------------------------------------------------------------------------
# (3) HEATMAP with input variables values (values of parameters optimized by SMAC)
# -----------------------------------------------------------------------------

# A different heatmap for every consortium architecture. Normal distribution of variables 
# is evaluated before representing the HeatMap through a Shapiro test. 

# If the variables considered in the pairwise relationship are normally distributed, 
# Pearson correlation coefficient is used. Otherwise, Spearman correlation coefficient is implemented.

    # SD acceptable, Acceptable configurations
    # Configurations without biomass loss
    # Subdivision by model architecture
    

# RETURN TO ORIGINAL OUTPUT PATH
os.chdir(output_path)
# -----------------------------------------------------------------------------

# Heatmap variables list
heatmap_variables = input_variables_dictionary["heatmap"]

# FOR EVERY POTENTIAL ARCHITECTURE EVALUATED THROUGH FLYCOP
with pd.ExcelFile(configResults_excel, engine="openpyxl") as xls:
    for architecture in xls.sheet_names:  # Every sheet_name is a different architecture
        if architecture == "Sheet": continue
        
        # (A) INITIAL READING OF EXCEL FILE
        configResults = pd.read_excel(xls, sheet_name=architecture)
        adapted_input_table = configResults[(configResults["ID_SD"] == 0) & (configResults["ConfigKey"] == "Acceptable") & (configResults["BiomassLoss"] != 1)]
        adapted_input_table = adapted_input_table[heatmap_variables]
        
        normal_distr = np.array([])  # Normal distribution: 0; Non-normal distribution: 1
        
        for column in adapted_input_table.columns:
            shapiro_test = stats.shapiro(adapted_input_table[column])  # p-value = shapiro_test[1]
            normal_distr = np.append(normal_distr, 0) if shapiro_test[1] > 0.05 else np.append(normal_distr, 1)  # Normal distribution if p-value > 0.05
        
        # Numpy to Pandas through reshape. Pandas dataframe with a single row indicating whether each of the 'heatmap_variables' are normally distributed or not
        normal_distr = pd.DataFrame(data=np.reshape(normal_distr, (1, len(normal_distr))), columns=heatmap_variables, dtype=np.float64)
        
        # Build a correlation matrix (as Pandas dataframe)
        corr_matrix = pd.DataFrame(columns=heatmap_variables, index=heatmap_variables, dtype=np.float64)
        
        for row in corr_matrix.itertuples():
            row_variable = row[0]
            
            for column in corr_matrix.columns:
                if normal_distr.loc[0, row_variable] == 0 and normal_distr.loc[0, column] == 0:
                    corr_matrix.loc[row_variable, column] = stats.pearsonr(adapted_input_table[row_variable], adapted_input_table[column])[0]
                else:
                    corr_matrix.loc[row_variable, column] = stats.spearmanr(adapted_input_table[row_variable], adapted_input_table[column])[0]
    
        # (B) DRAW HEATMAP
        # Return to output folder
        os.chdir(output_folder)
        
        heatmap = plt.figure(clear=True, figsize=(25, 15))
        plt.title("HeatMap_{0}".format(architecture), fontsize = 20, fontfamily='DejaVu Sans')
        sns.heatmap(corr_matrix, annot=True, cmap="bwr")
        heatmap.savefig("heatmap_{0}.png".format(architecture))
        plt.close(heatmap)
###############################################################################


# -----------------------------------------------------------------------------
# (4) FVA ANALYSIS
# -----------------------------------------------------------------------------

    # SD acceptable
    # Acceptable configurations in COBRA terms
    # Configurations without biomass loss
    # Subdivision by model architecture

# -----------------------------------------------------------------------------

""" Already performed in GeneralAnalysis.py as 'FVAanalysis_discrete_nonBL_countplot.png'
# FVA ANALYSIS DIR
os.mkdir("FVA_analysis")
os.chdir("FVA_analysis")


# FVA COMPARISON OF CONSORTIUM ARCHITECTURES (currently the best comparative option)
# ----------------------------------------------------------------------------------

# Histogram Format
MetPlot.axes_level_histplot(variables_list=input_variables_dictionary["FVAanalysis"], dataframe=filtered_global_dataframe_architecture, 
                            plot_title="FVA_comparison", suptitle=None)

# Scatterplot Format
# MetPlot. axes_level_scatterplot(variables_dict=FVA_analysis_dict, dataframe=filtered_global_dataframe_architecture, 
#                                 plot_title="FVA_comparison", suptitle=None, legend=False)

"""

os.chdir("..")
###############################################################################



