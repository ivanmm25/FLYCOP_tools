#!/usr/bin/python3

############ FLYCOP ############
# Author: Beatriz García-Jiménez, Iván Martín Martín
# April 2018, April 2021
################################

"""
EcPp3 - Glycosilation project. Preliminary Analysis of the configurationsResults.txt file:
    
    * configurationResults_consArchitecture.xlsx
    * nonOptimalConfigsasStringsX_models.txt
    * ErrorSummary_X_models.txt

"""


import re
import sys
import os.path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns
import subprocess
import openpyxl
# import shutil, errno
# import cobra
# import tabulate
# import getopt
# import copy
# import csv
# import math
# import cobra.flux_analysis.variability
# import massedit
# import statistics
# import importlib
# import optlang
# import spec


# PARSING PARAMETERS
# -----------------------------------------------------------------------------
# Reading the arguments given by command line
domainName = sys.argv[1]
id_number = sys.argv[2]
cons_architecture_series = sys.argv[3]  # '2_models 3_models'
# Interesante conocer el número de runs totales (configuraciones totales)
# -----------------------------------------------------------------------------



###############################################################################
# BLOCK 1: PRE-PROCESSING 'FLYCOP_config_V0_log'
# -----------------------------------------------------------------------------
# Original Analysis of 'FLYCOP_"+domainName+"_"+id_number+"_log.txt'
# This is the logFile after FLYCOP run
# -----------------------------------------------------------------------------

input_file = "FLYCOP_"+domainName+"_"+id_number+"_log.txt"
cons_architecture_list = cons_architecture_series.split()

# FOR EVERY POTENTIAL ARCHITECTURE EVALUATED THROUGH FLYCOP
for architecture in cons_architecture_list:
    
    # ERROR COUNT for every architecture
    ZeroDivisionError_count = 0  # Error count for ZeroDivisionError
    nonOptimalSolution_count = 0  # Error count for "model solution was not optimal"
    
    n_strains = architecture.split("_")[0]  # Number of strains in the consortium
    output1 = open("nonOptimalErrorConfigs_"+architecture+".txt", "w")  # in LogError directory
    
    with open(input_file, "r") as file:  
        lines = file.readlines()
        last_error = ""
        for line in lines:
            
            if re.match("\[WARN \] \[PROCESS-ERR\]", line):
                # ZeroDivisionError case
                if re.findall("ZeroDivisionError: float division by zero", line.strip("\n")):
                    last_error = "ZeroDivisionError"
                    
                # Non-optimal solution case
                elif re.findall("Exception: model solution was not optimal", line.strip("\n")):
                    last_error = "NonOptimal"
                    
                    
            elif re.match("\[ERROR\]", line) and last_error == "ZeroDivisionError":    
                
                if re.findall("The following algorithm call failed", line.strip("\n")) and re.findall("-p5_nmodels {0}_models".format(n_strains), line.strip("\n")):
                    ZeroDivisionError_count += 1
                    last_error = ""
                
            elif re.match("\[ERROR\]", line) and last_error == "NonOptimal":    
                
                if re.findall("The following algorithm call failed", line.strip("\n")) and re.findall("-p5_nmodels {0}_models".format(n_strains), line.strip("\n")):
                    nonOptimalSolution_count += 1
                    extract = re.findall("-p1_sucr1 '[-]*[0.|\d.]*[\d]+' -p2_frc2 '[-]*[0.|\d.]*[\d]+' -p3_nh4_Ec '[-]*[0.|\d.]*[\d]+' -p4_nh4_KT '[-]*[0.|\d.]*[\d]+' -p5_nmodels '{0}_models' [-p[\d]+_biomass_[\w]+ '[-]*[0.|\d.]*[\d]+']{1}".format(n_strains, n_strains), \
                                         line.strip("\n"))
                    output1.write(str(extract[0])+"\n")
                    last_error = ""
    
    output1.close()        
    
    
    # WRITE A BRIEF ERROR SUMMARY
    configs_summary = open("ErrorSummary_"+architecture+".txt", "w")  # in PreliminaryAnalysis directory   
    configs_summary.write("-------------------------------------------------------\n")
    configs_summary.write("ERROR SUMMARY\n")
    configs_summary.write("Consortium Architecture: {0}\n".format(architecture))
    configs_summary.write("-------------------------------------------------------\n")
    configs_summary.write("Number of ZeroDivisionError configurations found: "+str(ZeroDivisionError_count)+"\n")
    configs_summary.write("Number of nonOptimalSolution configurations found: "+str(nonOptimalSolution_count)+"\n")
    configs_summary.write("Total of ERROR configurations found: "+str(ZeroDivisionError_count + nonOptimalSolution_count)+"\n")
    configs_summary.close()



    # -----------------------------------------------------------------------------
    # Create a file with base configurations for non-optimal solutions (FLYCOP) for every architecture
    # Used in further comparison
    # -----------------------------------------------------------------------------
    
    output2 = open("nonOptimalConfigsasStrings"+architecture+".txt", "w")
    with open("nonOptimalErrorConfigs_"+architecture+".txt", "r") as file:  
        lines = file.readlines()
        for line in lines:
            config = ""
            params = re.findall("'[-]*[0.|\d.]*[\d]+'|'{n_strains}_models'", line)  # Dudas con esta expresión: ¿funciona?
    
            for parameter in params:
                if re.findall("'[-]*[0.|\d.]*[\d]+'", parameter) or re.findall("'{n_strains}_models'", parameter):
                    parameter = parameter.replace("\'", "")
                
                config += ","+str(parameter) if config else str(parameter)
            
            output2.write(config+"\n")
    
    output2.close()
    os.remove("nonOptimalErrorConfigs_"+architecture+".txt")
###############################################################################
###############################################################################



###############################################################################
###############################################################################
# BLOCK 2: Unify the different configurationsResults tables in a single file (xlsx)
# Each architecture is contained within a different worksheet
# -----------------------------------------------------------------------------

find_process = subprocess.run(["find . -name 'configurationsResults*.txt'"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = True, universal_newlines=True)
configTables_by_architecture = find_process.stdout.strip("\n").split("\n")


cons_architectures = []
for file in configTables_by_architecture:
    architecture = file.replace('.','-').split("-")[2]
    cons_architectures.append(architecture)


configResults_excel = "configurationResults_consArchitecture.xlsx"
configTable = openpyxl.Workbook(configResults_excel)
configTable.save(filename=configResults_excel)

with pd.ExcelWriter(configResults_excel, mode='a', engine="openpyxl") as writer:
    for i_arch in range(0, len(cons_architectures)):
        locals()[cons_architectures[i_arch]] = pd.read_csv(configTables_by_architecture[i_arch], sep="\t", header='infer')
        locals()[cons_architectures[i_arch]].to_excel(writer, sheet_name=cons_architectures[i_arch], header=True, index=False, index_label=None)

configTable.close()
###############################################################################

















