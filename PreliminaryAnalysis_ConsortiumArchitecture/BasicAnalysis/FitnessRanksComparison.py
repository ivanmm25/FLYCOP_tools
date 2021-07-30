#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun July 11 13:15:23 2020
@author: Iván Martín Martín

DESCRIPTION - BASIC ANALYSIS after a FLYCOP run
Pipeline of Selection of Consortium Architecture
------------------------------------------------
(A priori, this script has to be run by the user once the FLYCOP run has already finished)


Comparative Analysis for different fitness ranks within the same consortium architecture.
Comparison of different input and output parameters, according to the fitness ranks previously defined.

    1) Building of fitness intervals
    2) Plotting of parameters according to fitness ranks

(Utilities from 'FitnessRankAnalysis.py' are used here)

    
GENERAL USE
-----------

    * FILE LOCATION: The execution folder must be located accordingly to the Output Analysis utilities 
    (currently, in the 'OutputAnalysis' folder)
    
    * COMMAND LINE USE: how to run the script. 
    Example: python3 FitnessRanksAnalysis.py 38 5 ../../2_models_FVA_testing2 plotting_parameters_by_fitness.txt
    
    * No changes are needed in the current script, for the moment.


REQUIRED FILES
--------------

    * configurationResults_consArchitecture.xlsx
    
    * fitness_ranks_user.txt
    ----------------------------------------------------------------------
        - NO blank spaces, comma as separator character except for the colon
        - Single line file in dictionary format
        - KEY: 'fitness_ranks'. VALUE: string of numbers (rank limits)
          
        EXAMPLE: fitness_ranks:100,75,50,25
    
    * plotting_parameters_by_fitness.txt
    ----------------------------------------------------------------------
        - NO blank spaces, comma as separator character except for the colon
        - Header lines are not considered (those starting by '#'), they have just 
        organizational purposes
        - KEY: 'plotting_params'. VALUE: list of input and output parameters to be plotted
      
        EXAMPLE: plotting_params:global_final_biomass,MetNar_mM,Nar_mM,endCycle
      

SCRIPT DESIGN
-------------

    * PARSING PARAMETERS & REQUIRED FILES
    * FOR EVERY POTENTIAL ARCHITECTURE EVALUATED THROUGH FLYCOP (general script loop)
    (the script has to be run for every consortium architecture in the ExcelFile)
    
    1. BUILDING OF FITNESS RANKS
        - Automatic: build_fitness_ranks
        - Defined by user:fitness_ranks_by_user
    
    2. COLORIZING FITNESS COLUMN ACCORDING TO FITNESS RANKS: organize_colorize_fitness_ranks
    
    3. FITNESS RANK COMPARISON & PLOTTING
        
        - Retrieve plotting parameters
        - Categorical Organization of Fitness Ranks: plotting_categorical_fitnessRanks, plotting_categorical_fitnessRanks_by_keywords
        - Plotting: basic_boxplot_scatter
    
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
import xlsxwriter
import os.path
import subprocess
import openpyxl
import seaborn as sns
scripts_path = os.getcwd()

sys.path.append("../Utilities")
import Plotting as myplt
import FitnessRanksAnalysis as fitrank



# -----------------------------------------------------------------------------
# MAIN CODE
# =============================================================================
# PARSING PARAMETERS & REQUIRED FILES
# -----------------------------------------------------------------------------

# Reading the arguments given by command line
# Instead of command line args, these variables can be specified here as strings

n_configurations = sys.argv[1].split()  # e.g. '100' (configurations in a given FLYCOP execution)
n_ranks = sys.argv[2].split()  # e.g. '6' (fitness ranks into which divide the whole set of configurations)
folder_name = sys.argv[3]  # e.g. '../../OutputAnalysisFolder' (complete path)
plotting_parameters_by_fitness = sys.argv[4]  # e.g. 'plotting_parameters_by_fitness.txt'
# Command line use: python3 FitnessRanksAnalysis.py 38 5 ../../2_models_FVA_testing2/ plotting_parameters_by_fitness.txt 


# fitness_ranks_user = sys.argv[5]  # IN CASE OF USING 'fitness_ranks_by_user' FUNCTION
# Command line use: python3 FitnessRanksAnalysis.py 38 5 ../../2_models_FVA_testing2/ plotting_parameters_by_fitness.txt fitness_ranks_user.txt

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
        # -----------------------------
        configResults = pd.read_excel(xls, sheet_name=architecture, engine="openpyxl")


        # AUTOMATIC BUILDING OF FITNESS RANKS
        # -----------------------------------
        interval_limits = fitrank.build_fitness_ranks(configResults[configResults["ID_SD"] == 0], n_configurations = 38) 
        interval_limits = interval_limits[::-1]
        print("\nFitness interval list: ", interval_limits)
        
        
        # FITNESS RANKS ACCORDING TO USER DESIGNATION
        # -------------------------------------------
        # fitness_ranks_user = "fitness_ranks_user.txt"  # This argument can also be given by command line
        # interval_limits = fitness_ranks_by_user(fitness_ranks_user)
        # print("\nFitness interval list: ", interval_limits)


        # COLORIZING FITNESS COLUMN ACCORDING TO FITNESS RANKS
        # ----------------------------------------------------
        if interval_limits == []:
            print(f"Cannot organize fitness ranks by colour in the ExcelFile, if a proper interval-limits-list is not provided for the {architecture} architecture")
            print("The process continues with the next consortium architecture, if possible")
            continue
        else:
            ExcelFiles_new_folder = fitrank.organize_colorize_fitness_ranks(configResults[configResults["ID_SD"] == 0], cons_architecture = architecture, 
                                                                    n_ranks = 5, n_configurations=38,
                                                                    fitness_rank_limits = interval_limits)
        
        
        # ---------------------------------------------------------------------
        # FITNESS RANK COMPARISON & PLOTTING
        # ---------------------------------------------------------------------
        
        # Plotting parameters
        # -------------------
        parameters_list = []
        with open(plotting_parameters_by_fitness, "r") as plot_params:
            
            lines = plot_params.readlines()
            for line in lines:
                if len(line) > 1 and line[0] != "#":  # Avoid header or empty lines
                    line = line.strip("\n").split(":")
                    parameters_list = line[1].split(",")  # List of variable names
        
        print("\nPlotting parameters list: ", parameters_list)
        
        # Boxplot & Scatter Format
        # ---------------------------------------------------------------------
        sns.set_theme(style="darkgrid")
        sns.set_context('paper', font_scale=0.85, rc={'line.linewidth': 2.5, 
                        'font.sans-serif': [u'Times New Roman']})
        
        # Categorical Organization & Plotting of Fitness Ranks
        # ---------------------------------------------------------------------
        os.chdir(ExcelFiles_new_folder)
        
        # Original Dataframe for a given consortium architecture
        plotting_df = pd.read_excel(f'configurationResults-consArchitecture-modified-{architecture}.xlsx', sheet_name=architecture, engine="openpyxl")
        
        # Original Dataframe for a given consortium architecture, organized by a new colum ('fitRank', categorical classification according to fitness intervals)
        # OTHER CATEGORICAL CLASSIFICATION ALTERNATIVES: plotting_categorical_fitnessRanks_by_keywords
        fitRank_plotting_df = fitrank.plotting_categorical_fitnessRanks(plotting_df, interval_limits, plot_column = "fitRank", ref_column = 'fitFunc')
        
        os.chdir(output_path)
        
        # Plot Folder
        # ---------------------------------------------------------------------
        if not os.path.isdir(f"FitnessRankComparison_{architecture}"):
            os.mkdir(f"FitnessRankComparison_{architecture}")  # Create f"FitnessRankComparison_{architecture}" directory
        os.chdir(f"FitnessRankComparison_{architecture}")
        # ---------------------------------------------------------------------
        
        # -------------
        # Plotting Loop
        # -------------
        for parameter in parameters_list:
            # print(parameter)
            # print(fitRank_plotting_df[['fitRank', 'fitFunc']])
            myplt.basic_boxplot_scatter(fitRank_plotting_df, x_var = "fitRank", y_var = parameter, 
                                        x_label = "Fitness Ranks", y_label = parameter, 
                                        filename = f"{parameter}_boxplot_scatter", plot_title = f"{parameter}_boxplot_scatter",
                                        reverse_dataframe = True)
            
            # OTHER PLOTTING ALTERNATIVES: basic_boxplot
        
        
# BACK TO THE ORIGINAL DIRECTORY
os.chdir(scripts_path)


















