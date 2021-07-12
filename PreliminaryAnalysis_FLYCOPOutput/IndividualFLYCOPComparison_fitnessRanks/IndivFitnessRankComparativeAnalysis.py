#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 27 23:02:18 2020

@author: Iván Martín Martín


DESCRIPTION - INPUT PARAMETER COMPARISON BETWEEN DIFFERENT FITNESS RANKS

    Comparative Statistical Analysis for different fitness ranks within the same FLYCOP run.
    These ranks are compared between them. Input Parameters evaluated are (current script):
        - Uptake Rates ratio
        - Initial Biomass ratio
        - (...)
    
EXPECTED INPUT

    For the FLYCOP run to be considered in the Comparative Analysis: 
        - 'dataTable_AcceptedRatios_SDlt.xlsx' from "InputParametersAnalysis.py" script
        - Other suitable excel or configs file
        
OUTPUT

    Folder: ./ComparativeAnalysisPlots
        "UptakeRatesRatio_Boxplot.png"
        "UptakeRatesRatio_Boxplot_AxisReduced.png"
        
        "InitBiomassRatio_Boxplot.png"
        "InitBiomassRatio_Boxplot_Boxplot_AxisReduced.png"
    
NOTE THAT:
    
    The order of the fitness_ranks_set should be: higher to lower rank; (lower_bound, upper_bound).
    
    The variables to be displayed and the fitness ranks to be analyzed can be adapted if desired.
        (CHANGE keyword)
    
"""

# import re
import pandas as pd
import os.path
import seaborn as sns

scripts_path = os.getcwd()
os.chdir("../Utilities")
from FitnessRanks import organize_fitness_ranks
import Plotting as myplt

os.chdir(scripts_path)
path = "../../Project3_EcPp2_LimNut_M9/Nitrogen/M9200N"  # CHANGE path
original_path = os.getcwd()

# -----------------------------------------------------------------------------
# CLASSIFICATION OF FITNESS RANKS AS DISCRETE VARIABLES (-1, 0, ..., n); with n = number of fitness ranks
# (-1): fitness rank with 'ZeroDivisionError' configurations; (0): fitness rank with SDexcessive configurations (no 'ZeroDivisionError')
# -----------------------------------------------------------------------------

path1 = "../../Project3_EcPp2_LimNut_M9/NP_LimNutFinal_29Mar/NP3"
os.chdir(path1)
dataTable = pd.read_excel("configurationsResults_Scenario0_acceptableBiomassLoss_analysis.xlsx", sheet_name="Product_ratios", engine="openpyxl")

# NEW ORGANIZED DATAFRAME
# -----------------------------------------------------------------------------
dataTable["FitRank"] = 0

# CHANGE fitness ranks if desired
fitness_ranks_set = ((0, 30), (30, 55), (75, 100))  
dataTable = organize_fitness_ranks(dataTable, fitness_ranks_set, ref_column = "fitFunc")  


# -----------------------------------------------------------------------------
# BOXPLOT & Scatter REPRESENTATION
# -----------------------------------------------------------------------------

# Special BoxPlot display
sns.set_theme(style="darkgrid")
sns.set_context('paper', font_scale=1.0, rc={'line.linewidth': 2.5, 
                'font.sans-serif': [u'Times New Roman']})


# -----------------------------------------------------------------------------
if not os.path.isdir("MultipleFitnessRankComparison"):
    os.mkdir("MultipleFitnessRankComparison")  # Create "MultipleFitnessRankComparison" directory
os.chdir("MultipleFitnessRankComparison")
# -----------------------------------------------------------------------------


# POTENTIAL CHANGE FOR NAMES if a different consortium is used
ratios = ["sucr1_frc2", "Ecbiomass_KTbiomass"]  # Names for new column_ratios to be plotted, in order
input_parameters = ["sucr1_IP", "frc1_IP", "EcInit_IP", "KTInit_IP", "NH4_Ec", "NH4_KT", "Pi_Ec", "Pi_KT"]
output_parameters = ["fitFunc", "Nar_mM", "pCA_mM", "FinalEc_gL", "FinalKT_gL", "FinalSucr"]

x_axis = 'Fitness Ranks'
y_axis1 = 'Ratio of Uptake Rates'
y_axis2 = 'Ratio of Initial Biomass'

name1 = "UptakeRatesRatio_Boxplot"
title1 = "Carbon Uptake Rates ratio"
name2 = "InitBiomassRatio_Boxplot"
title2 = "Initial Biomass ratio"


# BOXPLOT 
# -------

# Basic Input Ratios
myplt.basic_boxplot_scatter(dataTable, "FitRank", ratios[0], x_axis, y_axis1, name1, title1)
# myplt.basic_boxplot_ylims(dataTable, "FitRank", ratios[0], x_axis, y_axis1, title1+"_AxisReduced1", ylims = (0, 1))
# myplt.basic_boxplot_ylims(dataTable, "FitRank", ratios[0], x_axis, y_axis1, title1+"_AxisReduced2", ylims = (0, 2))

myplt.basic_boxplot_scatter(dataTable, "FitRank", ratios[1], x_axis, y_axis2, name2, title2)
# myplt.basic_boxplot_ylims(dataTable, "FitRank", ratios[1], x_axis, y_axis2, title2+"_AxisReduced", ylims = (0, 4))


# NH4 and Pi uptake rates
myplt.basic_boxplot(dataTable, "FitRank", input_parameters[4], x_axis, "NH4 uptake by E.coli", "NH4uptake_Ec_boxplot", "NH4 uptake - E.coli")
myplt.basic_boxplot(dataTable, "FitRank", input_parameters[5], x_axis, "NH4 uptake by P.putida", "NH4uptake_KT_boxplot", "NH4 uptake - P.putida")
myplt.basic_boxplot(dataTable, "FitRank", input_parameters[6], x_axis, "Pi uptake by E.coli", "Piuptake_Ec_boxplot", "Pi uptake - E.coli")
myplt.basic_boxplot(dataTable, "FitRank", input_parameters[7], x_axis, "Pi uptake by P.putida", "Piuptake_KT_boxplot", "Pi uptake by P.putida")

# Final Sucrose
myplt.basic_boxplot(dataTable, "FitRank", output_parameters[5], x_axis, "[Sucrose] (mM)", "finalSucrose_boxplot", "Final Sucrose")


# Final Biomass
myplt.basic_boxplot(dataTable, "FitRank", output_parameters[3], x_axis, "E.coli biomass", "FinalEcBiomass_boxplot", "Final E.coli biomass")
myplt.basic_boxplot(dataTable, "FitRank", output_parameters[4], x_axis, "P.putida biomass", "FinalKTBiomass_boxplot", "Final P.putida biomass")

# Final Products
myplt.basic_boxplot(dataTable, "FitRank", input_parameters[1], x_axis, "[Naringenin] (mM)", "Nar_boxplot", "Final naringenin")
myplt.basic_boxplot(dataTable, "FitRank", input_parameters[2], x_axis, "[pCA] (mM)", "pCA_boxplot", "Final pCA")





















