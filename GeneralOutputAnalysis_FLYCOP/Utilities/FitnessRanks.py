#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 21 21:20:59 2021

@author: Iván Martín Martín
"""

"""
OUTPUT ANALYSIS AFTER FLYCOP (UTILITIES)
DESCRIPTION

    ORGANIZATION OF FITNESS RANKS & ASSOCIATED STATS DESCRIPTION
    Series of functions to define and process fitness ranks (utility for scripts related to Statistical Analysis).
    
        - obtain_fitness_rank
        - stats_description
        - describe_fitness_ranks: combination of the last two functions
        
        
    INDIVIDUAL COMPARATIVE ANALYSIS (FLYCOP run)
    Define fitness ranks for the Individual Comparative Analysis (FLYCOP run, input parameters)
    
        - organize_fitness_ranks
        
    
    EXTRACT INPUT PARAMETERS FOR A FLYCOP run (configuration) as a single str line
    
        - extract_ratios
        
        
    ANALYSIS OF BIOMASS LOSS
        
        - when_death_starts (when this effect is first registered in a given simulation)
    
    
EXPECTED INPUT

    - Dataframe: dataframe to be processed
    - rank_limits_set: tuple with a series of inner tuples (fitness rank intervals)
    - rank_limits: smaller tuple (fitness rank individual interval)
    
    - ref_colum: reference column to extract the fraction of the dataframe. Default :'fitness'
    - frac_dataframe: fraction of a particular dataframe
    - descr_columns: columns to be described with 'Pandas' statistical description (method .describe())
    
    - string_line_config. Example: -8.0,0.3,-12.0,0.05
    
        
OUTPUT

    See each particular function
    
NOTE THAT:
    
    Script in development (...)
    
"""

# import re
# import pandas as pd
# import os.path


# -----------------------------------------------------------------------------
# ORGANIZATION OF FITNESS RANKS & ASSOCIATED STATS DESCRIPTION
# -----------------------------------------------------------------------------

# RETURNS FRACTION OF INTEREST (fitness rank, all columns) OF THE DATAFRAME 
# For a fitness interval, retrieves all related information (rest of the parameters)

def obtain_fitness_rank(rank_limits, dataframe, ref_colum):
    frac_dataframe = dataframe[dataframe[ref_colum] < rank_limits[1]]  # Higher limit
    final_frac_dataframe = frac_dataframe[frac_dataframe[ref_colum] > rank_limits[0]]  # Lower limit
    return final_frac_dataframe
    

# STATISTICAL DESCRIPTION for the selected fitness rank, columns selected 
# descr_columns are those columns (parameters) for which the statistical description is required

def stats_description(frac_dataframe, descr_columns):
    stat_description = frac_dataframe[descr_columns].describe()
    return stat_description


# COMBINES THE TWO LAST FUNCTIONS
    # 1. Obtains every single fitness rank
    # 2. Makes the subsequent statistical description

def describe_fitness_ranks(rank_limits_set, dataframe, descr_columns, ref_column):
    
    # 'SAVE STATS' version, if wanted to be stored in a file
    """
    filename = "stats_description.txt"  # Which name?
    with open(filename, "w") as stats_file:
        for rank_limits_tuple in rank_limits_set:
            fitness_rank = obtain_fitness_rank(rank_limits_tuple, dataframe, ref_column)
            stat_descr = stats_description(fitness_rank, descr_columns)
            stats_file.write(stat_descr+"\n")
    """
        
    # 'PRINT' version
    for rank_limits_tuple in rank_limits_set:
        fitness_rank = obtain_fitness_rank(rank_limits_tuple, dataframe, ref_column)
        stat_descr = stats_description(fitness_rank, descr_columns)
        print(f"{ref_column} rank: {rank_limits_tuple[0]}-{rank_limits_tuple[1]}")   
        print(stat_descr)
        print()
    
    
# LIMITACIONES
# ------------
# Limitación: el primero de los rangos, hay que pasarle un límite superior más alto que el mejor de los fitness
# Limitación: ¿cómo haríamos cálculos individuales de un único parámetro estadístico? Véase mean(), median() (individualmente) 


# AUTOMATIZAR
# -------------------------------
# Set con tuplas para los rangos
# NUEVA IDEA: llevar análisis estadístico a archivo para posterior 'ComparativeAnalysis' entre configuraciones
    # Array 3D
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------



# -----------------------------------------------------------------------------
# INDIVIDUAL COMPARATIVE ANALYSIS (FLYCOP run)
# -----------------------------------------------------------------------------
# DEFINE FITNESS RANKS (new column 'FitRank') for the Individual Comparative Analysis within each FLYCOP run
# Utility required for further comparison of parameter ratios of each fitness rank in FLYCOP output tables

def organize_fitness_ranks(dataframe, rank_limits_set, ref_column):
    
    for row in dataframe.itertuples():  # row[0] = Index Number
        ref_variable = dataframe.loc[row[0], ref_column]
        
        for i in range(1, len(rank_limits_set)+1):
            rank_tuple = rank_limits_set[i-1]
                
            if rank_tuple[0] < ref_variable < rank_tuple[1]:
                dataframe.loc[row[0], "FitRank"] = int(i)
                break
                
            elif ref_variable == 0:
                ConfigError = dataframe.loc[row[0] , "ZeroDivisionError"]
                
                if ConfigError == 0:
                    dataframe.loc[row[0] , "FitRank"] = 0
                else:
                    dataframe.loc[row[0] , "FitRank"] = -1
    return dataframe
# -----------------------------------------------------------------------------



# -----------------------------------------------------------------------------
# INDIVIDUAL COMPARATIVE ANALYSIS (FLYCOP run)
# -----------------------------------------------------------------------------
# DEFINE RANKS (new column) for the Individual Comparative Analysis within each FLYCOP run
# The ranks are defined based on the desired 'ref_column' in the given dataframe

# 'New_column' contains the categorical classification of values, depending on the established ranks
# Instead of a number, the fitness interval itself

def organize_ranks(dataframe, rank_limits_set, ref_column, new_column):
    
    for row in dataframe.itertuples():  # row[0] = Index Number
        ref_variable = dataframe.loc[row[0], ref_column]
        
        for i in range(1, len(rank_limits_set)+1):
            rank_tuple = rank_limits_set[i-1]
                
            if rank_tuple[0] < ref_variable < rank_tuple[1]:
                dataframe.loc[row[0], new_column] = str(rank_tuple)
                break
                
    return dataframe
# -----------------------------------------------------------------------------



# -----------------------------------------------------------------------------
# EXTRACT RATIOS OF INPUT PARAMETERS FOR FLYCOP run (configuration) as a single str line
# -----------------------------------------------------------------------------
# Currently: specific to E.coli_iEC1364-P.putida_KT2440 configuration:
    # Sucrose/ fructose uptake rates ratio
    # E.coli/ P.putida KT initial biomass ratio
    
# EXAMPLE: -8.0,0.3,-12.0,0.05

def extract_ratios(string_line_config):
    list_line = string_line_config.split(",")
    
    sucr_ur = float(list_line[0])
    frc_ur = float(list_line[2])
    uptake_ratio = round(sucr_ur/frc_ur, 3)
    
    Ec_init = float(list_line[1])
    KT_init = float(list_line[3])
    initbiomass_ratio = round(Ec_init/KT_init, 3)
    
    return uptake_ratio, initbiomass_ratio
# -----------------------------------------------------------------------------



# -----------------------------------------------------------------------------
# EXTRACT RATIOS OF INPUT PARAMETERS FOR FLYCOP run (configuration) as a single str line
# -----------------------------------------------------------------------------
# Currently: specific to E.coli_iEC1364-P.putida_KT2440 configuration, with NP_uptake rates

    # Sucrose/ fructose uptake rates ratio
    # E.coli/ P.putida KT initial biomass ratio
    # NH4 uptake ratio (E.coli/P.putida)
    # Pi uptake ratio (E.coli/P.putida)
    
# EXAMPLE: -4.0,0.15,-18.0,0.05,-6.0,-10.0,-0.2,-0.25

def extract_ratios_NP(string_line_config):
    list_line = string_line_config.split(",")
    
    sucr_ur = float(list_line[0])
    frc_ur = float(list_line[2])
    uptake_ratio = round(sucr_ur/frc_ur, 3)
    
    Ec_init = float(list_line[1])
    KT_init = float(list_line[3])
    initbiomass_ratio = round(Ec_init/KT_init, 3)
    
    NH4_Ec = float(list_line[4])
    NH4_KT = float(list_line[5])
    NH4_Ec_KT = round(NH4_Ec/NH4_KT, 3)
    
    # Pi_Ec = float(list_line[6])
    # Pi_KT = float(list_line[7])
    # Pi_Ec_KT = round(Pi_Ec/Pi_KT, 3)
    
    return uptake_ratio, initbiomass_ratio, NH4_Ec_KT
# -----------------------------------------------------------------------------



# -----------------------------------------------------------------------------
# EXTRACT INPUT PARAMETERS FOR FLYCOP run (configuration) as a single str line
# -----------------------------------------------------------------------------
# Currently: specific to E.coli_iEC1364-P.putida_KT2440 configuration, with NP_uptake rates
# EXAMPLE: -4.0,0.15,-18.0,0.05,-6.0,-10.0,-0.2,-0.25

def extract_baseConfig_NP(string_line_config):
    list_line = string_line_config.split(",")
    
    sucr_ur = float(list_line[0])
    frc_ur = float(list_line[3])
    
    Ec_init = float(list_line[1])
    # Ec_init_glyc = float(list_line[2])
    KT_init = float(list_line[4])
    
    NH4_Ec = float(list_line[5])
    NH4_KT = float(list_line[6])
    
    # Pi_Ec = float(list_line[6])
    # Pi_KT = float(list_line[7])
    
    return sucr_ur, frc_ur, Ec_init, KT_init, NH4_Ec, NH4_KT
# -----------------------------------------------------------------------------



# -----------------------------------------------------------------------------
# FUNCTION TO: obtain the initial cycle for death effect, from the dataframe where it has previously registered

# INPUT: dataframe where to operate (pandas dataframe)
# OUTPUT: same dataframe with new column:
    # 'DT_cycles_init': cycle when dead effect starts

# NOTE THAT: "NoDeadTracking" means there is no death effect, thus the value for 'DT_cycles_init' is 0.
# If the mean for the death effect (initial cycle) was computed, all configurations would be taken into 
    # account (in the denominator) and those with no biomass loss would "sum 0" (to the numerator)
    
# TO-DO: further implementation / reorganization of code lines
# -----------------------------------------------------------------------------

def when_death_starts(dataframe):
    dataframe["DT_cycles_init"] = 0
    for row in dataframe.itertuples():
        DT_cycles = dataframe.loc[row[0], "DT_cycles"].split("-")
        DT_cycles_init = DT_cycles[0]
        
        if DT_cycles_init != "NoDeadTracking":
            dataframe.loc[row[0], "DT_cycles_init"] = int(DT_cycles_init)
            
    return dataframe
# -----------------------------------------------------------------------------
















