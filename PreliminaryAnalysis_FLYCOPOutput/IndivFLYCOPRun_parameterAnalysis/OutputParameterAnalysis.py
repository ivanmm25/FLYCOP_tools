#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 17 00:29:22 2021

@author: Iván Martín Martín
"""

"""
DESCRIPTION - OUTPUT PARAMETERS ANALYSIS

    Script for output analysis which calculates:
        
        ratio of metabolites, each produced by one of the two microbes in the corsortium (final product / intermediate product)
        ratio of final biomass (First microorganism / Second microorganism)
        
    Moreover, the script generates the corresponding plots of:
        
            ratio of metabolites vs. fitFunc
            ratio of final biomass (First microorganism / Second microorganism) vs. fitFunc
            
            final concentration of intermediate product vs. fitFunc
            final concentration of final product vs. fitFunc
        
            Limiting nutrient final concentration. vs. fitFunc 
            (where final conc != 0 mM, to easily find the fitness value for these particular cases)
            [IF THE CURRENT SIMULATION DOES NOT HAVE ANY LIMITING NUTRIENTS, THESE CODE LINES CAN BE OMITTED]
            
            TO-DO: add when_dead_starts() functionality
        
        These plots are generated:
            (a) For all configurations (SD excessive - included) - Folder ./Plots
            (b) For those configurations that fulfil the SD restriction - Folder: ./Plots_no0fitness
            
            (Note that configurations of 'ZeroDivisionError' cannot be considered here since 
             they are not included in the reference file 'configurationsResults_Scenario0.txt')

            
UTILITIES THAT MIGHT BE USED IN THIS SCRIPT:  
    
        (a) Remove duplicate headers in the 'configurationsResults_Scenario0.txt' file (header row with column names)
        (b) Changing separator character (more than 1 '\t' for just 1 '\t') in 'configurationsResults_Scenario0.txt'
        
        
    FIRST PART OF THE SCRIPT
    ------------------------
    0. Previous adaptation of the script: remove duplicate headers, change separator character '\t'
    1. Read dataframe and obtain those configurations with an acceptable Standard Deviation (SD): SD < 10% (average_fitness)
    2. Obtain those columns of interest from the other FLYCOP dataframe ('dataTable_Scenario0.txt') to be transferred
        to the current dataframe under study ('configurationsResults_Scenario0.txt')
    3. Sort the dataframe by 'fitness' and 'SD_criterion' unless otherwise desired
        
    
    SECOND PART OF THE SCRIPT
    -------------------------
    Computing ratios and further interesting parameters. This code chunks could be adapted to
    suit the purposes of the consortiums under analysis, i.e. in case of 
    a different number of microbes or metabolites per microbe. Currently:
        
        * ratio of metabolites, each produced by one of the two microbes in the corsortium (final product / intermediate product)
        * ratio of final biomass (First microorganism / Second microorganism)
    
    
    THIRD PART OF THE SCRIPT
    ------------------------
    1. Obtain the final dataframe and export it to EXCEL
    2. Generate a partial dataframe with just those configurations (and related information) with an acceptable SD
    3. Plotting. For further information about each plotting utility, see Plotting.py
        
        
EXPECTED INPUT

    'dataTable_Scenario0.txt' from ./xxx_FLYCOPdataAnalysis folder
    'configurationsResults_Scenario0.txt' from ./xxx_FLYCOPdataAnalysis folder
    
OUTPUT

    "configurationsResults_Scenario0_analysis.xlxs"  
    
    Folder: ./Plots
        "configResults_NARpCAr_initBiomass_limNut.png"  (with axes adaptation)
        "configResults_products_fitness_limNut.png"
        "configResults_finalBiomass_limNut.png"
        "configResults_"+limNut_name+"_limNut.png"
    
    Folder: ./Plots_no0fitness
        "configResults_NARpCAr_initBiomass_limNut_no0fitness.png"  (with axes adaptation)
        "configResults_products_fitness_limNut_no0fitness.png"
        "configResults_finalBiomass_limNut_no0fitness.png"
        "configResults_"+limNut_name+"_limNut_no0fitness.png"
    
    
NOTE THAT:
    
    Code lines where a change might be eventually required are marked as CHANGE.
    
    This script is currently adapted to the consortium for naringenin production, E.coli-P.putidaKT (2 microbes),
    where it calculates the ratio of final products between the two microbes and the ratio of final biomass.
    
    Note that two different types of plots are obtained, given the script organization:
        
        - configurations in which fiFunc = 0, INCLUDED (SD excessive)
        - configurations in which fiFunc = 0, NOT INCLUDED (SD excessive)
        
        (Necessary adaptation in case of change: sections on "COMPUTE RATIOS" and "PLOTTING")
        
    
        
"""

import re
import pandas as pd
import os.path

scripts_path = os.getcwd()
os.chdir("../Utilities")
import Plotting as myplt

os.chdir(scripts_path)  # Creo que esto va a fallar, hace falta: os.chdir("../IndividualFLYCOPAnalysis")
path = "../../Project3_EcPp2_LimNut_M9/NP_LimNutFinal_29Mar/NP3"  # CHANGE path
os.chdir(path)

# -----------------------------------------------------------------------------
# UTILITY FOR ELIMINATING DUPLICATE (repeated) HEADERS
# INPUT: input_file, name_corrected_file
# -----------------------------------------------------------------------------
def duplicate_headers(input_file, name_corrected_file):
    output = open(name_corrected_file, "w")
    with open(input_file, "r") as file:
        lines = file.readlines()
        output.write(lines[0])
        
        for line in lines:
            line = line.strip("\n").split("\t")
            if line[0] != "Fitness_function":
                output.write(("\t").join(line)+"\n")
        
    output.close()
    os.remove(input_file)
    return output
        
# -----------------------------------------------------------------------------
# UTILITY FOR CHANGING SEPARATOR CHARACTER in input file: more than 2 '\t' to just one '\t'
# Potential optimization?
# INPUT: input_file, name for the corrected file
# -----------------------------------------------------------------------------
def change_sep_char(input_file, name_corrected_file):
    output = open(name_corrected_file, "w")
    with open(input_file, "r") as file:
        lines = file.readlines()
        
        for line in lines:
            line_copy = re.sub("[\t]{2,5}", "\t", line)
            output.write(line_copy)
            
    output.close()
    os.remove(input_file)
    return output
    

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# SCRIPT CODE
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
    

# ORIGINAL DATAFRAME & ADAPTATIONS
# =============================================================================

final_file = "configurationsResults_Scenario0.txt"  # CHANGE name
# corrected_name = "configurationsResults_Scenario0_corrected.txt"

# CHANGING SEPARATOR CHARACTER
# final_file = change_sep_char("configurationsResults_Scenario0.txt", corrected_name)

# REMOVE DUPLICATE HEADERS
# final_file = duplicate_headers("configurationsResults_Scenario0.txt", corrected_name)

# =============================================================================

# DATAFRAME
# ---------
configResults = pd.read_csv(final_file, sep="\t", header="infer")
# print(configResults[configResults["fitFunc"] == 0])

    
# CLASSIFY RECORDS DEPENDING ON SD: higher or lower than (0.1)*(fitFunc)
# No 'ZeroDivisionError' in this script since these configurations are not included in 'configurationsResults_Scenario0.txt'
# ------------------------------------------
configResults["ID_SD"] = 0

for row in configResults.itertuples():   # row[0] = Index Number
        
    if configResults.loc[row[0], "sd"] >= (0.1)*(configResults.loc[row[0], "fitFunc"]):
        configResults.loc[row[0], "ID_SD"] = 1
    
    
# Automatically detect column names
column_names = list(configResults)
# print(column_names)
    
    
# INCLUDE THOSE DESIRED COLUMNS FROM THE OTHER DATATABLE OF INTEREST FOR THE FLYCOP RUN UNDER STUDY
# -------------------------------------------------------------------------
# dataTable_ratios = pd.read_excel("dataTable_AcceptedRatios_SDlt.xlsx", sheet_name="Uptake_initBiomass_r", engine="openpyxl")
# column_to_export = "column_to_export"
# configResults[column_to_export] = dataTable_ratios[column_to_export]
# -------------------------------------------------------------------------
    
    
# SORT BY ref_column: 'ID_SD', 'fitness' unless otherwise indicated 
# ----------------------
configResults = configResults.sort_values(by=['ID_SD', 'fitFunc'], ascending=[True, False])  # CHANGE sorting_order if desired
# print(configResults["fitFunc"])
    
    
    
# =============================================================================
# COMPUTE RATIOS
# Note that the names of metabolites for uptake rates and microbes names have to be CHANGED whenever necessary
# =============================================================================

# POTENTIAL CHANGE FOR NAMES if a different consortium is used
ratios = ["Nar_mM_pCA_mM", "FinalEc_gL_FinalKT_gL"]  # Names for new column_ratios to be calculated, in order
finalProducts = ["Nar_mM", "pCA_mM"]  # Numerator, denominator (in that order) for the first of the ratios to be calculated
finalBiomass = ["FinalEc_gL", "FinalKT_gL"]  # Numerator, denominator (in that order) for the second of the ratios to be calculated
    
# ratio NAR / pCA
configResults_copy = configResults.copy()  # Avoid 'SettingWithCopyWarning'
try:
    configResults_copy[ratios[0]] = round((configResults_copy[finalProducts[0]] / configResults_copy[finalProducts[1]]), 4)
except ZeroDivisionError:
    configResults_copy[ratios[0]] = "NaN"
        
# ratio finalEc / finalKT
try:
    configResults_copy[ratios[1]] = round((configResults_copy[finalBiomass[0]] / configResults_copy[finalBiomass[1]]), 4)
except ZeroDivisionError:
    configResults_copy[ratios[1]] = "NaN"
            

        
# =============================================================================
# FINAL DATAFRAME COPY with ratios to EXCEL
# =============================================================================
# Automatically detect column names
column_names = list(configResults_copy)
# print(column_names)


# DATAFRAME TO EXCEL: ordered by fitFunc (descending)
configResults_copy.to_excel("configurationsResults_Scenario0_analysis.xlsx", sheet_name="Product_ratios", header=True, index=True, index_label=None)


# SAME DATAFRAME TO EXCEL: ordered by naringenin production (descending)
# configResults_nar = configResults_copy.sort_values(by=['ID_SD', 'Nar_mM'], ascending=[True, False])
# configResults_nar.to_excel("configurationsResults_Scenario0_analysis_Nar.xlsx", sheet_name="Product_ratios", header=True, index=True, index_label=None)


# -----------------------------------------------------------------------------
# Subset of configurations where ID_SD == 0; i.e. not included SD excessive configurations 
configResults_copy_no0fitness = configResults_copy[configResults_copy["ID_SD"] == 0]
# -----------------------------------------------------------------------------



# =============================================================================
# ASSOCIATED PLOTS with configurations in which fiFunc = 0, INCLUDED (SD excessive)
# =============================================================================
if not os.path.isdir("Plots"):
    os.mkdir("Plots")  # Create "Plots" directory
os.chdir("Plots")
# -----------------------------------------------------------------------------

# ratios = ["Nar_mM_pCA_mM", "FinalEc_gL_FinalKT_gL"]  
title1 = "Input Parameter ratios"
png_name1 = "configResults_NARpCAr_finalBiomass_limNut"


# finalProducts = ["Nar_mM", "pCA_mM"]  
title2 = "Final Products"
png_name2 = "configResults_products_fitness_limNut"


# finalBiomass = ["FinalEc_gL", "FinalKT_gL"]
title3 = "Final Biomass"
png_name3 = "configResults_finalBiomass_limNut"


limNut_name = "NH4_mM"  # CHANGE limiting nutrient
title4 = "Limiting nutrient"
png_name4 = "configResults_"+limNut_name+"_limNut"


# Ratios vs. fitFunc
myplt.two_plots_twolabels("fitFunc", ratios[0], ratios[1], configResults_copy, png_name1+"1", title1)
myplt.two_plots_twolabels_xlim("fitFunc", ratios[0], ratios[1], configResults_copy, 100, png_name1+"2", title1)
myplt.two_plots_twolabels_x_lowerlim("fitFunc", ratios[0], ratios[1], configResults_copy, 100, png_name1+"3", title1)

# Final Products vs. fitFunc
myplt.two_plots_twolabels("fitFunc", finalProducts[0], finalProducts[1], configResults_copy, png_name2+"1", title2)
myplt.two_plots_twolabels_xlim("fitFunc", finalProducts[0], finalProducts[1], configResults_copy, 100, png_name2+"2", title2)
myplt.two_plots_twolabels_x_lowerlim("fitFunc", finalProducts[0], finalProducts[1], configResults_copy, 100, png_name2+"3", title2)

# Final Biomass vs. fitFunc
myplt.two_plots_twolabels("fitFunc", finalBiomass[0], finalBiomass[1], configResults_copy, png_name3+"1", title3)
myplt.two_plots_twolabels_xlim("fitFunc", finalBiomass[0], finalBiomass[1], configResults_copy, 100, png_name3+"2", title3)
myplt.two_plots_twolabels_x_lowerlim("fitFunc", finalBiomass[0], finalBiomass[1], configResults_copy, 100, png_name3+"3", title3)

# LimitNut vs. fitFunc, in those cases when LimitNut != 0 (at the end)
limNut_dataframe = configResults_copy[configResults_copy[limNut_name] != 0]  # Section of the dataframe
myplt.one_plot("fitFunc", limNut_name, limNut_dataframe, png_name4+"1", title4)
myplt.one_plot_xlim("fitFunc", limNut_name, limNut_dataframe, 100, png_name4+"2", title4)
myplt.one_plot_x_lowerlim("fitFunc", limNut_name, limNut_dataframe, 100, png_name4+"3", title4)

os.chdir("..")



# =============================================================================
# ASSOCIATED PLOTS with configurations in which fiFunc = 0, NOT INCLUDED (SD excessive)
# =============================================================================
if not os.path.isdir("Plots_no0fitness"):
    os.mkdir("Plots_no0fitness")  # Create "Plots_no0fitness" directory
os.chdir("Plots_no0fitness")
# -----------------------------------------------------------------------------
    
# ratios = ["Nar_mM_pCA_mM", "FinalEc_gL_FinalKT_gL"]  
title1 = "Output Parameter ratios"
png_name1 = "configResults_NARpCAr_finalBiomass_limNut_no0fitness"


# finalProducts = ["Nar_mM", "pCA_mM"]  
title2 = "Final Products"
png_name2 = "configResults_products_fitness_limNut_no0fitness"


# finalBiomass = ["FinalEc_gL", "FinalKT_gL"]
title3 = "Final Biomass"
png_name3 = "configResults_finalBiomass_limNut_no0fitness"


limNut_name = "NH4_mM"  # CHANGE limiting nutrient
title4 = "Limiting nutrient"
png_name4 = "configResults_"+limNut_name+"_limNut_no0fitness"


# Ratios vs. fitFunc
myplt.two_plots_twolabels("fitFunc", ratios[0], ratios[1], configResults_copy_no0fitness, png_name1+"1", title1)
myplt.two_plots_twolabels_xlim("fitFunc", ratios[0], ratios[1], configResults_copy_no0fitness, 100, png_name1+"2", title1)
myplt.two_plots_twolabels_x_lowerlim("fitFunc", ratios[0], ratios[1], configResults_copy_no0fitness, 100, png_name1+"3", title1)

# Final Products vs. fitFunc
myplt.two_plots_twolabels("fitFunc", finalProducts[0], finalProducts[1], configResults_copy_no0fitness, png_name2+"1", title2)
myplt.two_plots_twolabels_xlim("fitFunc", finalProducts[0], finalProducts[1], configResults_copy_no0fitness, 100, png_name2+"2", title2)
myplt.two_plots_twolabels_x_lowerlim("fitFunc", finalProducts[0], finalProducts[1], configResults_copy_no0fitness, 100, png_name2+"3", title2)

# Final Biomass vs. fitFunc
myplt.two_plots_twolabels("fitFunc", finalBiomass[0], finalBiomass[1], configResults_copy_no0fitness, png_name3+"1", title3)
myplt.two_plots_twolabels_xlim("fitFunc", finalBiomass[0], finalBiomass[1], configResults_copy_no0fitness, 100, png_name3+"2", title3)
myplt.two_plots_twolabels_x_lowerlim("fitFunc", finalBiomass[0], finalBiomass[1], configResults_copy_no0fitness, 100, png_name3+"3", title3)

# LimitNut vs. fitFunc, in those cases when LimitNut != 0 (at the end)
limNut_dataframe = configResults_copy_no0fitness[configResults_copy_no0fitness[limNut_name] != 0]  # Section of the dataframe
myplt.one_plot("fitFunc", limNut_name, limNut_dataframe, png_name4+"1", title4) 
myplt.one_plot_xlim("fitFunc", limNut_name, limNut_dataframe, 100, png_name4+"2", title4)
myplt.one_plot_x_lowerlim("fitFunc", limNut_name, limNut_dataframe, 100, png_name4+"3", title4)  

os.chdir("..")


# EN TEORÍA, ESTO ES INNECESARIO SI LUEGO HACEMOS LA TABLA DE CÁLCULO EN MULTIPLE COMPARATIVE ANALYSIS
# O BIEN SE PUEDE TRASLADAR UNA VERSIÓN SENCILLA DESDE ALLÍ
# =============================================================================
# ASSOCIATED PLOTS with configurations in which fiFunc = 0, NOT INCLUDED (SD excessive)
# =============================================================================

NH4_count = 0
dead_noSD = 0
globalcount = 0

for row in configResults_copy_no0fitness.itertuples():   # row[0] = Index Number
    globalcount += 1
    if configResults_copy_no0fitness.loc[row[0], "NH4_mM"] == 0:
        NH4_count += 1
    if configResults_copy_no0fitness.loc[row[0], "DeadTracking"] == 0:
        dead_noSD += 1

print("Number of configurations with acceptable SD and final [NH4+] (mM) = 0: ", NH4_count, "in", globalcount)
print("Number of configurations with acceptable SD and NO Dead Effect observed: ", dead_noSD, "in", globalcount)


dead_SD = 0
globalcount2 = 0

for row in configResults_copy.itertuples():   # row[0] = Index Number
    globalcount2 += 1
    if configResults_copy.loc[row[0], "DeadTracking"] == 0:
        dead_SD += 1

print("Number of configurations (excessive SD included) and NO Dead Effect observed: ", dead_SD, "in", globalcount2)






















