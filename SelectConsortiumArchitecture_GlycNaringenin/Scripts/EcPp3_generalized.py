#!/usr/bin/python
"""
Created on Mon May 17 10:31:53 2021

# Author: Beatriz García-Jiménez, Iván Martín Martín
# April 2018, June 2021
"""

###############################################################################
# SCRIPT DESCRIPTION   
###############################################################################
"""
PIPELINE DESIGNED FOR SELECTION OF THE BEST ARCHITECTURE FOR A GIVEN CONSORTIUM
-------------------------------------------------------------------------------
Series of functions:
    
    - "biomass_evolution_during_simulation" function for a given number of strains (say 'n')
    - "SelectConsortiumArchitecture" function for a given number of strains (say 'n')


The current script is designed so that the number of strains in a particular
architecture is inferred from the length of the list of strains given as a parameter. 

In this sense, THE ORDER IN WHICH THE STRAINS ARE GIVEN IN THAT LIST is key to
determine how the script works and how the associated files should be organized.
For example, this impacts the final plotting of biomass evolution.



Note that the next three files are important for the script to work and evaluate
the architecture that is currently running.


  * define_architecture.txt
  -------------------------
  FORMAT (each line): ARCHITECTURE_n:strain1,strain2,...,strain_n
      - NO blank spaces, comma as separator character except for the colon
      
  CONTENT: each line contains the strains composing a given architecture.
  
  
  * initialize_models.txt
  ------------------------
  FORMAT: (each line): ARCHITECTURE_n:function1,function2,...,function_n
        - NO blank spaces, comma as separator character except for the colon
          
  CONTENT: each line contains the function names for initializing a given architecture.
      	
  
  * initialize_variables.txt
  --------------------------
  FORMAT: FUNCTION_n:var1,var2,..., var_n
      - NO blank spaces, comma as separator character except for the colon
      
  CONTENT: each line contains the variable names required for calling a function 
      for intializing a particular GEM model

"""

# -----------------------------------------------------------------------------


# MODULES
# -----------------------------------------------------------------------------
# PYTHON MODULES
import cobra
import os, stat
import pandas as pd
import tabulate
import re
import sys
import getopt
import os.path
import copy
import csv
import math
import cobra.flux_analysis.variability
import massedit
import subprocess
import shutil, errno
import statistics
import optlang
import collections
from cobra import Reaction
from cobra import Metabolite
# import gurobipy
# import spec


# OUR MODULES FOR FLYCOP TO WORK
import EcPp3_generalized_initialize_GEMs
# -----------------------------------------------------------------------------


###############################################################################    
### FUNCTION dead_biomass_tracking  ###########################################

# DEAD TRACKING DURING THE COMMUNITY SIMULATION 
# UPDATED: 11-ago-21

# n_cycles: number of minimum consecutive cycles where biomass loss has to be 
# detected to consider the effect to be happening

# min_biomass_loss_allowed: minimum of biomass loss required to happen in a given cycle
# (in order to avoid slight biomass fluctuations). Note that this minimum loss
# is the result of a subtraction, thus it is later preceded by a minus sign 

# biomass_indexes: list of column indexes for the given microbe in the COMETS_file


# INDICATORS
# ----------

# lower_than_init_biomass: if the total biomass at any cycle during the simulation
# becomes lower than the initial biomass, the biomass loss effect is determined to
# be present. The first cycle where this effect is registered is considered as "endCycle"
# REVERSIBLE EFFECT (see below)

# biomass_loss_in_cycle: if there is biomass loss in the current cycle. There has to be
# biomass loss during more than "n_cycles" for the "biomass_track" indicator to detect
# the effect

# biomass_track: presence (1) or absence (0) of biomass loss

# -----------------------------------------------------------------------------
# Note that we track biomass loss during the complete simulation, but we are not 
# able to determine whether biomass loss has been continuous or intermitent 
# since the first time (first 10 consecutive cycles) it was detected. 

# Moreover, the current implementation does not either allow for determining 
# if there is just one or more microbes experiencing biomass loss in the community.
# -----------------------------------------------------------------------------

# 'Reversible Dead Tracking': biomass_track = -1
# In case of an initial biomass loss which is later regained, the 'biomass_track' 
# indicator is reversible (value = -1), in two scenarios:
    
    # a) if the total biomass in a given cycle happens to be lower than initial 
    # biomass eventually, but it is later regained.
    
        # lower_than_init_biomass set to 'False' again
    
    # b) if there has been biomass loss during more than 10 consecutive cycles, 
    # but there has also been biomass growth during more than 10 consecutive
    # (posterior) cycles as well.
    
        # biomass_growth = True  # Reversible Dead Tracking
        # biomass_growth_cycles = 0  # Number of consecutive cycles with biomass growth (counter)


def biomass_evolution_during_simulation(CometsTable, n_cycles = 10, min_biomass_loss_allowed = 1e-4, biomass_indexes = []):
    cycle_count = 0
    
    biomass_track = 0  # Biomass loss absence: 0; Biomass loss presence: 1
    count_cons_cycles = 0  # Number of consecutive cycles with biomass loss (counter)
    
    initial_dead = 0  # Cycle where the effect is considered to start
    init_biomass = 0  # Total initial biomass, at the beginning of the simulation
    
    biomass_growth = True  # Reversible Dead Tracking
    biomass_growth_cycles = 0  # Number of consecutive cycles with biomass growth (counter)
    
    # Dictionary: (biomass_i): last_biomass_value (last cycle)
    last_biomass = collections.OrderedDict()
    # Dictionary: (biomass_i): biomass_value (current cycle)
    biomass = collections.OrderedDict()
    
    
    # ITERATE ON COMETS_FILE, row by row
    # Note tuple 241 = cycle 240; tuple 0 = initial situation
    # -------------------------------------------------------
    for row in CometsTable.itertuples():  
        cycle = row[0]
        lower_than_init_biomass = False  # INDICATOR 
        cycle_count += 1

        
        # ---------------------------------------------------------------------------------------
        # BLOCK 1
        # Evaluate if there is biomass loss within the cycle and update 'last_biomass' dictionary
        # ---------------------------------------------------------------------------------------
        counter = 1
        if cycle == 0:  # Initial cycle
            for index in biomass_indexes:
                last_biomass["biomass"+str(counter)] = CometsTable.loc[cycle, CometsTable.columns[index]]  
                init_biomass += CometsTable.loc[cycle, CometsTable.columns[index]]
                counter += 1
            
            # Initial cycle is always 'cycle == 0'
            initCycle = cycle
            
        elif cycle != 0:  # Posterior cycle
            biomass_loss_in_cycle = False  # INDICATOR 
            cycle_total_biomass = 0  # Total biomass in the current cycle
            
            # For every microbe in the consortium
            counter = 1
            for index in biomass_indexes:  
                
                # Update dictionary on current biomass values
                biomass["biomass"+str(counter)] = CometsTable.loc[cycle, CometsTable.columns[index]]
                # Update total biomass in the current cycle
                cycle_total_biomass += CometsTable.loc[cycle, CometsTable.columns[index]]  
                
                # In case of biomass loss for a given microbe
                # Biomass loss is considered if the next substraction gives a negative value under
                # the minimal biomass loss allowed (min_biomass_loss_allowed)
                if float(biomass["biomass"+str(counter)] - last_biomass["biomass"+str(counter)] < (- min_biomass_loss_allowed)):
                    biomass_loss_in_cycle = True  # Set indicator to True
                    count_cons_cycles += 1  # Add up a new consecutive cycle  
                    last_dead = cycle  # Last cycle where the effect is registered
                    biomass_growth = False  # In the current cycle, biomass does not grow (it has been lost)
                    
                counter += 1
            
            
            # If there has not been biomass loss in the current and the previous cycle
            if not biomass_loss_in_cycle and biomass_growth:
                biomass_growth_cycles += 1  # Number of CONSECUTIVE cycles of biomass growth
                
                
            # If there has not been biomass loss in the current cycle
            if not biomass_loss_in_cycle:
                count_cons_cycles = 0  # Number of CONSECUTIVE cycles of biomass loss, back to 0
                biomass_growth = True  # In the current cycle, biomass has grown (very likely, since it has not been lost)
                
                
            # If the total biomass in the current cycle is lower than the initial biomass in origin
            if (float(cycle_total_biomass) < float(init_biomass)): 
                lower_than_init_biomass = True  # Set indicator to True
            
            
            # If the total biomass in the current cycle is again higher than the initial biomass in origin,
            # after having been lower (lower_than_init_biomass = True --> False)
            elif lower_than_init_biomass and (float(cycle_total_biomass) > float(init_biomass)): 
                lower_than_init_biomass = False  # Set indicator to False
                
                
            # Biomass values in current cycle become last biomass values
            counter = 1
            for index in biomass_indexes: 
                last_biomass["biomass"+str(counter)] = CometsTable.loc[cycle, CometsTable.columns[index]]
                counter += 1
            
                
        # ---------------------------------------------------------------------
        # BLOCK 2
        # ---------------------------------------------------------------------
        # If there is biomass loss during more than 10 consecutive cycles or 
        # if current total biomass is higher than initial biomass, 
        # BIOMASS LOSS is considered to be present
        # ---------------------------------------------------------------------
        # Set endCycle depending on biomass_track
        # ---------------------------------------------------------------------
        
        # Activation of 'Dead Tracking'
        if (count_cons_cycles >= n_cycles or lower_than_init_biomass) and biomass_track != 1:
            biomass_track = 1
            if initial_dead == 0: initial_dead = last_dead - count_cons_cycles
            endCycle = last_dead
        
        # 'Reversible Dead Tracking'
        elif biomass_track == 1 and (not lower_than_init_biomass and biomass_growth_cycles >= n_cycles):
            biomass_track = -1
            endCycle = last_dead
        
        # In case of NO BIOMASS LOSS or EQUIVALENT so far
        # The endCycle is the last cycle evaluated so far, since there is not any biomass loss effect currently registered
        if biomass_track != 1: endCycle = cycle
        # ---------------------------------------------------------------------
        
        
    # REGISTER EFFECT, AS IT CORRESPONDS       
    # -------------------------------------------------------------------------
    # print("Cycle count: ", cycle_count)
    
    # Initial line in the simulation
    initLine = CometsTable.iloc[initCycle].to_list()
    # Final line in the simulation
    finalLine = CometsTable.iloc[endCycle].to_list()
    # Correction of endCycle
    if initial_dead < 0: initial_dead = 0
        
    if biomass_track != 0:
        dead_cycles = str(initial_dead)+"-"+str(last_dead)  # biomass_track = 1 or -1 ('Reversible Dead Tracking')
        
    else:
        dead_cycles = "NoBiomassLoss"  # biomass_track = 0
    
    return biomass_track, dead_cycles, initLine, finalLine
        
### FUNCTION dead_biomass_tracking  ###########################################
###############################################################################



###############################################################################
### FUNCTION EcoliPputidaOneConf ##############################################
def SelectConsortiumArchitecture(sucr1, frc2, nh4_Ec, nh4_KT, consortium_arch, initial_biomass,
                                 fitObj='MaxGlycNar', maxCycles = 240, dirPlot='', repeat=5, sd_cutoff = 0.1,
                                 models_summary=False):  # At the moment, fitObj and maxCycles have no real utility
  '''
  Call: avgFitness, sdFitness = SelectConsortiumArchitecture(sucr1, frc2, nh4_Ec, nh4_KT, initial_biomass, consortium_arch, **args)
  Start with no more than 5 repeats (1st trial)

  INPUTS: 
      
      a. SERIES OF SMAC-OPTIMIZED PARAMETER VALUES. In the current example:

          sucr1: lower bound of sucrose uptake in E.coli W models (mM)
          frc2: lower bound of fructose uptake in model 2 (P.putida KT2440) (mM)
          nh4_Ec: lower bound of nh4 uptake in E.coli W (mM)
          nh4_KT: lower bound of nh4 uptake in P.putida KT2440 (mM)
          
      b. LIST OF INITIAL BIOMASSES OF STRAINS IN A GIVEN CONSORTIUM ARCHITECTURE (initial_biomass)
      c. CONSORTIUM ARCHITECTURE (consortium_arch)
          
      d. OTHER IMPORTANT PARAMETERS
      
          fitObj: fitness function to optimize. In the current example, 'MaxGlycNar' - maximize glycosilated naringenin production by the consortium
          maxCycles: cycles in COMETS run, stated in file 'layout_template'. It is not used in the Python scripts (wrapper, individualTest). 
              If desired to change, see 'layout_template'.
          dirPlot: copy of the plots with several run results.
          repeat: number of runs with the same configuration (COMETS, not number of SMAC iterations)
          
          
  OUTPUT: avgFitness: average fitness of 'repeat' COMETS runs with the same configuration (due to it is not deterministic)
          sdFitness: standard deviation of fitness during 'repeat' COMETS runs (see above)
  '''

  
  # Current directory: temporal folder 'xxx_TestTempV0'
  temporal_folder = os.getcwd()
  os.chdir("../EcPp3_TemplateOptimizeConsortiumV0")
  
  # 1) COMPOSE STRAINS LIST
  # ===========================================================================
  # This code block extracts the strains in the model architecture and composes
  # an ordered list of them, for further plotting
  # ===========================================================================
  # DIR: xxx_TemplateOptimizeConsortiumV0
  
  with open("define_architecture.txt", "r") as define_architecture:
      lines = define_architecture.readlines()
      
      # Number of potential consortium architectures
      # n_architectures = len(lines)
      
      # lines[0] = Consortium Architecture
      for line in lines:
          line = line.strip("\n").split(":")
          if line[0] == consortium_arch:
              strains_list = line[1].split(",")
              strains_string = "'"+(" ").join(strains_list)+"'"  # Doble quotes are important for later transfer of this variable to bash

      n_strains = len(strains_list)  # Number of strains in the current consortium
  
  

  # 2) WHICH MODELS TO INITIALIZE (depending on the consortium architecture)
  # ===========================================================================
  # a) Create a dictionary with key(function) : value(variables) for retrieving the parameter names
  # It contains all the functions for all possible architectures in the given consortium
  # ===========================================================================
    
  # DIR: xxx_TemplateOptimizeConsortiumV0
  print("INITIALIZING AND UPDATING GEM MODELS")
  print("------------------------------------\n")
  
  function_variables = {}
  with open("initialize_variables.txt", "r") as var_for_functions:
      lines = var_for_functions.readlines()
          
      for line in lines:
          line = line.strip("\n").split(":")
          function_variables[line[0]] = line[1].split(",")  # List of variable names

  
  # ===========================================================================
  # b) Execute initialization functions through the last dictionary
  # ===========================================================================
  # DIR: xxx_TemplateOptimizeConsortiumV0
  
  with open("initialize_models.txt", "r") as initialize_models:
      lines = initialize_models.readlines()
      
      for line in lines:
          line = line.strip("\n").split(":")
          if line[0] == consortium_arch:
              initialize_functions = line[1].split(",")
              
              module = sys.modules["EcPp3_generalized_initialize_GEMs"]  # Module containing functions to initialize and update GEMs models
              for init_function_name in initialize_functions:
                    
                    variables = []
                    for variable in function_variables[init_function_name]:
                        variables.append(locals()[variable])
                    
                    models_summary = True if models_summary else False
                    getattr(module, init_function_name)(*variables, temporal_folder=temporal_folder, models_summary=models_summary) 
 


  # =========================================================================== 
  # 3) COMETS: running and results
  # =========================================================================== 
  
  os.chdir(temporal_folder)
  # DIR: xxx_TestTempV0

  # Set initial biomass for all microbes
  # [shell script] Write automatically the COMETS parameters about initial biomass of strains
  # ---------------------------------------------------------------------------
  # The codification of biomasses in layout file should be a string of 5 equal figures, 
  # depending on the number of strains in the consortium: 11111, 22222, 33333, etc.
  # ---------------------------------------------------------------------------
  
  for i in range(len(initial_biomass)):
      massedit.edit_files(['EcPp3_layout_template2_'+consortium_arch+'.txt'],["re.sub(r'"+str(i+1)*5+"','"+str(initial_biomass[i])+"',line)"], dry_run=False)
 
    
  # RUN COMETS
  # [COMETS by command line] RUN COMETS
  # ----------------------------------------------------------------------------
  
  if not(os.path.exists('IndividualRunsResults')):
    os.makedirs('IndividualRunsResults')
    
  # Initial variables to track during execution
  totfitness=0
  sum_Nar=0  # Naringenin quantity variable (production by P.putida KT)
  sum_glycNar=0  # Glycosilated naringenin quantity variable (production by E.coli W, glycosilator strain)
  fitnessList=[]  # List with the different values for 'totfitness' in every execution ('n' repeats)
  suffix = "template2"  # Variable to be modified depending on the names of COMETS files
  
  # DIR: xxx_TestTempV0
  for i in range(repeat):
        
        # --------------------------------------------------------------------------
        # RUNNING COMETS + [R call] Run script to generate one graph:subprocess.call
        # DIR: xxx_TestTempV0
        # --------------------------------------------------------------------------
        with open("output.txt", "w") as f:
            subprocess.run(args=['./comets_scr', 'comets_script_template'+consortium_arch], stdout=f, stderr=subprocess.STDOUT)
            
        n_metabolites = 7  # 7 metabolites to track (manual adjustment by user). In this case: sucr nar7glu fru nar nh4 pi o2
        n_columns_without_biomass = n_metabolites + 1  # Column of cycle_number in the COMETS output file
        
        # String of initial biomasses for base configuration (baseConfig)
        initial_biomass_string = ""
        for init_biomass in initial_biomass:
            initial_biomass_string += ","+str(init_biomass) if initial_biomass_string else str(init_biomass)
            
        baseConfig=str(sucr1)+','+str(frc2)+','+str(nh4_Ec)+','+str(nh4_KT)+','+str(consortium_arch)+','+initial_biomass_string
        
        # Line to plot COMETS output 
        # 6 colours are given since O2 is not represented (i.e. we do not need 7 colours, just 6)
        subprocess.run(['../../Scripts/plot_biomassX2_vs_4mediaItem_generalized.sh template2 sucr nar7glu fru nar nh4 pi o2 '+str(maxCycles)+' '+baseConfig+' blue black darkmagenta yellow orange aquamarine '+strains_string], shell=True)
            
        # ---------------------------------------------------------------------
        # INDEX REFERENCES IN COMETS FILE (organized in columns)
        # ---------------------------------------------------------------------
        # sucr  nar7glu  fru  nar  nh4  pi  o2  cycle_number  Biomass1  Biomass2  Biomass3  [...]
        # 0     1        2    3    4    5   6   7             8         9         10        11
        # ---------------------------------------------------------------------
        
        
        
        # ---------------------------------------------------------------------
        # COMPUTE METRICS FROM COMETS
        # DIR: xxx_TestTempV0
        # ---------------------------------------------------------------------
        
        # (0) BIOMASS EVOLUTION
        #######################
        biomass_indexes = []
        for n_strain in range(n_strains):
            # Indexes for 'biomass_evolution_during_simulation' function
            biomass_indexes.append(n_columns_without_biomass + n_strain)
                
        CometsTable = pd.read_csv("COMETS_"+baseConfig+"_"+suffix+".txt", sep="\t", header=None)
        biomass_track, dead_process, initLine, finalLine = biomass_evolution_during_simulation(CometsTable, n_cycles = 10, min_biomass_loss_allowed= (1e-4), biomass_indexes = biomass_indexes)
        
        
        # (1) INITIAL BIOMASS
        #####################
        init_biomass = 0
        init_biomasses_dict = {}
        
        for n_strain in range(n_strains):
            # Initial biomass value for each microbe (individually)
            init_biomasses_dict[strains_list[n_strain]] = float(initLine[n_columns_without_biomass + n_strain])
            # (Global) initial biomass
            init_biomass += float(initLine[n_columns_without_biomass + n_strain])
            
            
        # (2) FINAL CONCENTRATIONS: pCA, Nar, limiting nutrients
        ##########################
        sucrConc=float(finalLine[0])  # Final sucrose
        tot_glicNar=float(finalLine[1])  # Final glycosilated naringenin
        tot_Nar=float(finalLine[3])  # Final Naringenin
        NH4conc=float(finalLine[4])  # Final NH4 (first limiting nutrient)
        Final_pi=float(finalLine[5])  # Second limiting nutrient
        Final_O2=round(float(finalLine[6]), 4)  # Final O2
        finalCycle=int(finalLine[7])  # Final Cycle
        
        
        # (3) FINAL BIOMASS
        ###################
        total_final_biomass = 0
        final_biomasses_dict = {}
        
        for n_strain in range(n_strains):
            # Final biomass value for each microbe (individually)
            final_biomasses_dict[strains_list[n_strain]] = float(finalLine[n_columns_without_biomass + n_strain])
            # (Global) final biomass 
            total_final_biomass += float(finalLine[n_columns_without_biomass + n_strain])


        # DEBUGGING
        ####################################
        print("\n--------------------------")
        print("Initial biomass: ", init_biomass)
        print("Initial line:", initLine)
        print("Final line: ", finalLine)
        print("Final biomass: ", total_final_biomass)
        print("---------------------------\n")
    
    
        # (4) Pi OVERCONSUMPTION TRACKING (currently disabled)
        ######################################################
        # pi_overconsumption, pi_cycles = metabolite_tracking_overconsumption("COMETS_"+baseConfig+"_"+suffix+".txt", 10.0, 9)
        
        # (5) COMPUTE FITNESS: maximize decorated naringenin
        ####################################################
        # if fitObj == "MaxGlycNar":
        fitFunc = tot_glicNar / (total_final_biomass)  # Final glycosilated naringenin yield over GLOBAL biomass (all microorganisms in the consortium)
        # POTENTIAL REDEFINITION OF FITNESS
        fitness=fitFunc
        
        # (6) UPDATE REPEATS
        ####################
        totfitness += fitness  # 'n' repeats
        fitnessList.append(fitness)  # List with fitness values in 'n' repeats
        sum_Nar += tot_Nar  # Total naringenin for 'n' repeats
        sum_glycNar += tot_glicNar  # Total glycosilated naringenin for 'n' repeats
    
        
        # ---------------------------------------------------------------------
        # PRINTING
        # ---------------------------------------------------------------------
        print("\nFitness(mM/gL): "+str(round(fitness,6))+" in cycle "+str(finalCycle))
        print("Execution: "+str(i+1)+" of "+str(repeat)+". Final cycle: "+str(finalCycle))
        print("Naringenin (mM): "+str(tot_Nar)+"\t"+"Glycosilated Nar (mM): "+str(tot_glicNar))
        # print("Biomass track checking: ", biomass_track, dead_process)
        for strain_key in final_biomasses_dict.keys():
            print("Final "+strain_key+" biomass (g/L): ", final_biomasses_dict[strain_key])

        
        # ---------------------------------------------------------------------
        # DIR: xxx_TestTempV0
        # ---------------------------------------------------------------------
        # Copy individual solution
        file='IndividualRunsResults/'+baseConfig+"_run"+str(i+1)+'_'+str(fitness)+'_'+str(finalCycle)+'.pdf'
        shutil.move(baseConfig+"_"+suffix+"_plot.pdf", file)        
        if(dirPlot != ''):
            file2=dirPlot+baseConfig+'_run'+str(i+1)+'_'+str(fitness)+'_'+str(finalCycle)+'.pdf'
            shutil.move(file,file2)
            
        file='IndividualRunsResults/'+'total_biomass_log_run'+str(i+1)+'.txt'
        shutil.move('total_biomass_log_'+suffix+'.txt',file)
        file='IndividualRunsResults/'+'media_log_run'+str(i+1)+'.txt'
        shutil.move('media_log_'+suffix+'.txt',file)
        file='IndividualRunsResults/'+'flux_log_run'+str(i+1)+'.txt'
        shutil.move('flux_log_'+suffix+'.txt',file)   
        # ---------------------------------------------------------------------
       
        
  # END OF 5 REPEATS
  # ---------------------------------------------------------------------------
  # MEAN & SD COMPUTATION for all (n = 5) repeats
  # ---------------------------------------------------------------------------
  avgfitness=totfitness/repeat  # 'totfitness' average in 'n' repeats
  if(repeat>1):
      sdfitness=statistics.stdev(fitnessList)  # standard deviations for 'n' values
  else:
      sdfitness=0.0
      
  # Correction if SD is too high. Maximum allowed SD = sd_cutoff variable
  # -------------------------------------------------------------------
  if sdfitness > float(sd_cutoff)*(avgfitness): 
       ID_SD = 1 
  else: ID_SD = 0
  # -------------------------------------------------------------------
  
  avgNar = sum_Nar/repeat  # Average naringenin (5 repeats)
  avgglycNar = sum_glycNar/repeat  # Average glycosilated naringenin (5 repeats)
  # ---------------------------------------------------------------------------
  
  

  # ---------------------------------------------------------------------------
  # SAVE RESULTS in TABLE: 'configurationsResults(...).txt' file
  # DIR: xxx_TestTempV0
  # ---------------------------------------------------------------------------
  
  if not os.path.isfile(dirPlot+"configurationsResults-"+consortium_arch+".txt"):  # CREATE FILE
  
      myfile = open(dirPlot+"configurationsResults-"+consortium_arch+".txt", "w")
      
      # HEADER
      myfile.write("FitObjective\tBaseConfig\tsucr_upt\tfrc_upt\tnh4_Ec\tnh4_KT\tConsortium_Arch\t")
      
      myfile.write("global_init_biomass\t")
      for strain_key in init_biomasses_dict.keys():
          myfile.write("init_"+strain_key+"\t") 
          
      myfile.write("global_final_biomass\t")
      for strain_key in final_biomasses_dict.keys():
          myfile.write("final_"+strain_key+"\t")  
      
      myfile.write("fitFunc\tSD\tID_SD\tGlycNar_mM\tNar_mM\t")
      myfile.write("endCycle\tNH4_mM\tpi_mM\tBiomassLoss\tDT_cycles\tFinalSucr\tFinalO2\n")  
      
      # INFORMATION LINE
      myfile.write(fitObj+"\t"+baseConfig+"\t"+str(sucr1)+"\t"+str(frc2)+"\t"+str(nh4_Ec)+"\t"+str(nh4_KT)+"\t"+str(consortium_arch)+"\t")
     
      myfile.write(str(init_biomass)+"\t")
      for strain_key in init_biomasses_dict.keys():
          myfile.write(str(init_biomasses_dict[strain_key])+"\t")
                   
      myfile.write(str(total_final_biomass)+"\t")
      for strain_key in final_biomasses_dict.keys():
          myfile.write(str(final_biomasses_dict[strain_key])+"\t")
                   
      myfile.write(str(round(avgfitness, 6))+"\t"+str(round(sdfitness, 6))+"\t"+str(ID_SD)+"\t"+str(round(avgglycNar, 6))+"\t"+str(round(avgNar, 6))+"\t")
      myfile.write(str(finalCycle)+"\t"+str(round(NH4conc, 4))+"\t"+str(round(Final_pi, 4))+"\t"+str(biomass_track)+"\t")
      myfile.write(str(dead_process)+"\t"+str(round(sucrConc, 4))+"\t"+str(Final_O2)+"\n")
                   
      myfile.close()
      
      
  else:  # APPEND TO THE EXISTING FILE
      myfile = open(dirPlot+"configurationsResults-"+consortium_arch+".txt", "a")
      
      # INFORMATION LINE
      myfile.write(fitObj+"\t"+baseConfig+"\t"+str(sucr1)+"\t"+str(frc2)+"\t"+str(nh4_Ec)+"\t"+str(nh4_KT)+"\t"+str(consortium_arch)+"\t")
     
      myfile.write(str(init_biomass)+"\t")
      for strain_key in init_biomasses_dict.keys():
          myfile.write(str(init_biomasses_dict[strain_key])+"\t")
                   
      myfile.write(str(total_final_biomass)+"\t")
      for strain_key in final_biomasses_dict.keys():
          myfile.write(str(final_biomasses_dict[strain_key])+"\t")
                   
      myfile.write(str(round(avgfitness, 6))+"\t"+str(round(sdfitness, 6))+"\t"+str(ID_SD)+"\t"+str(round(avgglycNar, 6))+"\t"+str(round(avgNar, 6))+"\t")
      myfile.write(str(finalCycle)+"\t"+str(round(NH4conc, 4))+"\t"+str(round(Final_pi, 4))+"\t"+str(biomass_track)+"\t")
      myfile.write(str(dead_process)+"\t"+str(round(sucrConc, 4))+"\t"+str(Final_O2)+"\n")
                   
      myfile.close()
      
      
  return avgfitness, sdfitness, strains_list
# END OF FUNCTION: EcoliPputidaFLYCOP_selectConsortiumArchitecture
###############################################################################    
""" 
  # ---------------------------------------------------------------------------
  # SAVE RESULTS in TABLE: 'configurationsResults(...).txt' file
  # DIR: XXX_TestTempV0
  # ---------------------------------------------------------------------------
  
  if not os.path.isfile(dirPlot+"configurationsResults_"+fitObj+".xlsx"):  # CREATE FILE
  
      # CREATE PANDAS DATAFRAME WITH HEADER
      configTable = pd.DataFrame(columns=["FitObjective", "BaseConfig", "sucr_upt", "frc_upt", "nh4_Ec", "nh4_KT", "Consortium_Arch"])
      
      configTable = configTable.assign(column="global_init_biomass")
      for strain_key in init_biomasses_dict.keys():
          configTable = configTable.assign(column="init_"+strain_key) 
          
      configTable = configTable.assign(column="global_final_biomass")
      for strain_key in final_biomasses_dict.keys():
          configTable = configTable.assign(column="final_"+strain_key)  
      
      configTable = pd.concat([configTable, pd.DataFrame(columns=["fitFunc", "SD", "ID_SD", "GlycNar_mM", "Nar_mM"])], axis=1)
      configTable = pd.concat([configTable, pd.DataFrame(columns=["endCycle", "NH4_mM", "pi_mM", "DeadTracking", "DT_cycles", "FinalSucr", "FinalO2"])], axis=1)

      
      # INFORMATION LINE
      myfile = open(dirPlot+"informationLine_"+consortium_arch+".txt", "w")
      myfile.write(fitObj+"\t"+baseConfig+"\t"+str(sucr1)+"\t"+str(frc2)+"\t"+str(nh4_Ec)+"\t"+str(nh4_KT)+"\t"+str(consortium_arch)+"\t")
     
      myfile.write(str(init_biomass)+"\t")
      for strain_key in init_biomasses_dict.keys():
          myfile.write(str(init_biomasses_dict[strain_key])+"\t")
                   
      myfile.write(str(total_final_biomass)+"\t")
      for strain_key in final_biomasses_dict.keys():
          myfile.write(str(final_biomasses_dict[strain_key])+"\t")
                   
      myfile.write(str(round(avgfitness, 6))+"\t"+str(round(sdfitness, 6))+"\t"+str(ID_SD)+"\t"+str(round(avgglycNar, 6))+"\t"+str(round(avgNar, 6))+"\t")
      myfile.write(str(finalCycle)+"\t"+str(round(NH4conc, 4))+"\t"+str(round(Final_pi, 4))+"\t"+str(biomass_track)+"\t")
      myfile.write(str(dead_process)+"\t"+str(round(sucrConc, 4))+"\t"+str(Final_O2)+"\n")
      myfile.close()
      
      # APPEND INFORMATION LINE TO PANDAS DATAFRAME
      information_line = pd.read_csv(dirPlot+"informationLine_"+consortium_arch+".txt", sep="\t", header='infer')
      configTable = configTable.append(information_line)
      
      # REMOVE INFORMATION LINE, CREATE EXCEL FILE WITH SHEET='consortium_arch'
      os.remove(dirPlot+"informationLine_"+consortium_arch+".txt")
      configTable.to_excel(dirPlot+"configurationsResults_"+fitObj+".xlsx", sheet_name=consortium_arch, header=True, index=True, index_label=None)
      
      
  else:  # APPEND TO THE EXISTING EXCEL FILE
  
      configTable = pd.read_excel(dirPlot+"configurationsResults_"+fitObj+".xlsx", sheet_name=consortium_arch, header=True, engine="openpyxl")
  
      # INFORMATION LINE
      myfile = open(dirPlot+"informationLine_"+consortium_arch+".txt", "w")
      myfile.write(fitObj+"\t"+baseConfig+"\t"+str(sucr1)+"\t"+str(frc2)+"\t"+str(nh4_Ec)+"\t"+str(nh4_KT)+"\t"+str(consortium_arch)+"\t")
     
      myfile.write(str(init_biomass)+"\t")
      for strain_key in init_biomasses_dict.keys():
          myfile.write(str(init_biomasses_dict[strain_key])+"\t")
                   
      myfile.write(str(total_final_biomass)+"\t")
      for strain_key in final_biomasses_dict.keys():
          myfile.write(str(final_biomasses_dict[strain_key])+"\t")
                   
      myfile.write(str(round(avgfitness, 6))+"\t"+str(round(sdfitness, 6))+"\t"+str(ID_SD)+"\t"+str(round(avgglycNar, 6))+"\t"+str(round(avgNar, 6))+"\t")
      myfile.write(str(finalCycle)+"\t"+str(round(NH4conc, 4))+"\t"+str(round(Final_pi, 4))+"\t"+str(biomass_track)+"\t")
      myfile.write(str(dead_process)+"\t"+str(round(sucrConc, 4))+"\t"+str(Final_O2)+"\n")
      myfile.close()
      
      # APPEND INFORMATION LINE TO PANDAS DATAFRAME
      information_line = pd.read_csv(dirPlot+"informationLine_"+consortium_arch+".txt", sep="\t", header='infer')
      configTable = configTable.append(information_line)
      
      # REMOVE INFORMATION LINE, CREATE EXCEL FILE WITH SHEET='consortium_arch'
      os.remove(dirPlot+"informationLine_"+consortium_arch+".txt")
      configTable.to_excel(dirPlot+"configurationsResults_"+fitObj+".xlsx", sheet_name=consortium_arch, header=True, index=True, index_label=None)
      
      
  return avgfitness, sdfitness
# END OF FUNCTION: EcoliPputidaFLYCOP_selectConsortiumArchitecture
############################################################################### 
"""   
      

  
  














