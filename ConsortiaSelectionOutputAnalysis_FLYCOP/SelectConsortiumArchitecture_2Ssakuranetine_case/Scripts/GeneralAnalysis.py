#!/usr/bin/env python3
# -*- coding: utf-8 -*-

############ FLYCOP ############
# Author: Iván Martín Martín
# August 2021
################################

"""
Created on Sun July 11 11:02:18 2020
@author: Iván Martín Martín
"""

"""
DESCRIPTION - GENERAL ANALYSIS after a FLYCOP run
Pipeline of Selection of Consortium Architecture
-------------------------------------------------------------------------------
(A priori, this script has to be run by the user once the FLYCOP run has already finished)


GENERAL USE
-----------

    * FILE LOCATION: this script is located at ./MainFolder/Scripts, while the 
    execution files are in ./MainFolder/FLYCOP_analysis (see command line use)
    
    * COMMAND LINE USE: how to run the script. 
    Example: python3 GeneralAnalysis.py '2_models 3_models' ../FLYCOP_analysis ./InputFiles configAnalysis_ratios.txt GeneralAnalysis_input.txt
    
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
        
        GeneralAnalysis_input.txt (dict type)
        ------------------------------------
        # Exchange rate analysis
        exchangeRates_discrete:sucr_upt,frc_upt,nh4_Ec,nh4_KT
        # FVA analysis
        FVAanalysis_discrete:FVApCA,FVAfru,FVAGerNar,FVANar
        # Statistical Description
        statsDescription:global_init_biomass,global_final_biomass,fitFunc,SD,MetNar_mM,Nar_mM,NH4_mM,pi_mM,FinalSucr_mM
        
        
        configAnalysis_ratios.txt (dictionary type)
        -------------------------------------------
        # RATIOS fitness_vs_ratio
        finalProducts_ratio:MetNar_mM,Nar_mM
        Cuptake_ratio:sucr_upt,frc_upt
        biomass_ratio:global_final_biomass,global_init_biomass

        ratio_name:two_parameters_to_calculate_ratio
        (Name of a given ratio: parameters for the ratio to be calculated - 
         numerator, denominator in that order)
         
        IMPORTANT: a ratio parameter name must end in '_ratio'
        
        
SCRIPT DESIGN
-------------

    * PARSING PARAMETERS
    * WORKING DIRECTORY AND MAIN FILE (configurationResults table)
    * OTHER INPUT FILES
    
    1. FOR EVERY POTENTIAL ARCHITECTURE EVALUATED THROUGH FLYCOP: calculate ratios 
    of those specified input variables in "configAnalysis_ratios.txt"
    
    2. COMPOSE A GLOBAL DATAFRAME with details of all possible architectures
    
    3. COMPARISON OF ACCEPTABLE vs. NON-OPTIMAL ARCHITECTURES, BY MODEL ARCHITECTURE
    (barplot of configurations)
    
    4, 5. PLOTTING configurations (always acceptable SD)
    
        A) Acceptable and NonOptimal in COBRA terms
        B) Acceptable in COBRA terms
    
        - SCATTER-BOXPLOT for continuous input variables
        - HISTOGRAM for discrete input variables
    
    6. STATISTICAL DESCRIPTION OF KEY VARIABLES through Pandas.describe()
        
    
TO-DO
-----
    
    * Always revisit documentation
    
"""


# import re
import sys
import pandas as pd
import os.path
import openpyxl
import shutil
import math
import matplotlib.pyplot as plt
scripts_path = os.getcwd()

# import Plotting as myplt
sys.path.append('../Utilities')
import MetabolicParameterPlotting as MetPlot


# -----------------------------------------------------------------------------
# MAIN CODE
# =============================================================================
# PARSING PARAMETERS
# -----------------------------------------------------------------------------

# Reading the arguments given by command line
# Instead of command line args, these variables can be specified here as strings
# COMMAND LINE USE: 
# python3 GeneralAnalysis.py '2_models 3_models' ../FLYCOP_analysis ./InputFiles configAnalysis_ratios.txt GeneralAnalysis_input.txt

cons_architecture_series = sys.argv[1]  # e.g. '2_models 3_models'
folder_name = sys.argv[2]  # e.g. '../FYCOP_analysis' (complete path)
input_files_folder = sys.argv[3]  # e.g. './InputFiles' (path with respect to folder_name variable)
ratios_file = sys.argv[4]  # e.g. 'configAnalysis_ratios.txt' (just the filename)
input_variables_dictionary_file = sys.argv[5]  # e.g. 'GeneralAnalysis_input.txt' (just the filename)


# -----------------------------------------------------------------------------
# WORKING DIRECTORY AND MAIN FILE (configurationResults table)
# -----------------------------------------------------------------------------

# ORIGINAL OUTPUT PATH
output_path = f"{folder_name}"  # CHANGE DIR to the FLYCOP run folder where the analysis should be performed
os.chdir(output_path)
output_path = os.getcwd()

# OUTPUT FOLDER within the ORIGINAL OUTPUT PATH
if os.path.isdir("GeneralAnalysis"): shutil.rmtree("GeneralAnalysis")
if not os.path.isdir("GeneralAnalysis"):
    os.mkdir("GeneralAnalysis")  # Create "GeneralAnalysis" directory
output_folder = output_path+"/GeneralAnalysis"

# EXCEL FILE containing configurationResults table
configResults_excel = "configurationResults_consArchitecture.xlsx"  # Common name

# (Future) EXCEL FILE including ratios of input variables
configResults_excel_ratios = "configurationResults_consArchitecture_ratios.xlsx"  # New name
modified_excelfile = openpyxl.Workbook(configResults_excel_ratios)
modified_excelfile.save(filename=configResults_excel_ratios)

# Consortium Architecture options
cons_architecture_list = cons_architecture_series.split()


# -----------------------------------------------------------------------------
# OTHER INPUT FILES
# -----------------------------------------------------------------------------

# Dictionary of ratios to be calculated and included in the configurationResults table
ratios_dict = MetPlot.parsing_external_file_to_dict(input_files_folder+"/"+ratios_file)

# FILE ON INPUT: file to dictionary of variables
input_variables_dictionary = MetPlot.parsing_external_file_to_dict(input_files_folder+"/"+input_variables_dictionary_file)

# Retrieve statistical descriptive variables
descriptive_columns = input_variables_dictionary["statsDescription"]

# Remove the last key from the dictionary for further plotting
input_variables_dictionary.pop("statsDescription", "Key not found")
###############################################################################


# -----------------------------------------------------------------------------
# (1) FOR EVERY POTENTIAL ARCHITECTURE EVALUATED THROUGH FLYCOP: RATIO CALCULATION
# -----------------------------------------------------------------------------

with pd.ExcelFile(configResults_excel, engine="openpyxl") as xls:
    for architecture in xls.sheet_names:  # Every sheet_name is a different architecture
        if architecture == "Sheet": continue
    
        # INITIAL READING OF EXCEL FILE
        configResults = pd.read_excel(xls, sheet_name=architecture, engine="openpyxl")


        # (A) READ INPUT PARAMETERS TO ANALYZE & OBTAIN DESIRED RATIOS
        # ---------------------------------------------------------------------
        configResults_copy = configResults.copy()  # Avoid 'SettingWithCopyWarning'
        
        for ratio_name in ratios_dict.keys():
            splitted_ratio_name = ratio_name.split("_")
            if splitted_ratio_name[len(splitted_ratio_name)-1] == "ratio":
                
                try:
                    configResults_copy[ratio_name] = round(configResults_copy[ratios_dict[ratio_name][0]], 4) / round(configResults_copy[ratios_dict[ratio_name][1]], 4)
                except ZeroDivisionError:
                    configResults_copy[ratio_name] = "NaN"
                    
                    
        # (B) DATAFRAME COPY with ratios to EXCEL
        # SAVE NEW EXCEL FILE with ratios of desired input variables
        # ---------------------------------------------------------------------
        
        with pd.ExcelWriter(configResults_excel_ratios, engine='openpyxl', mode='a') as writer:
            configResults_copy.to_excel(writer, sheet_name=architecture, header=True, index=False, index_label=None)
            writer.save()
        modified_excelfile.close()

# Recall CLOSE: (Future) EXCEL FILE including ratios of input variables  
modified_excelfile.close()
###############################################################################



# -----------------------------------------------------------------------------
# (2) COMPOSE A GLOBAL DATAFRAME with details of all possible architectures
# -----------------------------------------------------------------------------

# Global dataframe with details of all consortium architectures for further plotting purposes
columns = configResults.columns
global_dataframe_architectures = pd.DataFrame(columns=columns)

with pd.ExcelFile(configResults_excel, engine="openpyxl") as xls:
    for architecture in xls.sheet_names:  # Every sheet_name is a different architecture
        if architecture == "Sheet": continue
        
        configResults = pd.read_excel(xls, sheet_name=architecture)
        fraction_configResults = configResults[configResults.columns]
        global_dataframe_architectures = pd.concat([global_dataframe_architectures, fraction_configResults], ignore_index = True)


# CHANGE CODIFICATION OF "BiomassLoss" COLUMN in dataframe
# "BL": Biomass Loss (1), "nonBL": "non Biomass Loss" (0,-1)

# Add a new KeyColumn integrating Consortium_Arch + BiomassLoss ("ConsArch_BiomassLoss")
# "3_models_BL", "3_models_nonBL", "2_models_BL", "2_models_nonBL"
global_dataframe_architectures["ConsArch_BiomassLoss"] = 0
for row in global_dataframe_architectures.itertuples():
    row_index = row[0]
    
    if global_dataframe_architectures.loc[row_index, "BiomassLoss"] == 1:
        global_dataframe_architectures.loc[row_index, "BiomassLoss"] = "BL"
        global_dataframe_architectures.loc[row_index, "ConsArch_BiomassLoss"] = global_dataframe_architectures.loc[row_index, "Consortium_Arch"]+"_BL"
        
    # Eventual biomass losses that do not render the consortium inviable are considered as "nonBL" (i.e. "BiomassLoss" == -1)
    else:
        global_dataframe_architectures.loc[row_index, "BiomassLoss"] = "nonBL"
        global_dataframe_architectures.loc[row_index, "ConsArch_BiomassLoss"] = global_dataframe_architectures.loc[row_index, "Consortium_Arch"]+"_nonBL"
        
        
# Save 'global_dataframe_architectures' in xlsx format for further plotting purposes
global_dataframe_architectures.to_excel("global_dataframe_architectures.xlsx", header=True, index=False, index_label=None)
        
# FILTERING CONFIGURATIONS by Standard Deviation (non-higher than 10% of average fitness)
global_dataframe_architectures_SD = global_dataframe_architectures[(global_dataframe_architectures["ID_SD"] == 0)]

# CHANGE DIR TO THE OUTPUT FOLDER
os.chdir("GeneralAnalysis")
###############################################################################
    


# -----------------------------------------------------------------------------
# (3) COMPARISON OF ACCEPTABLE vs. NON-OPTIMAL ARCHITECTURES, BY MODEL ARCHITECTURE
# -----------------------------------------------------------------------------

    # SD acceptable
    # Acceptable vs. Non-optimal configurations
    # Biomass loss vs. non-biomass loss
    # Subdivision by model architecture
    
# BARPLOT OF CONFIGURATIONS
    # x_variable: x-axis ("Consortium_Arch")
    # first_categorical: hue ("BiomassLoss")
    # second_categorical: column ("ConfigKey")

MetPlot.barplot_of_configurations(global_dataframe_architectures_SD, x_variable="Consortium_Arch", 
                                  first_categorical="BiomassLoss", second_categorical="ConfigKey", 
                                  filename="configurations_histogram")
###############################################################################



# ---------------------------------------------------------------------
# (4) PLOTTING all configurations
# Acceptable and NonOptimal (always acceptable SD)
# Further distinction by biomass loss vs. non-biomass loss
# ---------------------------------------------------------------------
if not os.path.isdir("Plots_allConfigs"):
    os.mkdir("Plots_allConfigs")  # Create "Plots_allConfigs" directory
os.chdir("Plots_allConfigs")
        
# PLOTTING
for analysis_domain in input_variables_dictionary.keys(): 

    variable_type = analysis_domain.split("_")[1]
    
    if variable_type == "continuous": 
        MetPlot.axes_level_scatterplot(input_variables_dictionary[analysis_domain], global_dataframe_architectures_SD, 
                                       plot_title=analysis_domain, suptitle=None, legend=False)
    
    elif variable_type == "discrete": 
        MetPlot.axes_level_histplot(input_variables_dictionary[analysis_domain], 
                                    global_dataframe_architectures_SD[(global_dataframe_architectures_SD["BiomassLoss"] != "BL")], 
                                    plot_title=analysis_domain+"_nonBL", suptitle=None)
             
        MetPlot.axes_level_scatterplot(input_variables_dictionary[analysis_domain], 
                                       global_dataframe_architectures_SD[(global_dataframe_architectures_SD["BiomassLoss"] != "BL")], 
                                       plot_title=analysis_domain+"_nonBL", suptitle=None, single_scatter=True)
            
            
        if global_dataframe_architectures_SD[global_dataframe_architectures_SD["BiomassLoss"] == "BL"].count()[0] > 0:
                
            MetPlot.axes_level_histplot(input_variables_dictionary[analysis_domain], 
                                        global_dataframe_architectures_SD[(global_dataframe_architectures_SD["BiomassLoss"] == "BL")], 
                                        plot_title=analysis_domain+"_BL", suptitle=None)
                
            MetPlot.axes_level_scatterplot(input_variables_dictionary[analysis_domain], 
                                           global_dataframe_architectures_SD[(global_dataframe_architectures_SD["BiomassLoss"] == "BL")], 
                                           plot_title=analysis_domain+"_BL", suptitle=None, single_scatter=True)
                
        
os.chdir(output_path)
###############################################################################
        

# ---------------------------------------------------------------------
# (5) PLOTTING Acceptable configurations, if there are ALSO non optimal solutions.
# Otherwise, skip this plotting section.
# Always acceptable SD
# Further distinction by biomass loss vs. non-biomass loss
# ---------------------------------------------------------------------
if global_dataframe_architectures_SD[global_dataframe_architectures_SD["ConfigKey"] != "Acceptable"].count()[0] > 0:
            
    if not os.path.isdir("Plots_AccConfigs"):
        os.mkdir("Plots_AccConfigs")  # Create "Plots_AccConfigs" directory
    os.chdir("Plots_AccConfigs")
            
    # FILTERING
    global_dataframe_architectures_SD_Acceptable = global_dataframe_architectures_SD[(global_dataframe_architectures_SD["ConfigKey"] == "Acceptable")]
    
    # PLOTTING
    for analysis_domain in input_variables_dictionary.keys(): 

        variable_type = analysis_domain.split("_")[1]
        
        if variable_type == "continuous": 
            MetPlot.axes_level_scatterplot(input_variables_dictionary[analysis_domain], global_dataframe_architectures_SD_Acceptable, 
                                           plot_title=analysis_domain, suptitle=None, legend=False)
        
        
        elif variable_type == "discrete": 
            MetPlot.axes_level_histplot(input_variables_dictionary[analysis_domain], 
                                        global_dataframe_architectures_SD_Acceptable[(global_dataframe_architectures_SD_Acceptable["BiomassLoss"] != "BL")], 
                                        plot_title=analysis_domain+"_nonBL", suptitle=None)
            
            MetPlot.axes_level_scatterplot(input_variables_dictionary[analysis_domain], 
                                           global_dataframe_architectures_SD_Acceptable[(global_dataframe_architectures_SD_Acceptable["BiomassLoss"] != "BL")], 
                                           plot_title=analysis_domain+"_nonBL", suptitle=None, single_scatter=True)
            
            
            if global_dataframe_architectures_SD_Acceptable[global_dataframe_architectures_SD_Acceptable["BiomassLoss"] == "BL"].count()[0] > 0:
                MetPlot.axes_level_histplot(input_variables_dictionary[analysis_domain], 
                                            global_dataframe_architectures_SD_Acceptable[(global_dataframe_architectures_SD_Acceptable["BiomassLoss"] == "BL")], 
                                            plot_title=analysis_domain+"_BL", suptitle=None)
                
                MetPlot.axes_level_scatterplot(input_variables_dictionary[analysis_domain], 
                                               global_dataframe_architectures_SD_Acceptable[(global_dataframe_architectures_SD_Acceptable["BiomassLoss"] == "BL")], 
                                               plot_title=analysis_domain+"_BL", suptitle=None, single_scatter=True)
    
    
    os.chdir(output_path)
###############################################################################


# ---------------------------------------------------------------------
# (6) STATISTICAL DESCRIPTION OF KEY VARIABLES
# ---------------------------------------------------------------------

os.chdir(output_folder)

filtered_global_dataframe_architecture = global_dataframe_architectures_SD[global_dataframe_architectures_SD["ConfigKey"] == "Acceptable"]
filtered_global_dataframe_architecture_nonBL = filtered_global_dataframe_architecture[filtered_global_dataframe_architecture["BiomassLoss"] != "BL"]


# Acceptable configurations with and without biomass loss
MetPlot.statistics_description(filtered_global_dataframe_architecture, hue="Consortium_Arch", 
                               descriptive_columns=descriptive_columns, filename="AcceptableGeneral")

# Acceptable configurations without biomass loss
MetPlot.statistics_description(filtered_global_dataframe_architecture_nonBL, hue="Consortium_Arch", 
                               descriptive_columns=descriptive_columns, filename="AcceptableGeneral_nonBL")


# BACK TO THE ORIGINAL DIRECTORY
os.chdir(scripts_path)
###############################################################################
















