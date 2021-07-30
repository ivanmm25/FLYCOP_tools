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


Series of utilities for fitness rank analysis (see full description in each of them)
    

    build_fitness_ranks
    -------------------
    AUTOMATICALLY BUILD FITNESS RANKS, given: i) the total number of configurations
    available; ii) the number of desired fitness ranks.


    fitness_ranks_by_user
    ---------------------
    BUILD FITNESS RANKS, as established by the user in an external file.
    
        * fitness_ranks_user.txt
        ----------------------------------------------------------------------
          - NO blank spaces, comma as separator character except for the colon
          - Single line file in dictionary format
          - KEY: 'fitness_ranks'. VALUE: string of numbers (rank limits)
          
        EXAMPLE: fitness_ranks:100,75,50,25


    organize_colorize_fitness_ranks
    -------------------------------
    COLORIZE THE COLUMN ON 'fitness' in the EXCELFILE according to the designed
    fitness ranks.

    
    multiple_excel_unifier
    ----------------------
    ExcelFile Unifier: in case of different ExcelFiles to be unified in a single
    workbook, as different worksheets. INCONVENIENCE: the original format of 
    each individual ExcelFile is NOT maintained.

    
TO-DO
-----
    

    
"""


# import re
import sys
import pandas as pd
import xlsxwriter
import os.path
import subprocess
import openpyxl
scripts_path = os.getcwd()

sys.path.append("../Utilities")
# import Plotting as myplt



# -----------------------------------------------------------------------------
# UTILITY FOR AUTOMATICALLY BUILDING FITNESS RANKS (1a)
# -----------------------------------------------------------------------------

# Returns a list of fitness rank limits, from higher to lower limits 

# Median used as increase step in the building of intevals, instead of the mean
# REASON: the set of fitness values are not expected to be uniformly distributed,
# and they might be (partially) dominated by outliers

# KEYWORD ARGUMENTS:
        # n_ranks: integer. Number of desired fitness ranks in the pd_dataframe
        # n_configurations: integer. Number of configurations in the pd_dataframe
        # min_fitness, integer or float. Minimum value of fitness (deafult, 0)

# NOTE THAT 'n_configs_per_rank' is an integer that determines the number of 
# configurations per fitness rank. However, in those cases of non-integer divisions,
# the excess of configurations ends up: i) in the lowest rank; ii) in those ranks
# where there are several configurations with the same fitness value


def build_fitness_ranks(pd_dataframe, n_ranks = 5, n_configurations = 100, min_fitness = 0):
    
        # Slightly bigger than the maximum value found (10%)
        max_fitness = max(pd_dataframe["fitFunc"]) + (0.1) * max(pd_dataframe["fitFunc"]) 
        
        # 0 as the minimum value, default parameter
        # min_fitness = min(pd_dataframe["fitFunc"])  # A different alternative
        
         # List of intervals (fitness ranks)
        interval_limits = [max_fitness]
        
        n_configs_per_rank = n_configurations // n_ranks
        # print("Number of configurations per rank: ", n_configs_per_rank)
        current_position = max_fitness
        new_interval_limit = max_fitness
        
        
        for i_rank in range(n_ranks-1):
            # print("New rank: ", i_rank+1)
            n_configs_in_new_rank = 0
            
                
            for row in pd_dataframe.itertuples():
                fitFunc_value = pd_dataframe.loc[row[0], "fitFunc"]
                # print("Type of fitFunc_value: ", type(fitFunc_value))
                if fitFunc_value >= new_interval_limit: continue  # Avoid those configurations already classified in a fitness rank
                        
                current_position = fitFunc_value 
                n_configs_in_new_rank += 1
                
                if n_configs_in_new_rank >= n_configs_per_rank: break
                    
            # print("Final n_configs in current fitness rank: ", n_configs_in_new_rank)
            # print()
            new_interval_limit = current_position
            interval_limits.append(new_interval_limit)
        
        
        interval_limits.append(min_fitness)
        # print("New rank: ", n_ranks)
        # print("Current list of limits: ", interval_limits)
        
        return interval_limits

# -----------------------------------------------------------------------------        



# -----------------------------------------------------------------------------
# UTILITY FOR BUILDING FITNESS RANKS ACCORDING TO USER DESIGNATION (1b)
# -----------------------------------------------------------------------------

# Returns a list of fitness rank limits, from higher to lower limits 

# KEYWORD ARGUMENTS;
    # fitness_ranks_user: string. Name of the file where the fitness ranks are specified.


def fitness_ranks_by_user(fitness_ranks_user):
    
    with open(fitness_ranks_user, "r") as fitRank_file:
        lines = fitRank_file.readlines()
        for line in lines:
            
            if len(line) > 1 and line[0] != "#":  # Avoid header or empty lines
                line = line.strip("\n").split(":")
                
                if line[0] == "fitness_ranks": 
                    interval_limits_str = line[1].split(",")  # List of interval limits
                else: 
                    print("Please, correctly specify the 'fitness_ranks_user.txt' file, according to the docstring instructions")
                    interval_limits_str = []
                    break
    
    # Transform each interval limit (string) in integer or float
    interval_limits = []
    for interval_limit in interval_limits_str:
        interval_limits.append(eval(interval_limit))
        
    return interval_limits

# -----------------------------------------------------------------------------        



# -----------------------------------------------------------------------------
# UTILITY FOR COLORIZING THE COLUMN ON 'fitness' in the EXCELFILE, 
# according to the designed fitness ranks
# -----------------------------------------------------------------------------

# PAINT 'fitFunc' COLUMN CONSIDERING THE FITNESS RANK LIMITS
# REF: https://xlsxwriter.readthedocs.io/working_with_conditional_formats.html
# Section: type: cell, between. Also see section on format: for colours
    

# This utility is designed to be used for a given consortium architecture, in an
# ExcelFile with one or more potential architectures.

# KEYWORD ARGUMENTS:
        # n_ranks: integer. Number of desired fitness ranks in the pd_dataframe
        # n_configurations: integer. Number of configurations in the pd_dataframe
        # fitness_rank_limits: list of fitness rank limits.
        # new_older: string. Folder where the individual ExcelFiles by consortium architecture 
            # are stored, for organizational purposes.
            
# THIS FUNCTION ALSO RETURNS the new_folder where the individual (colorized) ExcelFiles are stored
        
# TO-DO: function on unifying the different ExcelFiles generated by this function.
    
    
def organize_colorize_fitness_ranks(pd_dataframe, cons_architecture, n_ranks, n_configurations, fitness_rank_limits, new_folder="ExcelFiles_colorized_fitRanks"):
    
    # IDENTIFY COLUMN LETTER IN THE EXCEL FILE
    # ----------------------------------------
    # Retrieve column names in the Dataframe as indexes
    column_names = pd.Index(list(pd_dataframe))
    # Locate index_number for the desired column ('fitFunc')
    excel_index = column_names.get_loc('fitFunc')
    # Transform the index_number into the corresponding letter in the ExcelFile
    excel_letter = xlsxwriter.utility.xl_col_to_name(excel_index)

    # CREATE NEW EXCEL FILE
    # ---------------------
    # Create a Pandas Excel writer using XlsxWriter as the engine
    modified_configResults = pd.ExcelWriter(f'configurationResults-consArchitecture-modified-{cons_architecture}.xlsx', engine='xlsxwriter')
    # Convert the dataframe to an XlsxWriter Excel object
    pd_dataframe.to_excel(modified_configResults, sheet_name=cons_architecture, index=False, engine = 'xlsxwriter')
    # Get the xlsxwriter workbook and worksheet objects
    modified_configResults_workbook  = modified_configResults.book  # WORKBOOK (ExcelFile)
    modified_configResults_worksheet = modified_configResults.sheets[cons_architecture]  # WORKSHEET
    
    
    # SOFT COLOURS SELECTED (yellow, red) for condittuional formatting
    # ---------------------
    light_red = modified_configResults_workbook.add_format({'bg_color': '#FFC7CE'})  # Light red fill
    light_yellow = modified_configResults_workbook.add_format({'bg_color': '#FFEB9C'})  # Light yellow fill
    given_format = [light_red, light_yellow]
    last_colour = 0
    
    # FITNESS RANKS - condittional formatting
    # -------------
    for i in range(n_ranks):
        lower_limit = fitness_rank_limits[i+1]
        # print("Type of lower lim: ", type(lower_limit))
        upper_limit = fitness_rank_limits[i]
    
        # ADD COLOURS
        # -----------
        modified_configResults_worksheet.conditional_format(f'{excel_letter}2:{excel_letter}{n_configurations + 1}', 
                                                            {'type':'cell',
                                                             'criteria': 'between',
                                                             'minimum':  lower_limit,
                                                             'maximum':  upper_limit,
                                                             'format': given_format[last_colour]})
        
        last_colour = 1 if last_colour == 0 else 0  # Alternate between light red and light yellow in the 'fitFunc' column painting
    
    # Close the Pandas Excel writer and output the Excel file
    if not os.path.isdir(new_folder):
        os.mkdir(new_folder)  # Create a new directory for the individual ExcelFiles (by consortium architecture)
        
    os.chdir(new_folder)
    modified_configResults.save()
    os.chdir("..")
    
    return new_folder
    
# -----------------------------------------------------------------------------
    


# -----------------------------------------------------------------------------
# UTILITY FOR UNIFYING THE DIFFERENT CONFIGURATION RESULTS TABLE IN A SINGLE FILE (xlsx)
# Each architecture is contained within a different worksheet
# -----------------------------------------------------------------------------

def multiple_excel_unifier(base_filename):

    # Find all potential configurationsResults files for the different consortium architectures
    find_process = subprocess.run([f"find . -name '{base_filename}*.xlsx'"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = True, universal_newlines=True)
    configTables_by_architecture = find_process.stdout.strip("\n").split("\n")
    
    
    cons_architectures = []
    for file in configTables_by_architecture:
        name_by_sections = file.strip(".").replace('.', '-').split("-")
        
        if len(name_by_sections) > 4:
            architecture = name_by_sections[3]
        else: continue
    
        cons_architectures.append(architecture)
    # print(cons_architectures)
    
    # Final Excel file
    configResults_excel = f"{base_filename}".replace('-', '_')+"_modified.xlsx"
    configTable = openpyxl.Workbook(configResults_excel)
    configTable.save(filename=configResults_excel)
    
    with pd.ExcelWriter(configResults_excel, mode='a', engine="openpyxl") as writer:
        for i_arch in range(0, len(cons_architectures)):
            locals()[cons_architectures[i_arch]] = pd.read_excel(configTables_by_architecture[i_arch], sheet_name=cons_architectures[i_arch], engine="openpyxl")
            # Each consortium architecture is a different sheet in the Excel file
            locals()[cons_architectures[i_arch]].to_excel(writer, sheet_name=cons_architectures[i_arch], header=True, index=False, index_label=None)
    
    configTable.close()
    
    # Remove individual ExcelFiles
    for individual_excelfile in configTables_by_architecture:
        # print(individual_excelfile)
        os.remove(individual_excelfile)

# -----------------------------------------------------------------------------



# -----------------------------------------------------------------------------
# UTILITY FOR CATEGORICAL PLOTTING OF FITNESS RANK COMPARISON
# -----------------------------------------------------------------------------
# The ranks are defined based on the desired 'ref_column' in the given dataframe
# DEFAULT: 'fitFunc'

# x-axis is represented by the fitness interval itself (string type)

def plotting_categorical_fitnessRanks(dataframe, fitness_rank_limits, plot_column = 'fitRank', ref_column = 'fitFunc'):
    
    # Number of float numbers
    # -----------------------
    float_numbers = str(fitness_rank_limits[len(fitness_rank_limits)-1])[::-1].find('.')
    if float_numbers > 3:
        float_round = 3
    else:
        float_round = 2
    
    # Building of a new series for categorical plotting
    # -------------------------------------------------
    dataframe[plot_column] = 0
    
    for row in dataframe.itertuples():  # row[0] = Index Number
        ref_variable = dataframe.loc[row[0], ref_column]
        
        for i in range(1, len(fitness_rank_limits)):
            rank_tuple = str(round(fitness_rank_limits[i-1], float_round))+"-"+str(round(fitness_rank_limits[i], float_round))
                
            # Note that the fitness interval limits are ordered from the highest to the lowest
            if fitness_rank_limits[i-1] <= ref_variable < fitness_rank_limits[i]:
                dataframe.loc[row[0], plot_column] = rank_tuple
                break
    
    # print(dataframe[[plot_column, ref_column]])
    return dataframe
# -----------------------------------------------------------------------------


# DIFFERENT ALTERNATIVE: FR1, FR2, etc. instead of using the proper fitness interval
    # as x-axis ticks

def plotting_categorical_fitnessRanks_by_keywords(dataframe, fitness_rank_limits, plot_column = 'fitRank', ref_column = 'fitFunc'):
    
    # Building of a new series for categorical plotting
    # -------------------------------------------------
    dataframe[plot_column] = 0
    
    for row in dataframe.itertuples():  # row[0] = Index Number
        ref_variable = dataframe.loc[row[0], ref_column]
        
        for i in range(1, len(fitness_rank_limits)):
            rank_tuple = "FR"+str(i)
                
            # Note that the fitness interval limits are ordered from the highest to the lowest
            if fitness_rank_limits[i-1] <= ref_variable < fitness_rank_limits[i]:
                dataframe.loc[row[0], plot_column] = rank_tuple
                break
    
    # print(dataframe[[plot_column, ref_column]])
    return dataframe
# -----------------------------------------------------------------------------












