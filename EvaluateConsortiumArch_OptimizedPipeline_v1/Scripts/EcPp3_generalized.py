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
    
    - "dead_biomass_tracking_unique" function for a given number of strains (say 'n')
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
# NOTE THAT row_number is considered a column with Pandas

# Dead Tracking within the community simulation: 
# if biomass of any strain (or several strains) decreases during more than 'n_cycles' consecutive cycles

# The endcycle can occur when the substrate (sucrose) is finally exhausted, which might not always happen in the last cycle
# cycles_number = len(CometsTable) - 1 # Lenght: 241 (initial row + 240 cycles)

# biomass_indexes: column index for a given microbe in the COMETS_file
# ---
# Note that we track biomass loss during the complete simulation, but we are not able to determine
# whether biomass loss has been continuous or intermitent since the first time (first 10 consecutive cycles)
# it was detected
# -----------------------------------------------------------------------------

def dead_biomass_tracking_unique(COMETS_file, endCycle, n_cycles = 10, biomass_indexes = []):
    CometsTable = pd.read_csv(COMETS_file, sep="\t", header=None)
    biomass_track = 0
    count_cons_cycles = 0
    initial_dead = 0
    cycle_count = 0
    
    # Dictionary: (biomass_i): last_biomass_value
    last_biomass = collections.OrderedDict()
    # Dictionary: (biomass_i): biomass_value
    biomass = collections.OrderedDict()
    
    # Iterate in COMETS file
    # ----------------------
    for row in CometsTable.itertuples():  # Note tuple 241 = cycle 240; tuple 0 = initial situation
        cycle = row[0]
        
        # Evaluate if there is biomass loss within the cycle and update 'last_biomass' dictionary
        # ---------------------------------------------------------------------------------------
        if cycle == 0:
            for i in range(len(biomass_indexes)):
                last_biomass["biomass"+str(i+1)] = row[biomass_indexes[i]]
            
        elif cycle != 0:
            cycle_count += 1
            biomass_loss_in_cycle = False
            for i in range(len(biomass_indexes)):
                biomass["biomass"+str(i+1)] = row[biomass_indexes[i]]
                
                if (biomass["biomass"+str(i+1)] - last_biomass["biomass"+str(i+1)]) < 0:  # cannot distinguish between the microbe experiencing biomass loss
                    biomass_loss_in_cycle = True   
                    count_cons_cycles += 1                                                # might be just one or both
                    last_dead = cycle
                    
                # If there is no biomass loss for a given microbe and there has not been previous biomass loss for other microbes within the same cycle
                elif (biomass["biomass"+str(i+1)] - last_biomass["biomass"+str(i+1)]) > 0 and not biomass_loss_in_cycle:
                    count_cons_cycles = 0
                
            for i in range(len(biomass_indexes)):
                last_biomass["biomass"+str(i+1)] = row[biomass_indexes[i]]
         
            
        # If there is biomass loss during more than 10 consecutive cycles, this effect is considered to be present
        # --------------------------------------------------------------------------------------------------------
        if count_cons_cycles > 10 and not biomass_track:
            biomass_track = 1
            initial_dead = last_dead - count_cons_cycles
            
    # If the effect is considered to be present, register the corresponding cycles       
    # ----------------------------------------------------------------------------
    # print("Contador de ciclos: ", cycle_count)
    if biomass_track:
        dead_cycles = str(initial_dead)+"-"+str(last_dead)    
        return biomass_track, dead_cycles
    # Otherwise
    # ---------
    else:
        return biomass_track, "NoDeadTracking"

# -----------------------------------------------------------------------------
### FUNCTION dead_biomass_tracking
###############################################################################



###############################################################################
### FUNCTION EcoliPputidaOneConf ##############################################
def SelectConsortiumArchitecture(sucr1, frc2, nh4_Ec, nh4_KT, consortium_arch, initial_biomass,
                                 fitObj='MaxNaringenin', maxCycles = 240, dirPlot='', repeat=5, sd_cutoff = 0.1,
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
      
          fitObj: fitness function to optimize. In the current example, 'MaxNaringenin' - maximize Naringenin production by P. putida KT2440 (mM)
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
  # DIR: EcPp3_TemplateOptimizeConsortiumV0
  
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
    
  # DIR: EcPp3_TemplateOptimizeConsortiumV0
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
  # DIR: EcPp3_TemplateOptimizeConsortiumV0
  
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
  # DIR: EcPp3_TestTempV0

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
  
  # DIR: EcPp3_TestTempV0
  for i in range(repeat):
        
        # --------------------------------------------------------------------------
        # RUNNING COMETS + [R call] Run script to generate one graph:subprocess.call
        # DIR: EcPp3_TestTempV0
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
        subprocess.run(['../../Scripts/plot_biomassX2_vs_4mediaItem_glic_generalized.sh template2 sucr nar7glu fru nar nh4 pi o2 '+str(maxCycles)+' '+baseConfig+' blue black darkmagenta yellow orange aquamarine '+strains_string], shell=True)
            
        # ---------------------------------------------------------------------
        # INDEX REFERENCES IN COMETS FILE (organized in columns)
        # ---------------------------------------------------------------------
        # sucr  nar7glu  fru  nar  nh4  pi  o2  cycle_number  Biomass1  Biomass2  Biomass3  [...]
        # 0     1        2    3    4    5   6   7             8         9         10        11
        # ---------------------------------------------------------------------
        
        
        
        # ---------------------------------------------------------------------
        # COMPUTE METRICS FROM COMETS
        # DIR: EcPp3_TestTempV0
        # ---------------------------------------------------------------------
        with open("COMETS_"+baseConfig+"_"+suffix+".txt", "r") as sources:
            endCycle=0
            lines = sources.readlines()                                                            
            iniPointV=lines[0].split()  # Initial line, initial values (row_number) 
            
            # (1) INITIAL BIOMASS
            init_biomass = 0
            init_biomasses_dict = {}
            for n_strain in range(n_strains):
                # Initial biomass value for each microbe (individually)
                init_biomasses_dict[strains_list[n_strain]] = float(iniPointV[n_columns_without_biomass + n_strain])
                # (Global) initial biomass
                init_biomass += float(iniPointV[n_columns_without_biomass + n_strain])
            
            # (2) DETERMINE ENDCYCLE
            # Endcycle occurs when either sucrose or NH4 are exhausted. Otherwise, 'endcycle' = last cycle
            for line in lines:
                sucrConc=float(line.split()[0])
                NH4conc=float(line.split()[4])
                endCycle=int(line.split()[7])
                if float(sucrConc) < 0.001 or float(NH4conc) < 0.001:  # Nunca llega a ser exactamente 0.0, habría que poner < 0.001 (por ejemplo, pero es adaptable)
                    break;  # ¿Columna que registre cuál de ambos nutrientes se agota?
            
        # ENDCYCLE: Line where the 'endcycle' is reached. Either sucrConc = 0.0, either encycle = last_cycle
        finalLineV=lines[endCycle].split()
        
        
        # (3) FINAL CONCENTRATIONS: pCA, Nar, limiting nutrients
        tot_glicNar=float(finalLineV[1])  # Final glycosilated naringenin
        tot_Nar=float(finalLineV[3])  # Final Naringenin
        # NH4conc=float(line.split()[4])  # First limiting nutrient
        Final_pi=float(finalLineV[5])  # Second limiting nutrient
        Final_O2=round(float(finalLineV[6]), 4)  # Final O2
        
        
        # (4) FINAL BIOMASS
        total_final_biomass = 0
        final_biomasses_dict = {}
        deadTrack_indexes = []
        
        print()
        for n_strain in range(n_strains):
            # Final biomass value for each microbe (individually)
            final_biomasses_dict[strains_list[n_strain]] = float(finalLineV[n_columns_without_biomass + n_strain])
            print("New biomass value to add - ", strains_list[n_strain], ": ", float(finalLineV[n_columns_without_biomass + n_strain]))
            
            # (Global) final biomass 
            total_final_biomass += float(finalLineV[n_columns_without_biomass + n_strain])
            print("New final biomass: ", total_final_biomass)
            
            # Indexes for 'dead_biomass_tracking_unique' function
            deadTrack_indexes.append(n_columns_without_biomass + n_strain)
        print("Done with the checking")
        print()
        
        # (5) BIOMASS DEAD TRACKING function
        biomass_track, dead_process = dead_biomass_tracking_unique("COMETS_"+baseConfig+"_"+suffix+".txt", endCycle = endCycle, n_cycles = 10, biomass_indexes = deadTrack_indexes)
            
        # (6) Pi OVERCONSUMPTION TRACKING
        # pi_overconsumption, pi_cycles = metabolite_tracking_overconsumption("COMETS_"+baseConfig+"_"+suffix+".txt", 10.0, 9)  # Disabled utility
        
        # (7) COMPUTE FITNESS: maximize glycosilated naringenin
        fitNar = tot_glicNar / (total_final_biomass)  # Final glycosilated naringenin yield over GLOBAL biomass (all microorganisms in the consortium)
        # POTENTIAL REDEFINITION OF FITNESS
        fitness=fitNar
        
        # UPDATE REPEATS
        totfitness += fitness  # 'n' repeats
        fitnessList.append(fitness)  # List with fitness values in 'n' repeats
        sum_Nar += tot_Nar  # Total naringenin for 'n' repeats
        sum_glycNar += tot_glicNar  # Total glycosilated naringenin for 'n' repeats
        
        
        # ---------------------------------------------------------------------
        # PRINTING
        # ---------------------------------------------------------------------
        print("\nFitness(mM/gL): "+str(round(fitness,6))+" in cycle "+str(endCycle))
        print("Execution: "+str(i+1)+" of "+str(repeat)+". Final cycle: "+str(endCycle))
        print("Naringenin (mM): "+str(tot_Nar)+"\t"+"Glycosilated Nar (mM): "+str(tot_glicNar))
        # print("Biomass track checking: ", biomass_track, dead_process)
        for strain_key in final_biomasses_dict.keys():
            print("Final "+strain_key+" biomass (g/L): ", final_biomasses_dict[strain_key])

        
        # ---------------------------------------------------------------------
        # DIR: EcPp3_TestTempV0
        # ---------------------------------------------------------------------
        # Copy individual solution
        file='IndividualRunsResults/'+baseConfig+"_run"+str(i+1)+'_'+str(fitness)+'_'+str(endCycle)+'.pdf'
        shutil.move(baseConfig+"_"+suffix+"_plot.pdf", file)        
        if(dirPlot != ''):
            file2=dirPlot+baseConfig+'_run'+str(i+1)+'_'+str(fitness)+'_'+str(endCycle)+'.pdf'
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
  # DIR: EcPp3_TestTempV0
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
      myfile.write("endCycle\tNH4_mM\tpi_mM\tDeadTracking\tDT_cycles\tFinalSucr\tFinalO2\n")  
      
      # INFORMATION LINE
      myfile.write(fitObj+"\t"+baseConfig+"\t"+str(sucr1)+"\t"+str(frc2)+"\t"+str(nh4_Ec)+"\t"+str(nh4_KT)+"\t"+str(consortium_arch)+"\t")
     
      myfile.write(str(init_biomass)+"\t")
      for strain_key in init_biomasses_dict.keys():
          myfile.write(str(init_biomasses_dict[strain_key])+"\t")
                   
      myfile.write(str(total_final_biomass)+"\t")
      for strain_key in final_biomasses_dict.keys():
          myfile.write(str(final_biomasses_dict[strain_key])+"\t")
                   
      myfile.write(str(round(avgfitness, 6))+"\t"+str(round(sdfitness, 6))+"\t"+str(ID_SD)+"\t"+str(round(avgglycNar, 6))+"\t"+str(round(avgNar, 6))+"\t")
      myfile.write(str(endCycle)+"\t"+str(round(NH4conc, 4))+"\t"+str(round(Final_pi, 4))+"\t"+str(biomass_track)+"\t")
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
      myfile.write(str(endCycle)+"\t"+str(round(NH4conc, 4))+"\t"+str(round(Final_pi, 4))+"\t"+str(biomass_track)+"\t")
      myfile.write(str(dead_process)+"\t"+str(round(sucrConc, 4))+"\t"+str(Final_O2)+"\n")
                   
      myfile.close()
      
      
  return avgfitness, sdfitness, strains_list
# END OF FUNCTION: EcoliPputidaFLYCOP_selectConsortiumArchitecture
###############################################################################    
""" 
  # ---------------------------------------------------------------------------
  # SAVE RESULTS in TABLE: 'configurationsResults(...).txt' file
  # DIR: EcPp3_TestTempV0
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
      myfile.write(str(endCycle)+"\t"+str(round(NH4conc, 4))+"\t"+str(round(Final_pi, 4))+"\t"+str(biomass_track)+"\t")
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
      myfile.write(str(endCycle)+"\t"+str(round(NH4conc, 4))+"\t"+str(round(Final_pi, 4))+"\t"+str(biomass_track)+"\t")
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
      

  
  














