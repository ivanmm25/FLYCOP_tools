#!/usr/bin/python3

############ FLYCOP ############
# Author: Beatriz García-Jiménez, Iván Martín Martín
# April 2018, April 2021
################################

"""
WRAPPER FILE for individual execution of every configuration on a FLYCOP run.
Functions used in the current script:

        * SelectConsortiumArchitecture(**args) from EcPp3_generalized.py

NOTE THAT the argument 'initial_biomass' is composed as a series of initial biomass
values returned from SMAC, to be given to the last function as a list.
"""

# FOLDERS
template_folder='EcPp3_TemplateOptimizeConsortiumV0/Comets'  # Contents
testTemp='EcPp3_TestTempV0'  # Temporal folder
dirPlots='../smac-output/EcPp3_PlotsScenario0/'  

# OTHER VARIABLES
fitFunc = "MaxGerNar"
maxCycles = 240  # See layout_template
repeats = 5
sd_cutoff = 0.1

# import cobra
import sys
import shutil, errno
import os.path
# import pandas as pd
# import tabulate
# import re
# import getopt
# import copy
# import csv
# import math
# import cobra.flux_analysis.variability
# import massedit
# import subprocess
# import statistics
# import importlib
# import optlang
# import spec

# Load code of individual run
sys.path.append('../Scripts')
import EcPp3_generalized

# Number of args by command line
n_line_args = len(sys.argv)


# Parsing parameters
# Reading the first 5 arguments in SMAC
# -------------------------------------
instance = sys.argv[1]
specifics = sys.argv[2]
cutoff = int(float(sys.argv[3]) + 1)
runlength = int(sys.argv[4])
seed = int(sys.argv[5])


# BIOMASSES
# SMAC returns a certain number of initial biomass values, depending on the selected consortium configuration
# -----------------------------------------------------------------------------

initial_biomass = []  # List of biomass values for the strains in the current consortium architecture
append_biomass = False

for i_arg in range(6, n_line_args):
    if append_biomass:
        initial_biomass.append(sys.argv[i_arg])
        append_biomass = False
    
    arg = sys.argv[i_arg].split("_")
    if len(arg) > 1 and arg[1] == "biomass":
        append_biomass = True

print("Initial biomass: ", initial_biomass)

# REST OF STUDY PARAMETERS OPTIMIZED BY SMAC
# ------------------------------------------
# UPTAKE RATES
sucr1 = float(sys.argv[7])
frc2 = float(sys.argv[9])
nh4_Ec = float(sys.argv[11])
nh4_KT = float(sys.argv[13])

# FVA rates
FVApCA = float(sys.argv[15])
FVAfru = float(sys.argv[17])
FVAGerNar = float(sys.argv[19])
FVANar = float(sys.argv[21])

# CONSORTIUM ARCH
consortium_arch = sys.argv[23]


# CREATE A TEMP FOLDER TO OPERATE IN THE CURRENT ITERATION
# Move all files from template_folder to testTemp folder
# --------------------------------------------------------
# Copy the template directory
if (os.path.exists(testTemp)):
    shutil.rmtree(testTemp)  # Remove content (directory tree)
try:
    shutil.copytree(template_folder, testTemp)
    
# In case of exception
except OSError as exc: # python >2.5
    if exc.errno == errno.ENOTDIR:  # Not a directory
        shutil.copy(template_folder, testTemp)
    else: raise
    
os.chdir(testTemp)  

if not os.path.exists(dirPlots):
    os.makedirs(dirPlots)


# At a higher level: Running the wrapper-script in SMAC 
# -----------------------------------------------------------------------------
avgfitness,sdfitness,strains_list=EcPp3_generalized.SelectConsortiumArchitecture(sucr1, frc2, nh4_Ec, nh4_KT, FVApCA, FVAfru, FVAGerNar, FVANar,
                                                                                 consortium_arch, initial_biomass, \
                                                                                 fitFunc, maxCycles, dirPlots, repeats, sd_cutoff)  

# Print wrapper Output:
# -----------------------------------------------------------------------------
print("Wrapper Output")
print("--------------")
print('Result of algorithm run: SAT, 0, 0, '+str(1-avgfitness)+', 0, '+str(seed)+', '+str(sdfitness)) # fitness maximize
# print('Result of algorithm run: SAT, 0, 0, '+str(avgfitness)+', 0, '+str(seed)+', '+str(sdfitness)) # fitness minimize

# Remove the temporal dir for this run result
os.chdir('..')  # Back to MicrobialCommunities
shutil.rmtree(testTemp)















