#!/usr/bin/python

# Author: Beatriz García-Jiménez, Iván Martín Martín
# April 2018, June 2021

###############################################################################
# SCRIPT DESCRIPTION   
###############################################################################
"""
PIPELINE DESIGNED FOR SELECTION OF THE BEST ARCHITECTURE FOR A GIVEN CONSORTIUM
-------------------------------------------------------------------------------

Script designed for adaptation of SMAC condictionals, depending on model architecture.

Conditionals:
    
    - The names of strains in the base file "SMAC_conditionals_arch.txt" and
    in the file "define_architecture" are NOT the same.
    
    - The enumeration of strains for every architecture (integer) in 
    "SMAC_conditionals_arch.txt" should always start by the 'common' strains to all
    architectures, for simplicity purposes
    
    - The enumeration of strains in the PCS file should be ordered in the same
    way as for the strains in every architecture in the "SMAC_conditionals_arch.txt"
    (specially for those common strains to all architectures).


###  FORMAT  ###
  
  SMAC_conditionals_arch.txt
  --------------------------
  FORMAT: integer:strain1,strain2,..., strain_n
      - NO blank spaces, comma as separator character except for the colon
      
  CONTENT - each line contains:
      - integer standing for the number of strains in each consortium architecture
      
      - Base name of strains in each consortium architeture
      
          * This name might not be equivalent to the name in 'define_architectures.txt' file.
          The only purpose of these names is to differentiate base strains for conditionals in the PCS 
          file, thus they might not be as indicative as strain names in the mentioned file 
          ('define_architectures.txt', with plotting purposes).

"""

###############################################################################
###############################################################################

import sys

# LINE COMMAND PARAMETERS
###############################################################################
# Reference file for updating SMAC conditionals on biomasses 
define_conditionals_file = sys.argv[1]

# Name of PCS file
smac_pcs_file = sys.argv[2]

# Number of arguments without considering those after 'n_models' (i.e. uptake rates + 'n_models' SMAC args)
with open(smac_pcs_file, "r") as def_file:
    lines = def_file.readlines()
    
    for line in lines:
        param_name = line.strip("\n").split()[0]
        if param_name.split("_")[1] == "nmodels":
            n_arg_nmodels = int(list(param_name.split("_")[0])[1])
            break
###############################################################################


###############################################################################

# BUILD A DICTIONARY WITH THE ORIGINAL FILE ON SMAC CONDITIONALS & CONSORTIUM ARCHITECTURE
# -----------------------------------------------------------------------------
architecture_dictionary = {}

with open(define_conditionals_file, "r") as def_file:
    lines = def_file.readlines()
          
    for line in lines:
        line = line.strip("\n").split(":")
        architecture_dictionary[int(line[0])] = line[1].split(",")  # List of variable names
        
        
# Base consortium architecture (the simplest one among possibilities)
min_n_models = min(architecture_dictionary.keys())
# Counter for proper numbering of conditionals
n_add_strains = min_n_models + 1


# UPDATE PCS FILE WITH SMAC CONDITIONALS ON BIOMASSES
# -----------------------------------------------------------------------------
for n_models_key in architecture_dictionary.keys():
    
    # Discard the base consortium architecture (no conditionals)
    if n_models_key != min_n_models:  
        
        # For every strain in a given architecture
        for strain in architecture_dictionary[n_models_key]:
            
            # If it it is not a base strain, but rather a strain specific to a given consortium architecture
            if strain not in architecture_dictionary[min_n_models]:  
                
                # Update PCS file with conditional
                with open(smac_pcs_file, "a") as smac_file:
                    smac_file.write("\np{0}_biomass_{1} | p{2}_nmodels == {3}_models".format(n_arg_nmodels + n_add_strains, strain, n_arg_nmodels, n_models_key))
                    # smac_file.write(f"\np{n_arg_nmodels + n_add_strains}_biomass_{strain} | p{n_arg_nmodels}_nmodels == {n_models_key}_models")
                    n_add_strains += 1  # Update counter for proper numbering of conditionals
                    
###############################################################################



























