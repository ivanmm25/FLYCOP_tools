#!/usr/bin/python3

############ FLYCOP ############
# Author: Beatriz García-Jiménez, Iván Martín Martín
# April 2018, April 2021
################################

"""
EcPp3_generalized - Glycosilation project. IndividualTest file using functions:

        - SelectConsortiumArchitecture(sucr1, frc2, nh4_Ec, nh4_KT, initial_biomass, consortium_arch, ...)

"""

print("\nInitialize individualTest execution\n")

import sys
sys.path.append('../../Scripts')
# import os
import EcPp3_generalized

# Number of args by command line
n_line_args = len(sys.argv)
sd_cutoff = 0.1


# STUDY PARAMETERS OPTIMIZED BY SMAC
# ------------------------------------------
# UPTAKE RATES
sucr1 = float(sys.argv[1])
frc2 = float(sys.argv[2])
nh4_Ec = float(sys.argv[3])
nh4_KT = float(sys.argv[4])

# CONSORTIUM ARCH AND SD_cutoff value
consortium_arch = sys.argv[5]
fitness = sys.argv[n_line_args-1]

# BIOMASSES
initial_biomass_str = sys.argv[6]
initial_biomass = [float(init_biomass) for init_biomass in initial_biomass_str.split()]

        
# RUN EXECUTION
avgfitness,sdfitness,strains_list=EcPp3_generalized.SelectConsortiumArchitecture(sucr1, frc2, nh4_Ec, nh4_KT, consortium_arch, initial_biomass, \
                                                                    fitObj='MaxNaringenin', maxCycles = 240, dirPlot='', repeat=5, sd_cutoff = sd_cutoff,
                                                                    models_summary=True)
    
print("\nComplete individualTest execution\n")

























