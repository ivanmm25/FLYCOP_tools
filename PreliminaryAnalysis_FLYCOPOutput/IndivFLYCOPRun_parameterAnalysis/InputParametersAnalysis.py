#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Sun Dec 27 23:02:18 2020

@author: Iván Martín Martín
"""

"""
DESCRIPTION - INPUT PARAMETERS ANALYSIS

    Script for output analysis which calculates: 
        
        ratio of carbon substrate uptake rates (First microorganism / Second microorganism)
        ratio of initial biomass (First microorganism / Second microorganism)
        
    Moreover, the script generates the corresponding plots:
            ratio of substrate uptake rates (First microorganism / Second microorganism) vs. fitFunc
            ratio of initial biomass (First microorganism / Second microorganism) vs. fitFunc
            
        These plots are generated:
            (a) For all configurations (ZeroDivisionError, SD excessive - included) - Folder ./Plots
            (b) For those configurations that fulfil the SD restriction - Folder: ./Plots_no0fitness
            
    
    FIRST PART OF THE SCRIPT
    ------------------------
    The script distinguishes between those configurations with an acceptable standard deviation (SD) vs. 
        those with excessive SD or those with a ZeroDivisionError for microbes death or exhaustion.
        An acceptable SD value would mean SD < (0.10)*(fitness)
        
        
    SECOND PART OF THE SCRIPT
    -------------------------
    Computing ratios and further interesting parameters. This code chunks could be adapted to
    suit the purposes of the consortiums under analysis, i.e. in case of a different number of microbes.
    Currently:
        
        * Ratio of (sucrose consumption / fructose consumption)
        * Ratio of (initial E.coli biomass / initial P.putida KT biomass)
    
    
    THIRD PART OF THE SCRIPT
    ------------------------
    1. Obtaining the final dataframe and exporting it to EXCEL
    2. Generating a partial dataframe with just those configurations (and related information) with an acceptable SD
    3. Plotting. For further information about each plotting utility, see Plotting.py
    
    
EXPECTED INPUT

    'dataTable_Scenario0.txt' from ./xxx_FLYCOPdataAnalysis folder
    'configurationsResults_Scenario0.txt' from ./xxx_FLYCOPdataAnalysis folder
        
OUTPUT

    "dataTable_AcceptedRatios_SDlt.xlxs"
    
    Folder: ./Plots
        "AccRatios_UptakeR_base.png"
        "AccRatios_UptakeR1.png"
        "AccRatios_UptakeR2.png"
        
        "AccRatios_initBiomass_base.png"
        "AccRatios_initBiomass1.png"
        "AccRatios_initBiomass2.png"
        
    
    Folder: ./Plots_no0fitness
        "AccRatios_UptakeR_base_no0fitness.png"
        "AccRatios_UptakeR_no0fitness1.png"
        "AccRatios_UptakeR_no0fitness2.png"
        
        "AccRatios_initBiomass_base_no0fitness.png"
        "AccRatios_initBiomass_no0fitness1.png"
        "AccRatios_initBiomass_no0fitness2.png"
    
    
NOTE THAT:
    
    Code lines where a change might be eventually required are marked as CHANGE.
    
    This script is currently adapted to the consortium for naringenin production, E.coli_iEC1364-P.putida_KT2440 (2 microbes),
    where it calculates the ratio of carbon uptake rates between the two microbes and the ratio of initial biomass.
    
    Note that two different types of plots are obtained, given the script organization:
        
        - configurations in which fiFunc = 0, INCLUDED (SD excessive, ZeroDivisionError)
        - configurations in which fiFunc = 0, NOT INCLUDED (SD excessive, ZeroDivisionError)
        
        (Necessary adaptation in case of change: sections on "COMPUTE RATIOS" and "PLOTTING")
    
"""


# import re
import pandas as pd
import os.path

scripts_path = os.getcwd()
os.chdir("../Utilities")
import Plotting as myplt

os.chdir(scripts_path)
path = "../Project3_EcPp2_LimNut_M9/Nitrogen/M9200N"  # CHANGE path
os.chdir(path)


# -----------------------------------------------------------------------------
# ORIGINAL TABLE: dataTable_Scenario0.txt
# -----------------------------------------------------------------------------
dataTable = pd.read_csv("dataTable_Scenario0.txt", sep="\t", header="infer")
configResults = pd.read_csv("configurationsResults_Scenario0.txt", sep="\t", header="infer")
# print(dataTable)


# -----------------------------------------------------------------------------
# (1) CLASSIFY RECORDS DEPENDING ON SD: higher or lower than (0.1)*(fitFunc)
# (2) LOCATE RECORDS with fitness = 0.0 which constitute a ZeroDivisionError
# -----------------------------------------------------------------------------
dataTable["ID_SD"] = 0
dataTable["ZeroDivisionError"] = 0

for row_dataTable in dataTable.itertuples():
    if dataTable.loc[row_dataTable[0], "sd"] >= (0.1)*(dataTable.loc[row_dataTable[0], "fitFunc"]):  # (1)
        dataTable.loc[row_dataTable[0], "ID_SD"] = 1  
        
    if dataTable.loc[row_dataTable[0], "fitFunc"] == 0:  # (2)
        sucr = float(row_dataTable[1])  # 'float' to obtain a float number, not an int
        EcBiomass = row_dataTable[2]
        frc = float(row_dataTable[3])
        KTbiomass = row_dataTable[4]
        config = str(sucr)+","+str(EcBiomass)+","+str(frc)+","+str(KTbiomass)
        
        # When a 'fitness = 0' configuration is not present in 'configurationsResults_Scenario0.txt', 
        # it means it constitutes a ZeroDivisionError
        dataTable.loc[row_dataTable[0], "ZeroDivisionError"] = 1
        for row_cR in configResults.itertuples():  
            if config == row_cR[2]:
                dataTable.loc[row_dataTable[0], "ZeroDivisionError"] = 0
                break



# -----------------------------------------------------------------------------
# COMPUTE RATIOS
# Note that the names of metabolites for uptake rates and microbes names have to be CHANGED whenever necessary
# -----------------------------------------------------------------------------

# POTENTIAL CHANGE FOR NAMES if a different consortium is used
ratios = ["sucr1_frc2", "Ecbiomass_KTbiomass"]  # Names for new column_ratios to be calculated, in order
finalProducts = ["sucr1", "frc2"]  # Numerator, denominator (in that order) for the first of the ratios to be calculated (finalProducts)
finalBiomass = ["Ecbiomass", "KTbiomass"]  # Numerator, denominator (in that order) for the second of the ratios to be calculated (finalBiomass)


# Automatically detect column names
column_names = list(dataTable)


# UPTAKE RATES RATIO
ratiosDataframe = dataTable.copy()  # Avoid 'SettingWithCopyWarning'
try:
    ratiosDataframe[ratios[0]] = round((ratiosDataframe[finalProducts[0]] / ratiosDataframe[finalProducts[1]]), 4)
except ZeroDivisionError:
    ratiosDataframe[ratios[0]] = "NaN"

# BIOMASS RATIO
try:
    ratiosDataframe[ratios[1]] = round((ratiosDataframe[finalBiomass[0]] / ratiosDataframe[finalBiomass[1]]), 4)
except:
    ratiosDataframe[ratios[1]] = "NaN"
    


# -----------------------------------------------------------------------------
# FINAL DATAFRAME COPY with ratios to EXCEL
# -----------------------------------------------------------------------------
# Automatically detect column names
column_names = list(ratiosDataframe)
# print(column_names)
accepted_ratios_sorted_copy = ratiosDataframe.sort_values(by="fitFunc", ascending=False)  # CHANGE sorting_order if desired
accepted_ratios_sorted_copy.to_excel("dataTable_AcceptedRatios_SDlt.xlsx", sheet_name="Uptake_initBiomass_r", header=True, index=True, index_label=None)

# -----------------------------------------------------------------------------
# Subset of configurations where ID_SD == 0; i.e. not included SD excessive nor ZeroDivisionError configurations 
ratiosDataframe_no0fitness = ratiosDataframe[ratiosDataframe["ID_SD"] == 0]
# -----------------------------------------------------------------------------



# -----------------------------------------------------------------------------
# ASSOCIATED PLOTS with configurations in which fiFunc = 0, INCLUDED (SD excessive, ZeroDivisionError)
# -----------------------------------------------------------------------------
if not os.path.isdir("Plots"):
    os.mkdir("Plots")  # Create "Plots" directory
os.chdir("Plots")
# -----------------------------------------------------------------------------


title1 = "Uptake Rate"
png_name1 = "AccRatios_UptakeR_base"

title2 = "Initial Biomass"
png_name2 = "AccRatios_initBiomass_base"


myplt.one_plot("fitFunc", ratios[0], ratiosDataframe, png_name1+"1", title1)  # Initial reference for further axis limitation
myplt.two_subplots_subsetxlim("fitFunc", ratios[0], ratiosDataframe, 100, png_name1+"2", title1)
myplt.two_subplots_subset_x_lowerlim("fitFunc", ratios[0], ratiosDataframe, 100, png_name1+"3", title1)


myplt.one_plot("fitFunc", ratios[1], ratiosDataframe, png_name2+"1", title2)  # Initial reference for further axis limitation
myplt.two_subplots_subsetxlim("fitFunc", ratios[1], ratiosDataframe, 100, png_name2+"2", title2)
myplt.two_subplots_subset_x_lowerlim("fitFunc", ratios[1], ratiosDataframe, 100, png_name2+"3", title2)
os.chdir("..")


# -----------------------------------------------------------------------------
# ASSOCIATED PLOTS with configurations in which fiFunc = 0, NOT INCLUDED (SD excessive, ZeroDivisionError)
# -----------------------------------------------------------------------------
if not os.path.isdir("Plots_no0fitness"):
    os.mkdir("Plots_no0fitness")  # Create "Plots_no0fitness" directory
os.chdir("Plots_no0fitness")
# -----------------------------------------------------------------------------


title3 = "Uptake Rate"
png_name3 = "AccRatios_UptakeR_base_no0fitness"

title4 = "Initial Biomass"
png_name4 = "AccRatios_initBiomass_base_no0fitness"


myplt.one_plot("fitFunc", ratios[0], ratiosDataframe_no0fitness, png_name3+"1", title3)   # Initial reference for further axis limitation
myplt.two_subplots_subsetxlim("fitFunc", ratios[0], ratiosDataframe_no0fitness, 100, png_name3+"2", title3)
myplt.two_subplots_subset_x_lowerlim("fitFunc", ratios[0], ratiosDataframe_no0fitness, 100, png_name3+"3", title3)


myplt.one_plot("fitFunc", ratios[1], ratiosDataframe_no0fitness, png_name4+"1", title4)   # Initial reference for further axis limitation
myplt.two_subplots_subsetxlim("fitFunc", ratios[1], ratiosDataframe_no0fitness, 100, png_name4+"2", title4)
myplt.two_subplots_subset_x_lowerlim("fitFunc", ratios[1], ratiosDataframe_no0fitness, 100, png_name4+"3", title4)

os.chdir("..")
















