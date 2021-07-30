#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Sun July 11 11:02:18 2020

@author: Iván Martín Martín
"""

"""
DESCRIPTION - BASIC ANALYSIS after a FLYCOP run
Pipeline of Selection of Consortium Architecture
------------------------------------------------
(A priori, this script has to be run by the user once the FLYCOP run has already finished)


GENERAL USE
-----------

    * FILE LOCATION: The execution folder must be located accordingly to the Output Analysis utilities 
    (currently, in the 'OutputAnalysis' folder)
    
    * COMMAND LINE USE: how to run the script. 
    Example: python3 BasicAnalysis.py 2_models ../../2_models_FVA_testing2 2_models_FVA_testing2_BA.txt
    
    * No changes are needed in the current script, for the moment.


REQUIRED FILES
--------------

    * configurationResults_consArchitecture.xlsx
    
    * BasicAnalysis_specifications.txt (e.g. 2_models_FVA_testing2_BA.txt)
    ----------------------------------------------------------------------
      - NO blank spaces, comma as separator character except for the colon
      - Header lines are not considered (those starting by '#'), they have just 
      organizational purposes
      - Avoid use of '_' character except for the ratio parameter names
      
    
        # INDIVIDUAL_PLOTTING fitness_vs_param
        
        dict_name:series_of_params
        (Name of a given dictionary of parameters: series of parameters to be
         individually plotted as x-axis against fitness)
        
        Each of these dictionaries groups some related (input or output) parameters.


        # RATIOS fitness_vs_ratio

        ratio_name:two_parameters_to_calculate_ratio
         (Name of a given ratio: parameters for the ratio to be calculated - 
          numerator, denominator in that order)
         
         IMPORTANT: a ratio parameter name must end in '_ratio'


SCRIPT DESIGN
-------------

    * PARSING PARAMETERS & REQUIRED FILES
    * FOR EVERY POTENTIAL ARCHITECTURE EVALUATED THROUGH FLYCOP (general script loop)
    (the script has to be run for every consortium architecture in the ExcelFile)
    
    1. READ INPUT PARAMETERS TO ANALYZE from the BasicAnalysis_specifications.txt file
    
    2. OBTAIN DESIRED RATIOS (calculate ratios as indicated in the mentioned file)
    
    3. DATAFRAME COPY with ratios to EXCEL
    (Update the ExcelFile with the new calculated ratios)
    
    4. PLOTTING configurations (always acceptable SD)
    
        A) Acceptable and NonOptimal 
        B) Acceptable
    
    
TO-DO
-----
    
    * Improve plotting design
    
        - Title, axis names, combination of plots
        - Display of several (related) plots in the same .png file
        
    * Always revisit documentation
    
"""


# import re
import sys
import pandas as pd
import os.path
scripts_path = os.getcwd()

sys.path.append("../Utilities")
import Plotting as myplt


# -----------------------------------------------------------------------------
# MAIN CODE
# =============================================================================
# PARSING PARAMETERS & REQUIRED FILES
# -----------------------------------------------------------------------------

# Reading the arguments given by command line
# Instead of command line args, these variables can be specified here as strings

cons_architecture_list = sys.argv[1].split()  # e.g. '2_models 3_models'
folder_name = sys.argv[2]  # e.g. '../../OutputAnalysisFolder' (complete path)
params_file = sys.argv[3]  # e.g. '2_models_FVA_testing2_BA.txt' (just the filename)
# Command line use: python3 BasicAnalysis.py 2_models ../../2_models_FVA_testing2 2_models_FVA_testing2_BA.txt

# EXCEL FILE containing configurationResults table
configResults_excel = "configurationResults_consArchitecture.xlsx"  # Common name

output_path = f"{folder_name}"  # CHANGE DIR to the FLYCOP run folder where the analysis should be performed
os.chdir(output_path)

# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# (0) FOR EVERY POTENTIAL ARCHITECTURE EVALUATED THROUGH FLYCOP
# -----------------------------------------------------------------------------

with pd.ExcelFile(configResults_excel, engine="openpyxl") as xls:
    for architecture in xls.sheet_names:  # Every sheet_name is a different architecture
        if architecture == "Sheet": continue
    
        # INITIAL READING OF EXCEL FILE
        configResults = pd.read_excel(xls, sheet_name=architecture, engine="openpyxl")


        # ---------------------------------------------------------------------
        # (1) READ INPUT PARAMETERS TO ANALYZE
        # ---------------------------------------------------------------------
        parameters_dict = {}
        with open(params_file, "r") as params_file:
            
            lines = params_file.readlines()
            for line in lines:
                if len(line) > 1 and line[0] != "#":  # Avoid header or empty lines
                    line = line.strip("\n").split(":")
                    parameters_dict[line[0]] = line[1].split(",")  # List of variable names


        # ---------------------------------------------------------------------
        # (2) OBTAIN DESIRED RATIOS
        # ---------------------------------------------------------------------
        
        configResults_copy = configResults.copy()  # Avoid 'SettingWithCopyWarning'
        
        for param_name in parameters_dict.keys():
            splitted_param_name = param_name.split("_")
            if splitted_param_name[len(splitted_param_name)-1] == "ratio":
                
                try:
                    configResults_copy[param_name] = round(configResults_copy[parameters_dict[param_name][0]], 4) / round(configResults_copy[parameters_dict[param_name][1]], 4)
                except ZeroDivisionError:
                    configResults_copy[param_name] = "NaN"
                    
        # ---------------------------------------------------------------------
        # (3) DATAFRAME COPY with ratios to EXCEL
        # SAVE MODIFIED SHEET (update last arch_model sheet)
        # ---------------------------------------------------------------------
        
        with pd.ExcelWriter(configResults_excel, engine='openpyxl', mode='a') as writer:
            configResults_excelfile = writer.book
            try:
                configResults_excelfile.remove(configResults_excelfile[architecture])
            except:
                print("Worksheet does not exist")
            finally:
                configResults_copy.to_excel(writer, sheet_name=architecture, header=True, index=False, index_label=None)
                writer.save()


        # ---------------------------------------------------------------------
        # (4) PLOTTING all configurations
        # Acceptable and NonOptimal (always acceptable SD)
        # ---------------------------------------------------------------------
        if not os.path.isdir("Plots_allConfigs"+architecture):
            os.mkdir("Plots_allConfigs"+architecture)  # Create "Plots_allConfigs" directory
        os.chdir("Plots_allConfigs"+architecture)
        
        # FILTERING
        configResults_copy_SDacceptable = configResults_copy[configResults_copy["ID_SD"] == 0]
        
        # PLOTTING
        for param_name in parameters_dict.keys():
            splitted_param_name = param_name.split("_")
            
            if splitted_param_name[len(splitted_param_name)-1] == "ratio":
                myplt.one_plot(param_name, "fitFunc", configResults_copy_SDacceptable, "fitFunc_vs_"+param_name, "fitFunc_vs_"+param_name)
                
            else:  
                for param in parameters_dict[param_name]:  
                    # A este nivel, se podría intentar componer un panel único con todos los parámetros en cada elemento del diccionario
                    # e.g. inputParameters:sucr_upt,frc_upt,nh4_Ec,nh4_KT,endCycle
                    myplt.one_plot(param, "fitFunc", configResults_copy_SDacceptable, "fitFunc_vs_"+param, "fitFunc_vs_"+param)
        
        
        
        # ---------------------------------------------------------------------
        # (5) PLOTTING acceptable configurations
        # Only Acceptable (always acceptable SD)
        # ---------------------------------------------------------------------
        os.chdir(output_path)
        if not os.path.isdir("Plots_AccConfigs"+architecture):
            os.mkdir("Plots_AccConfigs"+architecture)  # Create "Plots_AccConfigs" directory
        os.chdir("Plots_AccConfigs"+architecture)
        
        # FILTERING
        configResults_copy_SD_ConfigAcceptable = configResults_copy[(configResults_copy["ID_SD"] == 0) & (configResults_copy["ConfigKey"] == "Acceptable")]

        # PLOTTING
        for param_name in parameters_dict.keys():
            splitted_param_name = param_name.split("_")
            
            if splitted_param_name[len(splitted_param_name)-1] == "ratio":
                myplt.one_plot(param_name, "fitFunc", configResults_copy_SD_ConfigAcceptable, "fitFunc_vs_"+param_name, "fitFunc_vs_"+param_name)
                
            else:  
                for param in parameters_dict[param_name]:  
                    # A este nivel, se podría intentar componer un panel único con todos los parámetros en cada elemento del diccionario
                    # e.g. inputParameters:sucr_upt,frc_upt,nh4_Ec,nh4_KT,endCycle
                    myplt.one_plot(param, "fitFunc", configResults_copy_SD_ConfigAcceptable, "fitFunc_vs_"+param, "fitFunc_vs_"+param)


# BACK TO THE ORIGINAL DIRECTORY
os.chdir(scripts_path)

















