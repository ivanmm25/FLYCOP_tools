#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Wed Feb 17 00:06:44 2021

@author: Iván Martín Martín
"""

"""
DESCRIPTION

    Script for output analysis which extracts those configurations with excessive Standard Deviation [SD > 10% (avgfitness)], 
    but which do not raise a ZeroDivisionError --> "SDexcess_configs"
    
    'dataTable_Scenario0.txt' contains all configurations: 
        * right_configs: those with acceptable SD (SD < 10%)
        * SDexcess_configs: those with excessive SD (SD > 10%), in which we are here interested (current script)
        * ZeroDivisionError_configs: those which raise this type of error, which usually have an excessive SD 
        
    The current script aims at obtainig SDexcess_configs: SD > 10%, thus fitness = 0.
    
    
    'configurationsResults_Scenario0.txt' just contains:
        * right_configs 
        * SDexcess_configs
        
    So those configurations with fitness = 0 (coming from 'dataTable_Scenario0.txt') being in this file, would be SDexcess_configs.
    
    
EXPECTED INPUT

    'dataTable_Scenario0.txt'
    'configurationsResults_Scenario0.txt'
    
OUTPUT

    "nonFailConfig_SDexcess_analysis.csv"
    
NOTE THAT:
    
        This script is currently adapted to the consortium for naringenin production, E.coli-P.putidaKT (2 microbes).
        If you wanted to use it with a different consortium, please take into account the next adaptations:
            
            QUICK ADAPTATIONS. Recall: CHANGE 'variable'
                
                - variable 'path'
                - variable 'file_header' (output.write())
                
                
            STRUCTURAL SCRIPT ADAPTATIONS. Recall: ADAPT parameters
                
                - information to be extracted from the corresponding dataTables
                    * dataTable_Scenario0.txt  -->  dataTable_params
                    * configurationsResults_Scenario0.txt  -->  configResults_colums
                    
                - further parameters to be calculated if desired (i.e. ratios)
"""

# import re
import os.path
import pandas as pd
path = "../../Project3_EcPp2_LimNut_M9/NP_LimNutFinal_29Mar/NP2"  # CHANGE PATH
os.chdir(path)

count_SDconfigs = 0  # Count of configurations with final fitness 0, because of excessive SD


# -----------------------------------------------------------------------------
# Configurations at 'configurationsResults_Scenario0.txt'
# -----------------------------------------------------------------------------
configResults = pd.read_csv("configurationsResults_Scenario0.txt", sep="\t", header="infer")


# -----------------------------------------------------------------------------
# Configurations with fitness = 0 from 'dataTable_Scenario0.txt'
# -----------------------------------------------------------------------------

# A new file is created with the information for those configurations
output = open("nonFailConfig_SDexcess_analysis.txt", "w")
output.write("Configuration\tsucr_frc\tinitEc_KT\tfitness\tsd\tpCA_mM\tFinalEc_gL\tNar_mM\tFinalKT_gL\n")  # CHANGE file header


# DataTable
# ---------
dataTable = pd.read_csv("dataTable_Scenario0.txt", sep="\t", header="infer")
filtered_dataTable = dataTable[dataTable['fitFunc'] == 0]

dataTable_params = ["sucr1", "Ecbiomass", "frc2", "KTbiomass"]  # ADAPT parameters
configResults_colums = ["fitFunc", "sd", "pCA_mM", "FinalEc_gL", "Nar_mM", "FinalKT_gL"]  # ADAPT parameters

for row in filtered_dataTable.itertuples():  # ADAPT code_chunk
        sucr = float(filtered_dataTable.loc[row[0], dataTable_params[0]])  # 'float' so that number is type float, necessary in later comparison
        EcBiomass = filtered_dataTable.loc[row[0], dataTable_params[1]]
        frc = float(filtered_dataTable.loc[row[0], dataTable_params[2]])
        KTbiomass = filtered_dataTable.loc[row[0], dataTable_params[3]]
        config = str(sucr)+","+str(EcBiomass)+","+str(frc)+","+str(KTbiomass)
        # print(config)
        
        
        # When a 'fitness = 0' configuration is not present in 'configurationsResults_Scenario0.txt', 
        # it means it constitutes a ZeroDivisionError
        
        for row in configResults.itertuples():
            if config == row[2]:
                count_SDconfigs +=1
                
                # Ratios of interest
                sucr_frc = round(sucr/frc, 3)
                initBiomass = round(EcBiomass/KTbiomass, 3)
                fitness = round(configResults.loc[row[0], configResults_colums[0]], 3)
                SD = round(configResults.loc[row[0], configResults_colums[1]], 3)
                
                pCA = round(configResults.loc[row[0], configResults_colums[2]], 3)
                finalEc = round(configResults.loc[row[0], configResults_colums[3]], 3)
                Nar = round(configResults.loc[row[0], configResults_colums[4]], 3)
                finalKT = round(configResults.loc[row[0], configResults_colums[5]], 3)
                
                output.write(config+"\t"+sucr_frc+"\t"+initBiomass+"\t"+str(fitness)+"\t"+str(SD)+"\t"+pCA+"\t"+finalEc+"\t"+Nar+"\t"+finalKT+"\n")



print("Total of SDexcess_configs (ZeroDivisionError not included): ", count_SDconfigs)
print("Total of right_configs: ", len(configResults) - count_SDconfigs)
print(len(configResults))
output.close()

# -----------------------------------------------------------------------------
# New dataframe 'nonFailConfig_SDexcess_analysis.txt' to EXCEL
# -----------------------------------------------------------------------------
configResults_excessSD = pd.read_csv("nonFailConfig_SDexcess_analysis.txt", sep="\t", header = 0)
configResults_excessSD.to_excel("nonFailConfig_SDexcess_analysis.xlsx", sheet_name="SDexcess_configs", header=True, index=False, index_label=None)
os.remove("nonFailConfig_SDexcess_analysis.txt")






