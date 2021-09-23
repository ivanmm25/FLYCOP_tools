#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 12:42:28 2021

@author: Iván Martín Martín
"""

"""
DESCRIPTION - MULTIPLE COMPARATIVE STATISTICAL ANALYSIS FOR FLYCOP RUNS

    FIRST PART OF THE SCRIPT
    ------------------------
    1. Set REFERENCE PATH to find the different FLYCOP runs to be considered.
    2. Each FLYCOP RUN to be included in the Comparative Analysis is accessed and pre-processed:
        - Only those configurations with acceptable SD are taken into account
        - Death tracking utility applied (when_death_starts)
    

    SECOND PART OF THE SCRIPT
    -------------------------
    1. Create comparison dataframe with all FLYCOP runs required. KEYS are the reference strings to differentiate between FLYCOP runs.
    2. Fill in the comparison dataframe with those variables to be later used in plotting.
    
    
    THIRD PART OF THE SCRIPT
    ------------------------
    1. Plotting.     
    2. Potential call to 'MultipleComparativeDatatable.py'.


    
EXPECTED INPUT

    'configurationsResults_Scenario0_analysis.xlsx' from "OutputParametersAnalysis.py" script 
        (OutputAnalysis) for all the FLYCOP runs to be considered in the Comparative Analysis

        
OUTPUT

    Folder: ./MultipleComparativeAnalysis_xxx
        (several plots)
    
NOTE THAT:
    
    The number of FLYCOP runs to be analyzed can be variable and should be extended if desired.
        Key operations to access a new FLYCOP run:
            - Access the dataframe ("configurationsResults_Scenario0_analysis.xlsx")
            - Acceptable SD configurations filter
            - Death tracking utility applied (when_death_starts)
            
            * INCLUDE NEW FLYCOP RUNS IN THE COMPARISON DATAFRAME: "configResults_dataframes"
            
        
    It is also important to CHANGE / ADAPT the columns (variables) that conform the comparison dataframe.
    At the same time, it is worth revisitiing the PLOTTING section to check variables, axes labels and titles.
        (CHANGE keyword)
    
"""

# ¿Merece la pena hacer una función de este script? ESTAMOS EN ELLO

# import re
import pandas as pd
import os.path

scripts_path = os.getcwd()
os.chdir("../Utilities")

from FitnessRanks import extract_ratios, when_death_starts
import Plotting as myplt

script_path = os.getcwd()
os.chdir(scripts_path)  # Creo que esto va a fallar, hace falta: os.chdir("../IndividualFLYCOPAnalysis")


# -----------------------------------------------------------------------------
# REFERENCE PATH
# -----------------------------------------------------------------------------

ref_path = "../Project3_EcPp2_LimNut_M9/Nitrogen"  # CHANGE path
os.chdir(ref_path)


# -----------------------------------------------------------------------------
# FIRST FLYCOP RUN TO CONSIDER
path1 = "./M9base"  # CHANGE path
os.chdir(path1)

configResults1 = pd.read_excel("configurationsResults_Scenario0_analysis_sub.xlsx", sheet_name="Product_ratios", engine="openpyxl")
configResults1_copy = configResults1.copy()

configResults1_copy = configResults1_copy[configResults1_copy["ID_SD"] != 1]  #  Only those values for configurations with an acceptable SD
configResults1_copy = when_death_starts(configResults1_copy)  # Initial death cycle tracking
os.chdir("..")


# -----------------------------------------------------------------------------
# SECOND FLYCOP RUN TO CONSIDER
path2 = "./M950N"  # CHANGE path
os.chdir(path2)

configResults2 = pd.read_excel("configurationsResults_Scenario0_analysis_sub.xlsx", sheet_name="Product_ratios", engine="openpyxl")
configResults2_copy = configResults2.copy()

configResults2_copy = configResults2_copy[configResults2_copy["ID_SD"] != 1]  #  Only those values for configurations with an acceptable SD
configResults2_copy = when_death_starts(configResults2_copy)   # Initial death cycle tracking
os.chdir("..")


# -----------------------------------------------------------------------------
# THIRD FLYCOP RUN TO CONSIDER
path3 = "./M9100N"  # CHANGE path
os.chdir(path3)

configResults3 = pd.read_excel("configurationsResults_Scenario0_analysis_sub.xlsx", sheet_name="Product_ratios", engine="openpyxl")
configResults3_copy = configResults3.copy()

configResults3_copy = configResults3_copy[configResults3_copy["ID_SD"] != 1]  #  Only those values for configurations with an acceptable SD
configResults3_copy = when_death_starts(configResults3_copy)   # Initial death cycle tracking
os.chdir("..")


# -----------------------------------------------------------------------------
# FOURTH FLYCOP RUN TO CONSIDER
path4 = "./M9200N"  # CHANGE path
os.chdir(path4)

configResults4 = pd.read_excel("configurationsResults_Scenario0_analysis_fitFunc.xlsx", sheet_name="Product_ratios", engine="openpyxl")
configResults4_copy = configResults4.copy()

configResults4_copy = configResults4_copy[configResults4_copy["ID_SD"] != 1]  #  Only those values for configurations with an acceptable SD
configResults4_copy = when_death_starts(configResults4_copy)   # Initial death cycle tracking
os.chdir("..")
# -----------------------------------------------------------------------------



# -----------------------------------------------------------------------------
# SINGLE FINAL DATAFRAME FOR ALL VARIABLES TO BE COMPARED
# -----------------------------------------------------------------------------
# SET OF DATAFRAMES: dictionary, note KEYS in this dictionary should be reference strings to differentiate between the FLYCOP RUNS here displayed
# KEYS would also be the classification variables for further CATEGORICAL PLOTTING

configResults_dataframes = {"18.7": configResults1_copy, "50": configResults2_copy, "100": configResults3_copy, "200": configResults4_copy}
# configResults_dataframes = {"nonSucr_lim": configResults2_copy, "nonSucr_nP_lim": configResults3_copy} # "200": configResults4_copy}
    
    
    
# -----------------------------------------------------------------------------
# MULTIPLE COMPARISON DATAFRAME
# -----------------------------------------------------------------------------

comparison_df = pd.DataFrame({})
comparison_df_rows = 0


# COLUMN VARIABLES IN THE DATAFRAME -- CHANGE VARIABLE NAMES if required

ratios = ["Uptake_ratio", "InitBiomass_ratio"]
finalProducts = ["pCA_mM", "Nar_mM"]
finalBiomass = ["FinalEc_gL", "FinalKT_gL"]
mediaNutrients = ["NH4_mM", "pi_mM", "FinalSucr"]
tracking = ["DT_cycles_init"]


# DATAFRAME ITERATION AND INFORMATION EXTRACTION

for key in configResults_dataframes: 
    for row in configResults_dataframes[key].itertuples():
        
        # LOCATE CELLS OF INTEREST
        # ------------------------
        uptake_ratio, initBiomass_ratio = extract_ratios(configResults_dataframes[key].loc[row[0], "configuration"])
        final_product1 = configResults_dataframes[key].loc[row[0], finalProducts[0]]
        final_product2 = configResults_dataframes[key].loc[row[0], finalProducts[1]]
        
        final_Ec = configResults_dataframes[key].loc[row[0], finalBiomass[0]]
        final_KT = configResults_dataframes[key].loc[row[0], finalBiomass[1]]
        
        media_nutrient1 = configResults_dataframes[key].loc[row[0], mediaNutrients[0]]
        media_nutrient2 = configResults_dataframes[key].loc[row[0], mediaNutrients[1]]
        
        # media_nutrient3 = configResults_dataframes[key].loc[row[0], mediaNutrients[2]]
        # DT_init = configResults_dataframes[key].loc[row[0], tracking[0]]
        
        
        # INCLUDE IN COMPARISON DATAFRAME
        # -------------------------------
        comparison_df.loc[comparison_df_rows, "Key"] = key
        comparison_df.loc[comparison_df_rows, ratios[0]] = uptake_ratio
        comparison_df.loc[comparison_df_rows, ratios[1]] = initBiomass_ratio
        
        comparison_df.loc[comparison_df_rows, finalProducts[0]] = final_product1
        comparison_df.loc[comparison_df_rows, finalProducts[1]] = final_product2
        
        comparison_df.loc[comparison_df_rows, finalBiomass[0]] = final_Ec
        comparison_df.loc[comparison_df_rows, finalBiomass[1]] = final_KT
        
        comparison_df.loc[comparison_df_rows, mediaNutrients[0]] = media_nutrient1
        comparison_df.loc[comparison_df_rows, mediaNutrients[1]] = media_nutrient2
        
        # comparison_df.loc[comparison_df_rows, mediaNutrients[2]] = media_nutrient3
        # comparison_df.loc[comparison_df_rows, tracking[0]] = DT_init
        comparison_df_rows += 1
        
    # print(comparison_df_rows)

# print(comparison_df)
# print(list(comparison_df.columns))


# FOLDER NAME: ADAPT IT SO NO PREVIOUS EXISTING FOLDER GETS OVERWRITTEN
# -----------------------------------------------------------------------------
if not os.path.isdir("MultipleComparativeAnalysis_baseOriginal_withM9200N"):
    os.mkdir("MultipleComparativeAnalysis_baseOriginal_withM9200N")  
os.chdir("MultipleComparativeAnalysis_baseOriginal_withM9200N")
# -----------------------------------------------------------------------------

# x_label única
x_label = "FLYCOP run"

# No sé si es práctica una lista de nombres para la etiqueta en eje y (como serie de parámetros para una potencial función, puede ser demasiado complicado)
y_labels = ["Uptake Rates ratio", "Initial Biomass ratio", "Final [pCA] (mM)", "Final [Nar] (mM)", 
            "Final E.coli (g/L)", "Final P.putida KT (g/L)", "Final [NH4] (mM)", "Final [Pi] (mM)"]

# Posiblemente los títulos serían muy similares a las etiquetas para el eje y
titles = []

# File Names
file_names = ["uptakeRratio", "initBratio", "finalpca", "finalnar", "finalEc_", "finalKT", "finalNH4", "finalpi", "finalsucr", "DT_cycles_init"]


myplt.basic_scatter(comparison_df, "Key", ratios[0], x_label, "Uptake Rates ratio", file_names[0]+"_multiplescatter", "Uptake Rates ratio")
myplt.basic_scatter(comparison_df, "Key", ratios[1], x_label, "Initial Biomass ratio", file_names[1]+"_multiplescatter", "Initial Biomass ratio")

myplt.basic_scatter(comparison_df, "Key", finalProducts[0], x_label, "Final [pCA] (mM)", file_names[2]+"_multiplescatter", "Final pCA")
myplt.basic_scatter(comparison_df, "Key", finalProducts[1], x_label, "Final [Nar] (mM)", file_names[3], "_multiplescatter", "Final Naringenin")

myplt.basic_scatter(comparison_df, "Key", finalBiomass[0], x_label, "Final E.coli (g/L)", file_names[4]+"_multiplescatter", "Final E.coli biomass")
myplt.basic_scatter(comparison_df, "Key", finalBiomass[1], x_label, "Final P.putida KT (g/L)", file_names[5]+"_multiplescatter", "Final P.putida KT biomass")

myplt.basic_scatter(comparison_df, "Key", mediaNutrients[0], x_label, "Final [NH4] (mM)", file_names[6]+"_multiplescatter", "Final NH4")
myplt.basic_scatter(comparison_df, "Key", mediaNutrients[1], x_label, "Final [Pi] (mM)", file_names[7]+"_multiplescatter", "Final Pi")
# myplt.basic_scatter_ylim(comparison_df, "Key", mediaNutrients[1], x_label, "Final [Pi] (mM)", 100, file_names[7]+"_multiplescatter_ylim100", "Final Pi")
# myplt.basic_scatter_ylim(comparison_df, "Key", mediaNutrients[1], x_label, "Final [Pi] (mM)", 0.2, file_names[7]+"_multiplescatter_ylim0.2", "Final Pi")
# myplt.basic_scatter_ylim(comparison_df, "Key", mediaNutrients[1], x_label, "Final [Pi] (mM)", 0.05, file_names[7]+"_multiplescatter_ylim0.05", "Final Pi")

# myplt.basic_scatter(comparison_df, "Key", mediaNutrients[2], x_label, "Final [Sucr] (mM)", file_names[8]+"_multiplescatter", "Final Sucrose")
# myplt.basic_scatter(comparison_df, "Key", "DT_cycles_init", x_label, "Initial Death Cycle", file_names[9]+"_multiplescatter", "Death Effect (initial cycle)")
os.chdir("..")



# -----------------------------------------------------------------------------
# CALL TO 'MultipleComparativeDatatable'
# -----------------------------------------------------------------------------

        






















































