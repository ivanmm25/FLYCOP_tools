#!/usr/bin/env python3
# -*- coding: utf-8 -*-

############ FLYCOP ############
# Author: Iván Martín Martín
# August 2021
################################

"""
Created on Sat Sep 11 16:53:16 2021
@author: IVÁN MARTÍN MARTÍN
"""

"""
DESCRIPTION - BIOMASS & PRODUCTION ANALYSIS after a FLYCOP run
Pipeline of Selection of Consortium Architecture
-------------------------------------------------------------------------------
(A priori, this script has to be run by the user once the FLYCOP run has already finished)

The current analysis is centered on the evaluation of final biomass and nutrient
state in a given FLYCOP run. This analysis is applied after filtering the configurations according to:
        
        i) Consortium Architecture: i.e. 2_models vs. 3_models
    
        ii) Acceptable vs. suboptimal configurations in COBRA terms: i.e. only 
            Acceptable configurations are considered
            
        iii) effects of biomass loss: further sub-analysis
    
    
GENERAL USE
-----------

    * FILE LOCATION: this script is located at ./MainFolder/Scripts, while the 
    execution files are in ./MainFolder/FLYCOP_analysis (see command line use)
    
    * COMMAND LINE USE: how to run the script. 
    Example: python3 BiomassProductionAnalysis.py '2_models 3_models' ../FLYCOP_analysis ./InputFiles BiomassNutrientAnalysis_input.txt
    
    * No changes are needed in the current script, for the moment.
    

REQUIRED FILES
--------------

     * configurationResults_consArchitecture.xlsx
    
    * Main files at ./MainFolder/FLYCOP_analysis/InputFiles folder
    ---------------------------------------------------------------------------
      - NO blank spaces, comma as separator character except for the colon
      - Header lines are not considered (those starting by '#'), they have just 
      organizational purposes
      
      - RESULT: dictionary type (key:values) or list type
      
    EXAMPLES:
        
        BiomassNutrientAnalysis_input.txt (dictionary type)
        -----------------------------------------------------
        
        # Biomasses by Consortium Architecture
        3_models:init_iJN1463,init_iEC1364Wger,init_iEC1364W,final_iJN1463,final_iEC1364Wger,final_iEC1364W
        2_models:init_iJN1463,init_iEC1364Wuger,final_iJN1463,final_iEC1364Wuger
        # Global Biomass Analysis
        global_biomass:global_init_biomass,global_final_biomass
        # Nutrient Analysis
        nutrientAnalysis:GerNar_mM,Nar_mM,NH4_mM,pi_mM,FinalSucr_mM,FinalO2_mM
        # EndCycle Nutrient Analysis
        endCycleNutrientAnalysis:sucrcycle,nh4cycle,picycle,o2cycle,endCycle
        initCycleNutrientAnalysis:6gernarcycle,narcycle
        # Intermediate-to-End product relationship
        productRelationship:GerNar_mM,Nar_mM
        
        
SCRIPT DESIGN
-------------

    * PARSING PARAMETERS
    * WORKING DIRECTORY AND MAIN FILE (configurationResults table)
    * OTHER INPUT FILES
    
    1. SPECIFIC STUDY OF BIOMASS (individual strain biomass and total biomass)
    
    2. FINAL CONCENTRATION COMPARATIVE OF END-PRODUCTS
    
    3. OTHER PRODUCTION PLOTS

    
TO-DO
-----
    
    * Always revisit documentation
    
"""


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import sys
import shutil
import subprocess
import openpyxl
import re

sys.path.append('../Utilities')
import MetabolicParameterPlotting as MetPlot


# -----------------------------------------------------------------------------
# PARSING PARAMETERS
# -----------------------------------------------------------------------------

# Reading the arguments given by command line
# COMMAND LINE USE: python3 BiomassProductionAnalysis.py '2_models 3_models' ../FLYCOP_analysis ./InputFiles BiomassNutrientAnalysis_input.txt

cons_architecture_series = sys.argv[1]  # e.g. '2_models 3_models'
folder_name = sys.argv[2]  # e.g. '../FLYCOP_analysis' (complete path)
input_files_folder = sys.argv[3]  # e.g. './InputFiles' (path with respect to folder_name variable)
BiomassNutrientAnalysis_input_dictionary_file = sys.argv[4]  # e.g. 'BiomassNutrientAnalysis_input.txt' (just the filename)


# -----------------------------------------------------------------------------
# WORKING DIRECTORY AND MAIN FILE (configurationResults table)
# -----------------------------------------------------------------------------

# ORIGINAL OUTPUT PATH
output_path = f"{folder_name}"  # CHANGE DIR to the FLYCOP run folder where the analysis should be performed
os.chdir(output_path)
output_path = os.getcwd()

# OUTPUT FOLDER
if os.path.isdir("BiomassProductionAnalysis"): shutil.rmtree("BiomassProductionAnalysis")
if not os.path.isdir("BiomassProductionAnalysis"):
    os.mkdir("BiomassProductionAnalysis")  # Create "BiomassProductionAnalysis" directory
output_folder = output_path+"/BiomassProductionAnalysis"

# EXCEL FILE containing configurationResults table
configResults_excel = "configurationResults_consArchitecture.xlsx"  # Common name

# Consortium Architecture options
cons_architecture_list = cons_architecture_series.split()
    
# READ GLOBAL DATAFRAME FOR FURTHER PLOTTING COMPARISON
global_dataframe_architectures = pd.read_excel("global_dataframe_architectures.xlsx", engine="openpyxl")

# SUBSEQUENT FILTERING OF CONFIGURATIONS
# Fitness evaluation: configurations with i) acceptable SD; ii) optimal solutions in COBRA terms (i.e. acceptable)
filtered_global_dataframe_architecture = global_dataframe_architectures[(global_dataframe_architectures["ID_SD"] == 0) & 
                                                                        (global_dataframe_architectures["ConfigKey"] == "Acceptable")]


# IN CASE THERE ARE CONFIGURATIONS WITH BIOMASS LOSS
if filtered_global_dataframe_architecture[filtered_global_dataframe_architecture["BiomassLoss"] == "BL"].count()[0] > 0:
    filtered_global_dataframe_architecture_nonBL = filtered_global_dataframe_architecture[filtered_global_dataframe_architecture["BiomassLoss"] != "BL"]
    biomassLoss = True
else: biomassLoss = False


# -----------------------------------------------------------------------------
# INPUT FILE
# -----------------------------------------------------------------------------
# FILE ON INPUT: file to dictionary of variables
biomassNutrientAnalysis_dictionary = MetPlot.parsing_external_file_to_dict(input_files_folder+"/"+BiomassNutrientAnalysis_input_dictionary_file)
global_biomass_list = biomassNutrientAnalysis_dictionary["global_biomass"]
nutrients_list = biomassNutrientAnalysis_dictionary["nutrientAnalysis"]
endcycle_nutrients_list = biomassNutrientAnalysis_dictionary["endCycleNutrientAnalysis"]
initcycle_nutrients_list = biomassNutrientAnalysis_dictionary["initCycleNutrientAnalysis"]
product_relationship = biomassNutrientAnalysis_dictionary["productRelationship"]

# In the original 'biomassNutrientAnalysis_dictionary_file', there are keys which are not consortium architecture categories
# Thus they should be deleted for the SPECIFIC STUDY OF BIOMASS representation
delete_keys = []
for key in biomassNutrientAnalysis_dictionary.keys():
    if not re.search("[\d]+_models", key):
        delete_keys.append(key)
        
for key in delete_keys: biomassNutrientAnalysis_dictionary.pop(key, "Key not found")

# CHANGE DIR TO THE OUTPUT FOLDER
os.chdir("BiomassProductionAnalysis")
###############################################################################


# -----------------------------------------------------------------------------
# (1) SPECIFIC STUDY OF BIOMASS
    # Including biomass loss cases
    # Without including biomass loss cases
# -----------------------------------------------------------------------------
# BUILD BIOMASS DATAFRAME FOR PLOTTING INDIVIDUAL BIOMASS
# -----------------------------------------------------------------------------

# Final Biomass Dataframe
columns=["Biomass (g/L)", "Microbial model", "Moment during simulation", "Consortium Architecture", "ConfigKey", "ID_SD", "BiomassLoss"]
final_biomassDataframe = pd.DataFrame(columns=columns)

# WRITE AN INDIVIDUAL BIOMASS DATAFRAME
for biomassKey in biomassNutrientAnalysis_dictionary.keys():
    
    configResults = pd.read_excel("../"+configResults_excel, sheet_name=biomassKey, engine="openpyxl")
    for init_biomass in biomassNutrientAnalysis_dictionary[biomassKey]:
        
        fraction_biomassKey_df = pd.DataFrame(columns=columns)
        fraction_biomassKey_df["Biomass (g/L)"] = configResults[init_biomass]
        fraction_biomassKey_df["Microbial model"] = init_biomass.split('_')[1]
        fraction_biomassKey_df["Moment during simulation"] = init_biomass.split('_')[0]
        fraction_biomassKey_df["Consortium Architecture"] = biomassKey
        fraction_biomassKey_df["ConfigKey"] = configResults["ConfigKey"]
        fraction_biomassKey_df["ID_SD"] = configResults["ID_SD"]
        fraction_biomassKey_df["BiomassLoss"] = configResults["BiomassLoss"]
        
        final_biomassDataframe = pd.concat([final_biomassDataframe, fraction_biomassKey_df], ignore_index = True)
        
    
final_biomassDataframe.to_excel("biomassDataframe.xlsx", engine="openpyxl", header=True, index=False, index_label=None)
filtered_final_biomassDataframe = final_biomassDataframe[(final_biomassDataframe["ID_SD"] == 0) & (final_biomassDataframe["ConfigKey"] == "Acceptable")]
filtered_final_biomassDataframe = filtered_final_biomassDataframe.copy()  # Avoid 'Setting With Copy Warning'

# CHANGE CODIFICATION OF "BiomassLoss" COLUMN in dataframe
# "Biomass Loss": Biomass Loss (1), "non-Biomass Loss": "non Biomass Loss" (0,-1)
for row in filtered_final_biomassDataframe.itertuples():
    row_index = row[0]
    if filtered_final_biomassDataframe.loc[row_index, "BiomassLoss"] == 1:
        filtered_final_biomassDataframe.loc[row_index, "BiomassLoss"] = "Biomass Loss"
    else:
        filtered_final_biomassDataframe.loc[row_index, "BiomassLoss"] = "non-Biomass Loss"
        
        
# IN CASE THERE ARE CONFIGURATIONS WITH BIOMASS LOSS. Note 'filtered_final_biomassDataframe' is a different dataframe
if biomassLoss:
    filtered_final_biomassDataframe_nonBL = filtered_final_biomassDataframe[filtered_final_biomassDataframe["BiomassLoss"] == "non-Biomass Loss"]
    
###############################################################################

# INDIVIDUAL BIOMASS ANALYSIS
# -----------------------------------------------------------------------------
MetPlot.biomass_plotting(cons_architecture_list=cons_architecture_list, 
                         biomassDataframe=filtered_final_biomassDataframe, 
                         plotname="allCases")

if biomassLoss:
    MetPlot.biomass_plotting(cons_architecture_list=cons_architecture_list, biomassDataframe=filtered_final_biomassDataframe_nonBL, 
                             plotname="nonBL")
  
    
    
# GLOBAL BIOMASS ANALYSIS
# -----------------------------------------------------------------------------
MetPlot.axes_level_scatterplot(global_biomass_list, filtered_global_dataframe_architecture, 
                               plot_title="globalBiomass", suptitle=None, legend=False)

###############################################################################


# -----------------------------------------------------------------------------
# (2) FINAL CONCENTRATION COMPARATIVE OF END-PRODUCTS
# Further subdivision by biomass loss effect
# -----------------------------------------------------------------------------

# DIRECT COMPARATIVE
# TO-DO: also put on record initial nutrient concentrations

MetPlot.axes_level_scatterplot(variables_list=nutrients_list, dataframe=filtered_global_dataframe_architecture, 
                               plot_title="NutrientAnalysis", suptitle=None, legend=False)


# ENDCYCLE FOR SUBSTRATE CONSUMPTION

MetPlot.axes_level_scatterplot(variables_list=endcycle_nutrients_list, dataframe=filtered_global_dataframe_architecture, 
                               plot_title="endCycleNutrientAnalysis",ncols=5, suptitle=None, legend=False)

MetPlot.statistics_description(filtered_global_dataframe_architecture, hue="Consortium_Arch", 
                               descriptive_columns=endcycle_nutrients_list, filename="endcycleSubstrates")

if biomassLoss:
    MetPlot.statistics_description(filtered_global_dataframe_architecture_nonBL, hue="Consortium_Arch", 
                                   descriptive_columns=endcycle_nutrients_list, filename="endcycleSubstrates_nonBL")



# INITCYCLE FOR END-PRODUCTS SECRETION

MetPlot.axes_level_scatterplot(variables_list=initcycle_nutrients_list, dataframe=filtered_global_dataframe_architecture, 
                               plot_title="initCycleNutrientAnalysis", suptitle=None, legend=False)

MetPlot.statistics_description(filtered_global_dataframe_architecture, hue="Consortium_Arch", 
                               descriptive_columns=initcycle_nutrients_list, filename="initcycleProducts")

if biomassLoss:
    MetPlot.statistics_description(filtered_global_dataframe_architecture_nonBL, hue="Consortium_Arch", 
                                   descriptive_columns=initcycle_nutrients_list, filename="initcycleProducts_nonBL")


# -----------------------------------------------------------------------------
# (3) OTHER PRODUCTION PLOTS
# Further subdivision by biomass loss effect
# -----------------------------------------------------------------------------

sns.set_theme(style="darkgrid")
legend="auto"

# Function variables for plotting 
x=product_relationship[1]
y=product_relationship[0]
hue="Consortium_Arch"
hue_categories = filtered_global_dataframe_architecture[hue].unique()  # Categories in the given 'hue' parameter, numpy array
n_cat = len(hue_categories)  
ncols = 2 if biomassLoss else 1

# Create Global Figure
figsize = (6 * ncols, 8)
global_figure, axes = plt.subplots(num=0, clear=True, figsize=figsize, nrows=1, ncols=ncols)
plt.tight_layout(pad=4, h_pad=4, w_pad=4, rect=None)  # Margins between subplots


# With cases of biomass loss, create a global figure with all cases, and filtered cases without the given effect
if biomassLoss:
    
    sns.scatterplot(ax=axes[0], data=filtered_global_dataframe_architecture, x=x, y=y, hue=hue, legend=True)
    sns.scatterplot(ax=axes[1], data=filtered_global_dataframe_architecture_nonBL, x=x, y=y, hue=hue, legend=False)
    
    n_axes = [0, 0, 1, 1]
    dataframes = [filtered_global_dataframe_architecture, filtered_global_dataframe_architecture_nonBL]

    for ax, category in zip(n_axes, hue_categories.tolist() * 2):
        dataframe = dataframes[ax]
        sns.regplot(ax=axes[ax], x=x, y=y, scatter=False, data=dataframe[dataframe[hue] == category])
    

# With no cases of biomass loss, the figure displays a single plot
else:
    sns.scatterplot(ax=axes, data=filtered_global_dataframe_architecture, x=x, y=y, hue=hue, legend=True)
    for category in hue_categories:
        sns.regplot(ax=axes, x=x, y=y, scatter=False, data=filtered_global_dataframe_architecture[filtered_global_dataframe_architecture[hue] == category])


# Save Global Figure
if biomassLoss: global_figure.suptitle("Left plot: all cases. Right plot: non-biomass loss cases", fontsize = 10, fontfamily='DejaVu Sans')
global_figure.savefig("{0}_vs_{1}_scatter.png".format(y, x))
plt.close(global_figure)


os.chdir("..")
###############################################################################




