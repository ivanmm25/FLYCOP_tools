#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Tue Feb 16 09:03:08 2021

@author: Iván Martín Martín
"""

"""
DESCRIPTION

    Script for output analysis which extracts the ERRORs selected from FLYCOP_config_V0_log.txt:
    Type of ERROR this script is suited for: ZeroDivisionError, exhaustion of one of the microbes in the media
    
    Currently adapted to: E.coli_iEC1364-P.putida_KT2440 naringenin production corsortium (2 microbes).
    Information extracted from ERRORs:
        
        * Final E.coli biomass
        * Final P.putida KT biomass
        * Final Naringenin concentration
        
        
EXPECTED INPUT

    'FLYCOP_config_V0_log.txt'
        
OUTPUT

    "FailConfigResults_analysis.txt"
    "FailConfigResults_dataTable.txt"
    
    
NOTE THAT:
    
        This script is specific to ZeroDivisionError (exhaustion of one of the microbes in the media).
        Moreover, it is currently adapted to the consortium for naringenin production, E.coli_iEC1364-P.putida_KT2440 (2 microbes).
        
        If you wanted to use it with a different consortium, please take into account the next adaptations:
        
            QUICK ADAPTATIONS. Recall: CHANGE 'variable'
                
                - variable 'path'
                - variable 'input_file'
                
                
            STRUCTURAL SCRIPT ADAPTATIONS. Recall: ADAPT line_code
                
                - configuration values to be extracted after 'ZeroDivisionError' (order and names are important)
                - config_extract in final DataTable - FailConfigResults_dataTable.txt
        
"""


import re
import os.path
# import pandas as pd
path = "../../Project3_EcPp2_LimNut_M9/NP_LimNutFinal_29Mar/NP3"  # CHANGE path
os.chdir(path)
count = 0  # Error count

# -----------------------------------------------------------------------------
# Original Analysis of 'FLYCOP_config_V0_log.txt'
# This is the logFile after FLYCOP run
# -----------------------------------------------------------------------------

output = open("FailConfigResults_analysis.txt", "w")
input_file = "FLYCOP_EcPp2_0_log.txt"  # CHANGE input_file

with open(input_file, "r") as file:  
    lines = file.readlines()
    last_line = ""
    for line in lines:
        if re.match("\[WARN \] \[PROCESS-ERR\]", line):
            if re.findall("ZeroDivisionError: float division by zero", line.strip("\n")):
                output.write("\n\nNEW ERROR\n-----------------------------------------------------------\n")
                output.write(last_line)
                output.write(line+"\n")
                count += 1
                
            last_line = line
                
                
        if re.match("\[ERROR\]", line):   
            if re.findall("The following algorithm call failed", line.strip("\n")):
                extract = re.findall("-p1_sucr1 '-[\d]+' -p2_biomassEc '0.[\d]+' -p3_frc2 '-[\d]+' -p4_biomassKT '0.[\d]+'", line)  # ADAPT line_code
                output.write("CONFIGURATION: "+str(extract[0])+"\n")
            else:
                output.write(line)
                
                
output.close()
if count == 0:  # NO errors found
    os.remove("FailConfigResults_analysis.txt")
print("\nNumber of fail configurations found: ", count)


# -----------------------------------------------------------------------------
# Associated Storing File (Table Format)
# POTENTIAL ADAPTATION NEEDED FOR header and variable_names for columns
# -----------------------------------------------------------------------------

output2 = open("FailConfigResults_dataTable.txt", "w")
output2.write("ERROR\tEx_Microbe\tConfig\tEc_finalB\tKT_finalB\tFinalNar")  # CHANGE header

# Column values   // CHANGE variables for columns
error = ""
microbe = ""
config = ""
nar_value = ""
Ec_value = ""
KT_value = ""

with open("FailConfigResults_analysis.txt", "r") as file:  
    lines = file.readlines()
    for line in lines:
        
        if re.match("\[WARN \] \[PROCESS-ERR\]", line):
            if re.findall("E.coli", line.strip("\n")):  # CHANGE microbe1
                microbe = "E.coli"
            elif re.findall("P.putida KT", line.strip("\n")):  # CHANGE microbe2
                microbe = "P.putida KT"
            
            if re.findall("ZeroDivisionError", line.strip("\n")):
                error = "ZeroDivisionError"
               
                
        if re.match("CONFIGURATION", line.strip("\n")):
                config_line = line.strip("\n")
            
                # Uptake rates + remove double quotes ("''")
                conc = re.findall("'-*[\d]+'", config_line)
                conc2 = []
                for i in range(len(conc)):
                    match = re.findall("-*[\d]+", conc[i])
                    number = float(match[0])
                    conc2.append(number)
                
                # Initial Biomass + remove double quotes ("''")
                biomass = re.findall("'0.[\d]+'", config_line)  # since initial biomass < 1.0, POTENTIAL CHANGE
                biomass2 = []
                for i in range(len(biomass)):
                    match = re.findall("0.[\d]+", biomass[i])
                    number = float(match[0])
                    biomass2.append(number)
                
                config = str(conc2[0])+","+str(biomass2[0])+","+str(conc2[1])+","+str(biomass2[1])  # ADAPT line_code
                # print(config)
                
        
        # Only saves the last values, for the following three variables; in each 'NEW ERROR' section of 'FailConfigResults_analysis.txt'
        # Nar, Ec_biomass, KT_biomass, POTENTIAL ADAPTATION OF CODE FOR THE STORING DATATABLE
        
        if re.match("\[ERROR\]", line):  
            
            if re.findall("Nar:", line.strip("\n")):
                nar_line = re.findall("Nar: [\d]+.[\d]+", line.strip("\n"))
                nar_value = re.findall("[\d]+.[\d]+", nar_line[0])  # 1 element list
                nar_value = nar_value[0]
                # print(nar_value)

            if re.findall("Final Ec biomass:", line.strip("\n")):
                Ec_line = re.findall("Final Ec biomass:[\s]+[\d]+.[\d]+", line.strip("\n"))
                Ec_value = re.findall("[\d]+.[\d]+", Ec_line[0])  # 1 element list
                Ec_value = Ec_value[0]
                # print(Ec_value)
        
            if re.findall("Final KT biomass:", line.strip("\n")):
                KT_line = re.findall("Final KT biomass:[\s]+[\d]+.[\d]+", line.strip("\n"))
                KT_value = re.findall("[\d]+.[\d]+", KT_line[0])  # 1 element list
                KT_value = KT_value[0]
                # print(KT_value)
        
        if re.match("NEW ERROR", line):
            output2.write(error+"\t"+microbe+"\t"+config+"\t"+Ec_value+"\t"+KT_value+"\t"+nar_value+"\n")


output2.write(error+"\t"+microbe+"\t"+config+"\t"+Ec_value+"\t"+KT_value+"\t"+nar_value+"\n")  # Final Recall
output2.close()










