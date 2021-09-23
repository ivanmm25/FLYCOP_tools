#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 17 10:31:53 2021

# Author: Iván Martín Martín
# June 2021
"""

###############################################################################
# SCRIPT DESCRIPTION   
###############################################################################

"""
PIPELINE DESIGNED FOR SELECTION OF THE BEST ARCHITECTURE FOR A GIVEN CONSORTIUM
-------------------------------------------------------------------------------
In the current script, functions to initialize and update a given GEM model 
should be defined, so that they can be called from the function 'SelectConsortiumArchitecture'
in 'EcPp3_generalized.py'. Every GEM-model function should have two sections: 

    * 'INITIALIZE MODEL' section from xml file
    * 'UPDATE MODEL' section from mat file (where this mat file exists in advance)

Current series of initialize_update functions:
    
    - Initialize models:
        * "initialize_models_iEC1364_W_p_coumarate" function: basic E.coli W model (p-coumarate + fructose secretion)
        * "initialize_models_iEC1364_W_exc_metilator" function: E.coli W model for exclusive metilation
        * "initialize_models_iEC1364_W_unique_2saku" function: complex E.coli W model (p-coumarate + fructose secretion, metilation)
        * "initialize_models_iJN1463_narB12" function: basic P.putida KT2440 model
        
Aditionally, the function 'mat_to_comets' is contained here and executed within each of the initialize_update functions.


-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
IMPORTANT CONSIDERATIONS FOR DEFINING AN INITIALIZE_UPDATE GEM MODEL FUNCTION
-------------------------------------------------------------------------------

1. Please, copy and adapt the first 6 lines from any other function here, where 
the verification of the presence of the xml model in the expected folder is performed.

2. The INITIALIZE MODEL section in your function is only executed if the model does
not already exist in mat format; i.e. 

    if not os.path.exists('your_model_name_tmp.mat'):
        
  In the same section, perform:
      
      a. MODEL TRADUCTION (new to old COBRA version, since Docker uses old COBRA version)
      B. MODEL ADJUSTEMENTS
      
3. The UPDATE MODEL section in your function is only executed if the model does
not already exists in txt format; i.e.

    if not os.path.exists('your_model_name_tmp.mat.txt'):

4. Go back to the original_path at the end of your function.

"""
# -----------------------------------------------------------------------------


# MODULES
# -----------------------------------------------------------------------------
import os
import sys
import re
import collections
import shutil

import cobra
import cobra.flux_analysis.variability
from cobra import Reaction
from cobra import Metabolite
# -----------------------------------------------------------------------------


###############################################################################
###############################################################################
# FINAL MODEL SUMMARY, depending on the particular consortium architecture
# MUST BE IN DIR: {domainName}_TemplateOptimizeConsortiumVX/ModelsInput

def final_model_summary(strain_model):
    
  if not os.path.exists("optimal_model_summary.txt"):
      with open("optimal_model_summary.txt", "w") as model_sum:
          model = cobra.io.load_matlab_model(strain_model)
          model.optimize()
          model_sum.write("\nMODEL SUMMARY FOR "+strain_model)
          model_sum.write("\n--------------------------------------------------\n")
          model_sum.write(str(model.summary()) if not Exception else "Exception: model solution was not optimal")
          model_sum.write("\n\n")
          del(model)
      
  else:
      with open("optimal_model_summary.txt", "a") as model_sum:
          model = cobra.io.load_matlab_model(strain_model)
          model.optimize()
          model_sum.write("\nMODEL SUMMARY FOR "+strain_model)
          model_sum.write("\n--------------------------------------------------\n")
          model_sum.write(str(model.summary()) if not Exception else "Exception: model solution was not optimal")
          model_sum.write("\n\n")
          del(model)
          
###############################################################################
###############################################################################


###############################################################################
###############################################################################

# UTILITIES FOR PARSING AN EXTERNAL FILE WITH USER SPECIFICATIONS
# -----------------------------------------------------------------------------

"""
Parsing external file (file = configAnalysis_ratios.txt), defined as follows:

        - Header lines are not considered (those starting by '#'), they have just organizational purposes
        - NO blank spaces, comma as separator character except for the colon
        
        - FORMAT: dict_name:series_of_params
                * Name of a given key_name: series of parameters to be individually considered.
                * Each of these dictionary keys groups some related parameters.
                
        - RESULT: dictionary type
                
        EXAMPLE for configAnalysis_ratios.txt: 
            finalProducts_ratio:MetNar_mM,Nar_mM
            Cuptake_ratio:sucr_upt,frc_upt
"""
        
def parsing_external_file_to_dict(file):
    parameters_dict = collections.OrderedDict()
    with open(file, "r") as params_file:
            
        lines = params_file.readlines()
        for line in lines:
            
            if len(line) > 1 and line[0] != "#":  # Avoid header or empty lines
                line = line.strip("\n").split(":")
                parameters_dict[line[0]] = line[1].split(",")  # List of variable names

    return parameters_dict

###############################################################################
###############################################################################


###############################################################################
# FUNCTIONS to individually initialize GEM models   
###############################################################################


# Basic E.coli W model (p-coumarate + fructose secretion)
# Unable of metilation
# -----------------------------------------------------------------------------

def initialize_models_iEC1364_W_p_coumarate(sucr1, nh4_Ec, FVApCA, FVAfru, temporal_folder, models_summary):
 # Only to run 1st time, to build the model!
 if not(os.path.exists('ModelsInput/iEC1364_W_p_coumarate.xml')):
     print('ERROR! Not iEC1364_W_p_coumarate.xml file with GEM in ModelsInput!')
 else:
  path=os.getcwd()  # original path == "MicrobialCommunities/XXX_TemplateOptimizeConsortiumVX"
  os.chdir('ModelsInput')
  
  # ---------------------------------------------------------------------------
  # INITIALIZE MODEL
  # Only create the model in MAT format if it does not exist yet
  # ---------------------------------------------------------------------------
  
  if not os.path.exists('iEC1364_W_p_coumarate_tmp.mat'):
      # ---------------------------------------------------------------------------
      # E. coli W for taking sucrose and excreting fructose and T4hcinnm
      # ---------------------------------------------------------------------------
      model=cobra.io.read_sbml_model("iEC1364_W_p_coumarate.xml")
      
      # MODEL TRADUCTION
      # ================
      # Replace brackets with compartment location (e.g. "[c]") in metabolite ids by '_' (e.g. "_c") 
      for metabolite in model.metabolites:
        metabolite.id = re.sub('__91__c__93__',r'[c]',metabolite.id)
        metabolite.id = re.sub('__91__p__93__$',r'[p]',metabolite.id)
        metabolite.id = re.sub('__91__e__93__',r'[e]',metabolite.id)
        # metabolite.id = re.sub('__',r'_',metabolite.id)
        metabolite.compartment = ''
      # To solve possible problems in changing names     
      model.repair()
      cobra.io.save_matlab_model(model,"iEC1364_W_p_coumarate.mat")
      del(model)
      model = cobra.io.load_matlab_model("iEC1364_W_p_coumarate.mat")
      
      # Replace brackets with compartment location (e.g. "[c]") in rxn ids by '_' (e.g. "_c") 
      for rxn in model.reactions:
        rxn.id = re.sub('__40__p__41__',r'(p)',rxn.id)
        rxn.id = re.sub('__40__c__41__',r'(c)',rxn.id)
        rxn.id = re.sub('__40__e__41__',r'(e)',rxn.id)    
      # To solve possible problems in changing names     
      model.repair()
      cobra.io.save_matlab_model(model,"iEC1364_W_p_coumarate.mat")
      del(model)
      model = cobra.io.load_matlab_model("iEC1364_W_p_coumarate.mat")
      
      
      # MODEL ADJUSTEMENTS
      # ==================
      # Avoid glucose exchange (although there is no glucose in the original media)
      model.reactions.get_by_id("EX_glc__D(e)").bounds = (0,0)
      # Put sucrose as carbon source and maximize uptake, later changed by the parameter 'sucr1'
      model.reactions.get_by_id("EX_sucr(e)").bounds=(-15,0)
      # OXYGEN UPTAKE
      model.reactions.get_by_id("EX_o2(e)").bounds = (-20, 0)
      
      # NITROGEN UPTAKE
      # Uptake rate for NH4, later changed by NH4_Ec parameter
      model.reactions.get_by_id("EX_nh4(e)").bounds = (-15, 1000)
      # PHOSPHATE UPTAKE
      model.reactions.get_by_id("EX_pi(e)").bounds = (-10, 1000)  
      
      # MAKE SURE FRUCTOSE METABOLISM IS SHUTTED DOWN
      model.reactions.get_by_id("XYLI2").bounds = (0, 0)
      model.reactions.get_by_id("HEX7").bounds = (0, 0)  
      model.reactions.get_by_id("FRUpts2pp").bounds = (0, 0)
      model.reactions.get_by_id("FRUptspp").bounds = (0, 0)
      
      
      # ACTIVATED REACTION: FFSD: h2o[c] + suc6p[c] --> fru[c] + g6p[c] (sucrose hydrolysis)
      model.reactions.get_by_id("FFSD").bounds = (0, 1000)
      
      # To un-limit the fructose production, for the flux variability analysis
      model.reactions.get_by_id('FRUtpp').bounds=(-1000,1000)  
      model.reactions.get_by_id('FRUtex').bounds=(-1000,1000)  
      model.reactions.get_by_id('EX_fru(e)').bounds=(-1000,1000)
      
      # B12 auxotrophy: control / dependence with P.putida KT2440
      model.reactions.ADOCBLS.bounds=(0,0)
      
      # Optimize T4hcinnm production from tyrosine
      model.reactions.get_by_id('TAL').bounds=(0,1000)  # TAL: tyr_L[c] --> T4hcinnm[c] + nh4[c]
      
      # SAVE MODEL (tmp)
      cobra.io.save_matlab_model(model,"iEC1364_W_p_coumarate_tmp.mat")
      del(model)
      print("Model iEC1364_W_p_coumarate successfully initialized")
      
  # ---------------------------------------------------------------------------
  # UPDATE MODEL
  # Only create the model in txt from mat format if it does not exist yet
  # ---------------------------------------------------------------------------
    
  if not os.path.exists('iEC1364_W_p_coumarate_tmp.mat.txt'):
    # ========================================================================= 
    # MODEL ADAPTATION TO THE PARAMETERS PASSED TO THE 'SelectConsortiumArchitecture' function
    # E.coli W model: iEC1364_W_p_coumarate_tmp, specific to '3models' architecture
    # ========================================================================= 
    
    model=cobra.io.load_matlab_model('iEC1364_W_p_coumarate_tmp.mat')
    model.objective = "BIOMASS_Ec_iJO1366_WT_53p95M"  # WT, instead of 'core'
    
    # This reaction ('EX_sucr(e)') controls the global sucr exchange flux for E. coli W
    model.reactions.get_by_id("EX_sucr(e)").bounds=(sucr1, 0)
    # The rest of reactions depend on the sucr flux already specified
    model.reactions.get_by_id("SUCtpp").bounds=(0, 1000)  # sucr[p] --> sucr[c]  
    model.reactions.get_by_id("SUCRtpp").bounds=(0, 1000)  # sucr[p] --> sucr[c]
    model.reactions.get_by_id("SUCRtex").bounds=(0, 1000)  # sucr[e] --> sucr[p]
    model.optimize()
    
    # NH4 uptake rate
    model.reactions.get_by_id("EX_nh4(e)").bounds=(nh4_Ec, 0)

    
    # -------------------------------------------------------------------------
    # FLUX VARIABILITY ANALYSIS: pCA, fructose. 20% over global objective (optimize biomass production)
    dictOptValueFru = cobra.flux_analysis.flux_variability_analysis(model, {'EX_fru(e)'}, fraction_of_optimum=FVAfru)
    dictOptValuepCA = cobra.flux_analysis.flux_variability_analysis(model, {'EX_T4hcinnm(e)'}, fraction_of_optimum=(FVApCA))
   
    
    # FRUCTOSA
    # ======================
    FruExLimit=dictOptValueFru['EX_fru(e)']['maximum']
    model.reactions.get_by_id("FRUtpp").bounds=(0, FruExLimit)
    model.reactions.get_by_id("FRUtex").bounds=(-FruExLimit, 0)
    model.reactions.get_by_id("EX_fru(e)").bounds=(FruExLimit, FruExLimit)  
    
    
    # pCUMARATO
    # ======================
    pCALimit=dictOptValuepCA['EX_T4hcinnm(e)']['maximum']
    model.reactions.get_by_id('T4HCINNMtpp').bounds=(pCALimit,1000)
    model.reactions.get_by_id('T4HCINNMtex').bounds=(pCALimit,1000)
    model.reactions.get_by_id('EX_T4hcinnm(e)').bounds=(pCALimit,pCALimit)  
    
    
    cobra.io.save_matlab_model(model,'iEC1364_W_p_coumarate_tmp.mat')
    # -------------------------------------------------------------------------
    
    model.optimize()
    cobra.io.save_matlab_model(model,'iEC1364_W_p_coumarate_tmp.mat')
    del(model)                                
    print("Model iEC1364_W_p_coumarate successfully updated")    
    
    # MAT TO COMETS
    mat_to_comets('iEC1364_W_p_coumarate_tmp.mat')
    # =========================================================================
    # =========================================================================
      
  # Copy the txt model to temporal folder where COMETS is run
  shutil.copy("iEC1364_W_p_coumarate_tmp.mat.txt", temporal_folder)
  
  # MODEL SUMMARY
  if models_summary: final_model_summary('iEC1364_W_p_coumarate_tmp.mat')
  
  # BACK TO 'Microbial Communities' folder 
  os.chdir(path)
  # ---------------------------------------------------------------------------
  # END OF INITIALIZE FUNCTION


###############################################################################
###############################################################################
  

# E.coli W model adapted for metilation
# Does not secrete fructose
# -----------------------------------------------------------------------------

def initialize_models_iEC1364_W_exc_metilator(sucr1, nh4_Ec, FVAMetNar, temporal_folder, models_summary):
 # Only to run 1st time, to build the model!
 if not(os.path.exists('ModelsInput/iEC1364_W_unique_saku2.xml')):
     print('ERROR! Not iEC1364_W_unique_saku2.xml file with GEM in ModelsInput!')
 else:
  path=os.getcwd()  # original path == "MicrobialCommunities"
  os.chdir('ModelsInput')
  
  # ---------------------------------------------------------------------------
  # INITIALIZE MODEL
  # Only create the model in MAT format if it does not exist yet
  # ---------------------------------------------------------------------------
  
  if not os.path.exists('iEC1364_W_exc_metilator_tmp.mat'):
      # ---------------------------------------------------------------------------
      # E. coli W for metilating naringenin
      # ---------------------------------------------------------------------------
      model=cobra.io.read_sbml_model("iEC1364_W_unique_saku2.xml")
      
      # MODEL TRADUCTION
      # ================
      # Replace brackets with compartment location (e.g. "[c]") in metabolite ids by '_' (e.g. "_c") 
      for metabolite in model.metabolites:
        metabolite.id = re.sub('__91__c__93__',r'[c]',metabolite.id)
        metabolite.id = re.sub('__91__p__93__$',r'[p]',metabolite.id)
        metabolite.id = re.sub('__91__e__93__',r'[e]',metabolite.id)
        # metabolite.id = re.sub('__',r'_',metabolite.id)
        metabolite.compartment = ''
      # To solve possible problems in changing names     
      model.repair()
      cobra.io.save_matlab_model(model,"iEC1364_W_exc_metilator.mat")
      del(model)
      model = cobra.io.load_matlab_model("iEC1364_W_exc_metilator.mat")
      
      # Replace brackets with compartment location (e.g. "[c]") in rxn ids by '_' (e.g. "_c") 
      for rxn in model.reactions:
        rxn.id = re.sub('__40__p__41__',r'(p)',rxn.id)
        rxn.id = re.sub('__40__c__41__',r'(c)',rxn.id)
        rxn.id = re.sub('__40__e__41__',r'(e)',rxn.id)    
      # To solve possible problems in changing names     
      model.repair()
      cobra.io.save_matlab_model(model,"iEC1364_W_exc_metilator.mat")
      del(model)
      model = cobra.io.load_matlab_model("iEC1364_W_exc_metilator.mat")
      
      
      # MODEL ADJUSTEMENTS
      # ==================
      # Avoid glucose exchange (although there is no glucose in the original media)
      model.reactions.get_by_id("EX_glc__D(e)").bounds = (0, 0)
      # Put sucrose as carbon source and maximize uptake, later changed by the parameter 'sucr1'
      model.reactions.get_by_id("EX_sucr(e)").bounds=(-15,0)
      # OXYGEN UPTAKE
      model.reactions.get_by_id("EX_o2(e)").bounds = (-20, 0)
      
      # NITROGEN UPTAKE
      # Uptake rate for NH4, later changed by NH4_Ec parameter
      model.reactions.get_by_id("EX_nh4(e)").bounds = (-15, 1000)
      # PHOSPHATE UPTAKE
      model.reactions.get_by_id("EX_pi(e)").bounds = (-10, 1000)  
      
      # FRUCTOSE METABOLISM IS ACTIVATED AGAIN FOR THE GLYCOSILATOR STRAIN E. coli W 
      model.reactions.get_by_id("XYLI2").bounds = (0, 0)  # AVOID: XYLI2: glc_D[c] <=> fru[c] (we want just fructose metabolism)
      
      model.reactions.get_by_id("HEX7").bounds = (-1000, 1000)  # HEX7: atp[c] + fru[c] <=> adp[c] + f6p[c] + h[c]
      model.reactions.get_by_id("FRUpts2pp").bounds = (-1000, 1000)  # FRUpts2pp: fru[p] + pep[c] <=> f6p[c] + pyr[c]
      model.reactions.get_by_id("FRUptspp").bounds = (-1000, 1000)  # FRUptspp: fru[p] + pep[c] <=> f1p[c] + pyr[c]
      
      # ACTIVATED REACTION: FFSD: h2o[c] + suc6p[c] --> fru[c] + g6p[c] (sucrose hydrolysis)
      model.reactions.get_by_id("FFSD").bounds = (0, 1000)
      
      # AVOID FRUCTOSE SECRETION
      model.reactions.get_by_id('FRUtpp').bounds=(0,0)  
      model.reactions.get_by_id('FRUtex').bounds=(0,0)  
      model.reactions.get_by_id('EX_fru(e)').bounds=(0,0)
      
      # B12 auxotrophy: control / dependence with P.putida KT2440
      model.reactions.ADOCBLS.bounds=(0,0)
      
      # SHUT DOWN T4hcinnm METABOLISM
      model.reactions.get_by_id('TAL').bounds=(0,0)  # TAL: tyr_L[c] --> T4hcinnm[c] + nh4[c]
      model.reactions.get_by_id('T4HCINNMtpp').bounds=(0,0)  # T4HCINNMtpp:  T4hcinnm[c] --> T4hcinnm[p]
      model.reactions.get_by_id('T4HCINNMtex').bounds=(0,0)  # T4HCINNMtex:  T4hcinnm[p] --> T4hcinnm[e]
      model.reactions.get_by_id('EX_T4hcinnm(e)').bounds=(0,0)  # EX_T4hcinnm(e):  T4hcinnm[e] --> 
      
      # NARINGENIN RELATED-REACTIONS
      # ----------------------------
      # Naringenin uptake by E.coli
      model.reactions.get_by_id("naringenintpp").bounds = (-1000, 0)  # naringenintpp: nar[c] <-- nar[p]
      model.reactions.get_by_id("naringenintex").bounds = (-1000, 0)  # naringenintex: nar[p] <-- nar[e]
      model.reactions.get_by_id("EX_nar(e)").bounds = (-1000, 0)  # EX_nar(e): nar[e] <--
    
      # Naringenin metilation
      model.reactions.get_by_id("DE_N7OMT_FR").bounds = (0, 1000)  # DE_N7OMT_FR: amet[c] + nar[c] --> 2saku[c] + ahcys[c] + h[c]
    
      # Met-Naringenin export, previous to FVA
      model.reactions.get_by_id("2saku_tpp").bounds = (0, 1000)  # 2saku_tpp: 2saku[c] --> 2saku[p]
      model.reactions.get_by_id("2saku_tex").bounds = (0, 1000)  # 2saku_tex: 2saku[p] --> 2saku[e]
      
      # SAVE MODEL (tmp)
      cobra.io.save_matlab_model(model,"iEC1364_W_exc_metilator_tmp.mat")
      del(model)
      print("Model iEC1364_W_exc_metilator successfully initialized")
      
  # ---------------------------------------------------------------------------
  # UPDATE MODEL
  # Only create the model in txt from mat format if it does not exist yet
  # ---------------------------------------------------------------------------
    
  if not os.path.exists('iEC1364_W_exc_metilator_tmp.mat.txt'):
    # =========================================================================
    # MODEL ADAPTATION TO THE PARAMETERS PASSED TO THE 'SelectConsortiumArchitecture' function
    # E.coli W model: iEC1364_W_exc_metilator_tmp, specific to '3models' architecture
    # =========================================================================
    
    model=cobra.io.load_matlab_model('iEC1364_W_exc_metilator_tmp.mat')
    model.objective = "BIOMASS_Ec_iJO1366_WT_53p95M"  # WT, instead of 'core'
    
    # This reaction ('EX_sucr(e)') controls the global sucr exchange flux for E. coli W
    model.reactions.get_by_id("EX_sucr(e)").bounds=(sucr1, 0)
    # The rest of reactions depend on the sucr flux already specified
    model.reactions.get_by_id("SUCtpp").bounds=(0, 1000)  # sucr[p] --> sucr[c]  
    model.reactions.get_by_id("SUCRtpp").bounds=(0, 1000)  # sucr[p] --> sucr[c]
    model.reactions.get_by_id("SUCRtex").bounds=(0, 1000)  # sucr[e] --> sucr[p]
    model.optimize()
    
    # NH4 uptake rate
    model.reactions.get_by_id("EX_nh4(e)").bounds=(nh4_Ec, 0)

    
    # -------------------------------------------------------------------------
    # FLUX VARIABILITY ANALYSIS: metilated naringenin. 20% over global objective (optimize biomass production)
    dictOptValuemetnar = cobra.flux_analysis.flux_variability_analysis(model, {'EX_2saku(e)'}, fraction_of_optimum=(FVAMetNar))
   
    # Glycosilated naringenin
    # =======================
    MetNarLimit=dictOptValuemetnar['EX_2saku(e)']['maximum']
    model.reactions.get_by_id("2saku_tpp").bounds=(MetNarLimit, 1000)  
    model.reactions.get_by_id("2saku_tex").bounds=(MetNarLimit, 1000)  
    model.reactions.get_by_id("EX_2saku(e)").bounds=(MetNarLimit, MetNarLimit)  
    
    
    cobra.io.save_matlab_model(model,'iEC1364_W_exc_metilator_tmp.mat')
    # -------------------------------------------------------------------------
    
    model.optimize()
    cobra.io.save_matlab_model(model,'iEC1364_W_exc_metilator_tmp.mat')
    del(model)                                    
    print("Model iEC1364_W_exc_metilator successfully updated")
    
    # MAT TO COMETS
    mat_to_comets('iEC1364_W_exc_metilator_tmp.mat')
    # =========================================================================
    # =========================================================================
  
  # Copy the txt model to temporal folder where COMETS is run
  shutil.copy("iEC1364_W_exc_metilator_tmp.mat.txt", temporal_folder)
  
  # MODEL SUMMARY
  if models_summary: final_model_summary('iEC1364_W_exc_metilator_tmp.mat')
  
  # BACK TO 'Microbial Communities' folder  
  os.chdir(path)
  # ---------------------------------------------------------------------------
  # END OF INITIALIZE FUNCTION


###############################################################################
###############################################################################


# E.coli W model (p-coumarate + fructose secretion)
# Also metilator strain
# -----------------------------------------------------------------------------

def initialize_models_iEC1364_W_unique_saku2(sucr1, nh4_Ec, FVApCA, FVAfru, FVAMetNar, temporal_folder, models_summary):
 # Only to run 1st time, to build the model!
 if not(os.path.exists('ModelsInput/iEC1364_W_unique_saku2.xml')):
     print('ERROR! Not iEC1364_W_unique_saku2.xml file with GEM in ModelsInput!')
 else:
  path=os.getcwd()  # original path == "MicrobialCommunities"
  os.chdir('ModelsInput')
  
  # ---------------------------------------------------------------------------
  # INITIALIZE MODEL
  # Only create the model in MAT format if it does not exist yet
  # ---------------------------------------------------------------------------
  
  if not os.path.exists('iEC1364_W_unique_saku2_tmp.mat'):
      # ---------------------------------------------------------------------------
      # E. coli W for taking sucrose and excreting fructose
      # ---------------------------------------------------------------------------
      model=cobra.io.read_sbml_model("iEC1364_W_unique_saku2.xml")
      
      # MODEL TRADUCTION
      # ================
      # Replace brackets with compartment location (e.g. "[c]") in metabolite ids by '_' (e.g. "_c") 
      for metabolite in model.metabolites:
        metabolite.id = re.sub('__91__c__93__',r'[c]',metabolite.id)
        metabolite.id = re.sub('__91__p__93__$',r'[p]',metabolite.id)
        metabolite.id = re.sub('__91__e__93__',r'[e]',metabolite.id)
        # metabolite.id = re.sub('__',r'_',metabolite.id)
        metabolite.compartment = ''
      # To solve possible problems in changing names     
      model.repair()
      cobra.io.save_matlab_model(model,"iEC1364_W_unique_saku2.mat")
      del(model)
      model = cobra.io.load_matlab_model("iEC1364_W_unique_saku2.mat")
      
      # Replace brackets with compartment location (e.g. "[c]") in rxn ids by '_' (e.g. "_c") 
      for rxn in model.reactions:
        rxn.id = re.sub('__40__p__41__',r'(p)',rxn.id)
        rxn.id = re.sub('__40__c__41__',r'(c)',rxn.id)
        rxn.id = re.sub('__40__e__41__',r'(e)',rxn.id)    
      # To solve possible problems in changing names     
      model.repair()
      cobra.io.save_matlab_model(model,"iEC1364_W_unique_saku2.mat")
      del(model)
      model = cobra.io.load_matlab_model("iEC1364_W_unique_saku2.mat")
      
      # MODEL ADJUSTEMENTS
      # ==================
      # Put sucrose as carbon source and maximize uptake, later changed by the parameter 'sucr1'
      model.reactions.get_by_id("EX_sucr(e)").bounds=(-15,0)
      # OXYGEN UPTAKE
      model.reactions.get_by_id("EX_o2(e)").bounds = (-20, 0)
      # Avoid glucose exchange
      model.reactions.get_by_id("EX_glc__D(e)").bounds = (0,0)
      
      # NITROGEN UPTAKE
      # Uptake rate for NH4, later changed by NH4_Ec parameter
      model.reactions.get_by_id("EX_nh4(e)").bounds = (-15, 1000)
      # PHOSPHATE UPTAKE
      model.reactions.get_by_id("EX_pi(e)").bounds = (-10, 1000)  
      
      # MAKE SURE FRUCTOSE METABOLISM IS SHUTTED DOWN
      model.reactions.get_by_id("XYLI2").bounds = (0, 0)
      model.reactions.get_by_id("HEX7").bounds = (0, 0)  
      model.reactions.get_by_id("FRUpts2pp").bounds = (0, 0)
      model.reactions.get_by_id("FRUptspp").bounds = (0, 0)
      
      
      # ACTIVATED REACTION: FFSD: h2o[c] + suc6p[c] --> fru[c] + g6p[c]
      model.reactions.get_by_id("FFSD").bounds = (0, 1000)
      
      # To un-limit the fructose production, for the flux variability analysis
      model.reactions.get_by_id('FRUtpp').bounds=(-1000,1000)  
      model.reactions.get_by_id('FRUtex').bounds=(-1000,1000)  
      
      # model.reactions.FRUtex.bounds=(0,0)  # to be used in case of a second E.coli model for naringenin modification (without fructose secretion)
      model.reactions.get_by_id('EX_fru(e)').bounds=(-1000,1000)
      
      # Optimize T4hcinnm production from tyrosine
      model.reactions.get_by_id('TAL').bounds=(0,1000)  # TAL: tyr_L[c] --> T4hcinnm[c] + nh4[c]
      
      # B12 auxotrophy: control / dependence with P.putida KT2440
      model.reactions.ADOCBLS.bounds=(0,0)
      
      
      # NARINGENIN RELATED-REACTIONS
      # ----------------------------
      # Naringenin uptake by E.coli
      model.reactions.get_by_id("naringenintex").bounds = (-1000, 0)  # naringenintex: nar[p] <-- nar[e]
      model.reactions.get_by_id("naringenintpp").bounds = (-1000, 0)  # naringenintpp: nar[c] <-- nar[p]
      model.reactions.get_by_id("EX_nar(e)").bounds = (-1000, 0)  # EX_nar(e): nar[e] <--
    
      # Naringenin metilation
      model.reactions.get_by_id("DE_N7OMT_FR").bounds = (0, 1000)  # DE_N7OMT_FR: amet[c] + nar[c] --> 2saku[c] + ahcys[c] + h[c]
    
      # Met-Naringenin export, previous to FVA
      model.reactions.get_by_id("2saku_tpp").bounds = (0, 1000)  # 2saku_tpp: 2saku[c] --> 2saku[p]
      model.reactions.get_by_id("2saku_tex").bounds = (0, 1000)  # 2saku_tex: 2saku[p] --> 2saku[e]
      
      # SAVE MODEL (tmp)
      cobra.io.save_matlab_model(model,"iEC1364_W_unique_saku2_tmp.mat")
      del(model)
      print("Model iEC1364_W_unique_saku2 successfully initialized")
      
  
  # ---------------------------------------------------------------------------
  # UPDATE MODEL
  # Only create the model in txt from mat format if it does not exist yet
  # ---------------------------------------------------------------------------
  
  if not os.path.exists('iEC1364_W_unique_saku2_tmp.mat.txt'):
    # ========================================================================= 
    # MODEL ADAPTATION TO THE PARAMETERS PASSED TO THE 'SelectConsortiumArchitecture' function
    # E.coli W model: iEC1364_W_unique_saku2_tmp, specific to '2models' architecture
    # ========================================================================= 
    
    model=cobra.io.load_matlab_model('iEC1364_W_unique_saku2_tmp.mat')
    model.objective = "BIOMASS_Ec_iJO1366_WT_53p95M"  # WT, en lugar de 'core'
    
    # This reaction ('EX_sucr(e)') controls the global sucr exchange flux for E. coli
    model.reactions.get_by_id("EX_sucr(e)").bounds=(sucr1, 0)
    # The rest of reactions depend on the sucr flux already specified
    model.reactions.get_by_id("SUCtpp").bounds=(0, 1000)  # sucr[p] --> sucr[c]  
    model.reactions.get_by_id("SUCRtpp").bounds=(0, 1000)  # sucr[p] --> sucr[c]
    model.reactions.get_by_id("SUCRtex").bounds=(0, 1000)  # sucr[e] --> sucr[p]
    model.optimize()
    
    # NH4 uptake rate
    model.reactions.get_by_id("EX_nh4(e)").bounds=(nh4_Ec, 0)

    
    # -------------------------------------------------------------------------
    # FLUX VARIABILITY ANALYSIS: pCA, fructose, metylated naringenin. 20% over global objective (optimize biomass production)
    dictOptValuepCA = cobra.flux_analysis.flux_variability_analysis(model, {'EX_T4hcinnm(e)'}, fraction_of_optimum=(FVApCA))
    dictOptValueFru = cobra.flux_analysis.flux_variability_analysis(model, {'EX_fru(e)'}, fraction_of_optimum=FVAfru)
    dictOptValuemetnar = cobra.flux_analysis.flux_variability_analysis(model, {'EX_2saku(e)'}, fraction_of_optimum=(FVAMetNar))
   
    
    # FRUCTOSE
    # ======================
    FruExLimit=dictOptValueFru['EX_fru(e)']['maximum']
    model.reactions.get_by_id("FRUtpp").bounds=(0, FruExLimit)
    model.reactions.get_by_id("FRUtex").bounds=(-FruExLimit, 0)
    model.reactions.get_by_id("EX_fru(e)").bounds=(FruExLimit, FruExLimit)  
    
    
    # p-COUMARATE
    # ======================
    pCALimit=dictOptValuepCA['EX_T4hcinnm(e)']['maximum']
    model.reactions.get_by_id('T4HCINNMtpp').bounds=(pCALimit,1000)
    model.reactions.get_by_id('T4HCINNMtex').bounds=(pCALimit,1000)
    model.reactions.get_by_id('EX_T4hcinnm(e)').bounds=(pCALimit,pCALimit)  
    
    
    # Metilated naringenin
    # =======================
    MetNarLimit=dictOptValuemetnar['EX_2saku(e)']['maximum']
    model.reactions.get_by_id("2saku_tpp").bounds=(MetNarLimit, 1000)  
    model.reactions.get_by_id("2saku_tex").bounds=(MetNarLimit, 1000)  
    model.reactions.get_by_id("EX_2saku(e)").bounds=(MetNarLimit, MetNarLimit)  
    
    
    cobra.io.save_matlab_model(model,'iEC1364_W_unique_saku2_tmp.mat')
    # -------------------------------------------------------------------------
    
    model.optimize()
    cobra.io.save_matlab_model(model,'iEC1364_W_unique_saku2_tmp.mat')
    del(model)           
    print("Model iEC1364_W_unique_saku2 successfully updated")   
                  
    # MAT TO COMETS
    mat_to_comets('iEC1364_W_unique_saku2_tmp.mat')
    # =========================================================================
    # =========================================================================
    
  # Copy the txt model to temporal folder where COMETS is run
  shutil.copy("iEC1364_W_unique_saku2_tmp.mat.txt", temporal_folder)
  
  # MODEL SUMMARY
  if models_summary: final_model_summary('iEC1364_W_unique_saku2_tmp.mat')
  
  # BACK TO 'Microbial Communities' folder  
  os.chdir(path)
  # ---------------------------------------------------------------------------
  # END OF INITIALIZE FUNCTION
    

###############################################################################
###############################################################################


# P.putida KT2440 (malon + naringenin production)
# Also B12 vitamin production
# -----------------------------------------------------------------------------

def initialize_models_iJN1463_narB12(frc2, nh4_KT, FVANar, temporal_folder, models_summary):
 # Only to run 1st time, to build the model!
 if not(os.path.exists('ModelsInput/iJN1463_naringeninB12.xml')):
     print('ERROR! Not iJN1463_naringeninB12.xml file with GEM in ModelsInput!')
 else:
  path=os.getcwd()  # original path == "MicrobialCommunities"
  os.chdir('ModelsInput')
  
  # ---------------------------------------------------------------------------
  # INITIALIZE MODEL
  # Only create the model in MAT format if it does not exist yet
  # ---------------------------------------------------------------------------
  
  if not os.path.exists('iJN1463_naringeninB12_tmp.mat'):
      # ---------------------------------------------------------------------------
      # P.putida KT2440 model for taking fructose and secreting B12
      # ---------------------------------------------------------------------------
      model=cobra.io.read_sbml_model('iJN1463_naringeninB12.xml')
    
      # MODEL TRADUCTION
      # ================
      # Replace brackets with compartment location (e.g. "[c]") in metabolite ids by '_' (e.g. "_c") 
      for metabolite in model.metabolites:
        metabolite.id = re.sub('__91__c__93__',r'[c]',metabolite.id)
        metabolite.id = re.sub('__91__p__93__$',r'[p]',metabolite.id)
        metabolite.id = re.sub('__91__e__93__',r'[e]',metabolite.id)
        # metabolite.id = re.sub('__',r'_',metabolite.id)
        metabolite.compartment = ''
      # To solve possible problems in changing names     
      model.repair()
      cobra.io.save_matlab_model(model,"iJN1463_naringeninB12.mat")
      del(model)
      model=cobra.io.load_matlab_model('iJN1463_naringeninB12.mat') 
      
      # Replace brackets with compartment location (e.g. "[c]") in rxn ids by '_' (e.g. "_c") 
      for rxn in model.reactions:
        rxn.id = re.sub('__40__p__41__',r'(p)',rxn.id)
        rxn.id = re.sub('__40__c__41__',r'(c)',rxn.id)
        rxn.id = re.sub('__40__e__41__',r'(e)',rxn.id)    
      # To solve possible problems in changing names     
      model.repair()
      cobra.io.save_matlab_model(model,"iJN1463_naringeninB12.mat")
      del(model)
      model=cobra.io.load_matlab_model('iJN1463_naringeninB12.mat') 
      
      
      # MODEL ADJUSTEMENTS
      # ==================
      # This model cannot take sucrose from media: model.reactions.get_by_id("EX_sucr(e)").bounds = (0, 0)  
      
      # FRU reactions
      model.reactions.get_by_id("EX_fru(e)").bounds=(-15,0)  # Maximize uptake, maximum upper bound. Later changed by the parameter 'frc2'
      model.reactions.get_by_id("FRUtex").bounds = (0, 1000)
    
      # PREVENT P.putidaKT FROM TAKING glc[e] from the media
      model.reactions.get_by_id("EX_glc__D(e)").bounds = (0, 0)
      # OXYGEN UPTAKE
      model.reactions.get_by_id("EX_o2(e)").bounds = (-20, 0)
      
      # NITROGEN UPTAKE
      model.reactions.get_by_id("EX_nh4(e)").bounds = (-12, 1000)  # Later changed by NH4_KT parameter 
      # PHOSPHATE UPTAKE 
      model.reactions.get_by_id("EX_pi(e)").bounds = (-10, 1000)
      
      # pCOUMARATE UPTAKE
      model.reactions.get_by_id("EX_T4hcinnm(e)").bounds = (-1000, 0)
      model.reactions.get_by_id("T4HCINNMtex").bounds = (0, 1000)
      model.reactions.get_by_id("T4HCINNMtpp").bounds = (0, 1000)
      model.reactions.get_by_id("4CMCOAS").bounds = (0, 0)  # T4hcinnm[c] + atp[c] + coa[c] --> amp[c] + coucoa[c] + ppi[c]
      
      # MALON reactions - no MALON secretion
      model.reactions.get_by_id("EX_malon(e)").bounds = (0, 0)
      model.reactions.get_by_id("MALONtex").bounds = (0, 0)
      model.reactions.get_by_id("MALONpp").bounds = (0, 0)
      model.reactions.get_by_id("MALONHY").bounds = (0, 0)  # Reacción de hidrólisis de malcoa[c] --> malon[c]
            
      # NARINGENIN PRODUCTION reactions - optimize production
      model.reactions.get_by_id("matB").bounds = (0, 1000)
      model.reactions.get_by_id("AS_C_4CMCOAS_FR").bounds = (0, 1000)
      model.reactions.get_by_id("AS_C_CHALS1_FR").bounds = (0, 1000)
      model.reactions.get_by_id("AS_CHALIS1_FR").bounds = (0, 1000)
      
      # PROMOTE NARINGENIN SECRETION 
      # -------------------------------------------------------------------------
      model.reactions.get_by_id("EX_nar(e)").bounds = (0, 1000)  # EX_nar(e): nar[e] -->
      model.reactions.get_by_id("naringenintex").bounds = (0, 1000)  # naringenintex: nar[p] --> nar[e]
      model.reactions.get_by_id("naringenintpp").bounds = (0, 1000)  # naringenintpp: nar[c] --> nar[p]
      
      # SAVE MODEL (tmp)
      cobra.io.save_matlab_model(model,"iJN1463_naringeninB12_tmp.mat")
      del(model)
      print("Model initialize_models_iJN1463_narB12 successfully initialized")
      
  # ---------------------------------------------------------------------------
  # UPDATE MODEL
  # Only create the model in txt from mat format if it does not exist yet
  # ---------------------------------------------------------------------------
  
  if not os.path.exists('iJN1463_naringeninB12_tmp.mat.txt'):
    # =========================================================================
    # MODEL ADAPTATION TO THE PARAMETERS PASSED TO THE 'SelectConsortiumArchitecture' function
    # P.putida KT2440 model: iJN1463_naringeninB12_tmp
    # =========================================================================
    
    model=cobra.io.load_matlab_model('iJN1463_naringeninB12_tmp.mat')
    model.objective = "BIOMASS_KT2440_WT3"  # WT, en lugar de 'core'  - asegurar objetivo biomasa (clave)
    
    # This reaction ('EX_fru(e)') controls the global fru exchange flux for P. putida KT
    model.reactions.get_by_id("EX_fru(e)").bounds=(frc2, 0)
    # The rest of reactions depend on the 'fru' flux already specified
    model.reactions.get_by_id("FRUtex").bounds=(0, 1000)   # fru[e] --> fru[p]
    model.reactions.get_by_id("FRUptspp").bounds=(0, 1000)   # fru[p] + pep[c] --> f1p[c] + pyr[c]
    model.optimize()
    
    # NH4 uptake rate
    model.reactions.get_by_id("EX_nh4(e)").bounds=(nh4_KT, 0)

    
    # -------------------------------------------------------------------------
    # FLUX VARIABILITY ANALYSIS: naringenin. 20% over global objective (optimize biomass production)
    dictNarValue=cobra.flux_analysis.variability.flux_variability_analysis(model,{'EX_nar(e)'},fraction_of_optimum=FVANar)
    NarLimit=dictNarValue['EX_nar(e)']['maximum']
    
    model.reactions.get_by_id('matB').bounds=(0, NarLimit)
    model.reactions.get_by_id('naringenintpp').bounds=(NarLimit,1000)
    model.reactions.get_by_id('naringenintex').bounds=(NarLimit,1000)
    model.reactions.get_by_id('EX_nar(e)').bounds=(NarLimit,NarLimit)
    # -------------------------------------------------------------------------
    
    model.optimize()
    cobra.io.save_matlab_model(model,'iJN1463_naringeninB12_tmp.mat')
    del(model)
    print("Model initialize_models_iJN1463_narB12 successfully updated")
    
    # MAT TO COMETS
    mat_to_comets('iJN1463_naringeninB12_tmp.mat')
    # =========================================================================
    # =========================================================================
  
  # Copy the txt model to temporal folder where COMETS is run
  shutil.copy("iJN1463_naringeninB12_tmp.mat.txt", temporal_folder)
  
  # MODEL SUMMARY
  if models_summary: final_model_summary('iJN1463_naringeninB12_tmp.mat')
  
  # BACK TO 'Microbial Communities' folder  
  os.chdir(path)
  # ---------------------------------------------------------------------------
  # END OF INITIALIZE FUNCTION
    
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
###############################################################################



###############################################################################   
### FUNCTION mat_to_comets ####################################################    
# mat_to_comets(modelPath)
def mat_to_comets(matInputFile):
    model=cobra.io.load_matlab_model(matInputFile)
    # Open output file:
    with open(matInputFile+'.txt', mode='w') as f:
        # Print the S matrix
        f.write("SMATRIX  "+str(len(model.metabolites))+"  "+str(len(model.reactions))+"\n")
        for x in range(len(model.metabolites)):
            for y in range(len(model.reactions)):
                if (model.metabolites[x] in model.reactions[y].metabolites):
                    coeff=model.reactions[y].get_coefficient(model.metabolites[x])
                    f.write("    "+str(x+1)+"   "+str(y+1)+"   "+str(coeff)+"\n")
        f.write("//\n")
        
        # Print the bounds
        f.write("BOUNDS  -1000  1000\n");
        for y in range(len(model.reactions)):
            lb=model.reactions[y].lower_bound
            up=model.reactions[y].upper_bound
            f.write("    "+str(y+1)+"   "+str(lb)+"   "+str(up)+"\n")
        f.write("//\n")
        
        # Print the objective reaction
        f.write('OBJECTIVE\n')
        for y in range(len(model.reactions)):
            if (model.reactions[y] in model.objective):   # Cambio línea ejecución Docker
            # if (str(model.reactions[y].id) in str(model.objective.expression)):  # Cambio línea ejecución MiOrdenador
                indexObj=y+1
        f.write("    "+str(indexObj)+"\n")
        f.write("//\n")
        
        # Print metabolite names
        f.write("METABOLITE_NAMES\n")
        for x in range(len(model.metabolites)):
            f.write("    "+model.metabolites[x].id+"\n")
        f.write("//\n")

        # Print reaction names
        f.write("REACTION_NAMES\n")
        for y in range(len(model.reactions)):
            f.write("    "+model.reactions[y].id+"\n")
        f.write("//\n")

        # Print exchange reactions
        f.write("EXCHANGE_REACTIONS\n")
        for y in range(len(model.reactions)):
            if (model.reactions[y].id.find('EX_')==0):
                f.write(" "+str(y+1))
        f.write("\n//\n")            
    del(model)
### end-function-mat_to_comets    
###############################################################################












