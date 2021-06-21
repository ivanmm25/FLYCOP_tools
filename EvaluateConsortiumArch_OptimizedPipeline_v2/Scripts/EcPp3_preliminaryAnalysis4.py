#!/usr/bin/python3

############ FLYCOP ############
# Author: Beatriz García-Jiménez, Iván Martín Martín
# April 2018, April 2021
################################

"""
PRELIMINARY ANALYSIS of the 'configurationsResults' information (IV)
# -----------------------------------------------------------------------------

# BLOCK 5: ADDITIONAL PLOTTING

    (5A) BOXPLOTS, categorical comparison of consortium architecture.
    	- SD acceptable, Acceptable configurations
        - Biomass loss vs. non-biomass loss
        - Subdivision by model architecture
    
    Variables in the y-axis (quantitative): 
    	- Input variables: sucrose and fructose uptake rates, E.coli and KT NH4 uptake rates
        - Global final biomass (sum of all microbes)
        - Fitness

# -----------------------------------------------------------------------------

    # (5B) HEATMAP with input configuration values (values of parameters optimized by SMAC). 
    A different heatmap for every consortium architecture. Normal distribution of variables 
    is evaluated before representing the HeatMap through a Shapiro test.
    
    If the variables considered in the pairwise relationship are normally distributed, 
    Pearson correlation coefficient is used. Otherwise, Spearman correlation coefficient is implemented.
    
    ### HEATMAP ###
    	- SD acceptable, Acceptable configurations
        - Biomass loss vs. non-biomass loss - Should we consider just cases with non-biomass loss?
        - Subdivision by model architecture

# -----------------------------------------------------------------------------

    (5C) SCATTERPLOT MATRIX: pairwise relationships between quantitative variables.
    	- SD acceptable, Acceptable configurations
        - Biomass loss vs. non-biomass loss - Should we consider just cases with non-biomass loss?
        - Subdivision by model architecture

# -----------------------------------------------------------------------------

    (5D) Scatterplot: SD vs. fitness.
    	- SD acceptable, Acceptable configurations
        - Biomass loss vs. non-biomass loss: see legend (0: non-biomass loss; 1: biomass loss)
        - Subdivision by model architecture

"""


import re
import sys
import os.path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy import stats
import seaborn as sns
# import shutil, errno
# import cobra
# import tabulate
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


# FUNCTIONS
# ---------

# COMBINATION OF BOXPLOT AND SCATTERPLOT through seaborn package, for a compound figure with several plots
# alpha: from 0 to 1. Level of opacity of the boxplots, so that the scatter-points can be easily visualized

def basic_boxplot_scatter_ax(ax, dataframe, x_var, y_var, x_label, y_label):
    
    sns.set(style="whitegrid")  # TO BE IMPLEMENTED
    sns.stripplot(ax=ax, x=x_var, y=y_var, jitter = True, data = dataframe)
    ax_boxplot = sns.boxplot(ax=ax, x = x_var, y = y_var, data = dataframe, boxprops=dict(alpha=0.2))
    ax_boxplot.set(xlabel = x_label, ylabel = y_label)

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


# PARSING PARAMETERS
# -----------------------------------------------------------------------------
# Reading the arguments given by command line
cons_architecture_series = sys.argv[1]  # e.g. '2_models 3_models'
# -----------------------------------------------------------------------------

cons_architecture_list = cons_architecture_series.split()
configResults_excel = "configurationResults_consArchitecture.xlsx"

# Global dataframe with details of all consortium architectures for further plotting purposes
global_dataframe_architectures = pd.read_excel("global_dataframe_architectures.xlsx")
# Acceptable SD for plotting
global_dataframe_architectures_SD_acc = global_dataframe_architectures[(global_dataframe_architectures["ID_SD"] == 0) & (global_dataframe_architectures["ConfigKey"] == "Acceptable")]


###############################################################################
###############################################################################
# BLOCK 5: ADDITIONAL PLOTTING
# -----------------------------------------------------------------------------
    
# (5A) BOXPLOTS, categorical comparison of consortium architecture
    # SD acceptable, Acceptable configurations
    # Biomass loss vs. non-biomass loss
    # Subdivision by model architecture

# y-axis variable (quantitative)
    # Input variables: sucrose and fructose uptake rates, E.coli and KT NH4 uptake rates
    # Global final biomass (sum of all microbes)
    # Fitness
# -----------------------------------------------------------------------------

# GLOBAL DISPLAY
global_figure, axes = plt.subplots(num=0, clear=True, figsize=(15, 15), nrows=2, ncols=3)
global_figure.suptitle("BoxPlots - categorical comparison of consortium architecture", fontsize = 24, fontfamily='DejaVu Sans')

# Subplots
basic_boxplot_scatter_ax(axes[0, 0], global_dataframe_architectures_SD_acc, "Consortium_Arch", "sucr_upt", "Consortium Architecture", "Sucrose uptake rate (mmol/ g DW h)")
basic_boxplot_scatter_ax(axes[1, 0], global_dataframe_architectures_SD_acc, "Consortium_Arch", "frc_upt", "Consortium Architecture", "Fructose uptake rate (mmol/ g DW h)")
basic_boxplot_scatter_ax(axes[0, 1], global_dataframe_architectures_SD_acc, "Consortium_Arch", "nh4_Ec", "Consortium Architecture", "NH4 uptake rate (mmol/ g DW h) - E.coli")
basic_boxplot_scatter_ax(axes[1, 1], global_dataframe_architectures_SD_acc, "Consortium_Arch", "nh4_KT", "Consortium Architecture", "NH4 uptake rate (mmol/ g DW h) - KT")
basic_boxplot_scatter_ax(axes[0, 2], global_dataframe_architectures_SD_acc, "Consortium_Arch", "global_final_biomass", "Consortium Architecture", "Global final biomass (gL-1)")
basic_boxplot_scatter_ax(axes[1, 2], global_dataframe_architectures_SD_acc, "Consortium_Arch", "fitFunc", "Consortium Architecture", "Fitness (mM / gL-1")

# Save and close global_figure
global_figure.savefig("model_architecture_boxplots.png")
plt.close(global_figure)


# -----------------------------------------------------------------------------
# (5B) HEATMAP with input configuration values (values of parameters optimized by SMAC)
# A different heatmap for every consortium architecture
# Note that normal distribution of variables has to be evaluated before representing the HeatMap

    # SD acceptable, Acceptable configurations
    # Biomass loss vs. non-biomass loss - Should we consider just cases with non-biomass loss?
    # Subdivision by model architecture
# -----------------------------------------------------------------------------

heatmap_variables = ["sucr_upt", "frc_upt", "nh4_Ec", "nh4_KT", "global_init_biomass", "global_final_biomass", "MetNar_mM", "fitFunc"]

# FOR EVERY POTENTIAL ARCHITECTURE EVALUATED THROUGH FLYCOP
with pd.ExcelFile(configResults_excel) as xls:
    for architecture in xls.sheet_names:  # Every sheet_name is a different architecture
        if architecture == "Sheet": continue
        
        # (a) INITIAL READING OF EXCEL FILE
        configResults = pd.read_excel(xls, sheet_name=architecture)
        adapted_input_table = configResults[(configResults["ID_SD"] == 0) & (configResults["ConfigKey"] == "Acceptable")]
        adapted_input_table = adapted_input_table[heatmap_variables]
        
        normal_distr = np.array([])  # Normal distribution: 0; Non-normal distribution: 1
        
        for column in adapted_input_table.columns:
            shapiro_test = stats.shapiro(adapted_input_table[column])  # p-value = shapiro_test[1]
            normal_distr = np.append(normal_distr, 0) if shapiro_test[1] > 0.05 else np.append(normal_distr, 1)  # Normal distribution if p-value > 0.05
        
        # Numpy to Pandas through reshape. Pandas dataframe with a single row indicating whether each of the 'heatmap_variables' are normally distributed or not
        normal_distr = pd.DataFrame(data=np.reshape(normal_distr, (1, len(normal_distr))), columns=heatmap_variables, dtype=np.float64)
        
        # Build a correlation matrix (as Pandas dataframe)
        corr_matrix = pd.DataFrame(columns=heatmap_variables, index=heatmap_variables, dtype=np.float64)
        
        for row in corr_matrix.itertuples():
            row_variable = row[0]
            
            for column in corr_matrix.columns:
                if normal_distr.loc[0, row_variable] == 0 and normal_distr.loc[0, column] == 0:
                    corr_matrix.loc[row_variable, column] = stats.pearsonr(adapted_input_table[row_variable], adapted_input_table[column])[0]
                else:
                    corr_matrix.loc[row_variable, column] = stats.spearmanr(adapted_input_table[row_variable], adapted_input_table[column])[0]
    
        # (B) DRAW HEATMAP
        heatmap = plt.figure(clear=True, figsize=(25, 15))
        plt.title("HeatMap_{0}".format(architecture), fontsize = 20, fontfamily='DejaVu Sans')
        sns.heatmap(corr_matrix, annot=True, cmap="bwr")
        heatmap.savefig("heatmap_{0}.png".format(architecture))
        plt.close(heatmap)


# -----------------------------------------------------------------------------
# (5C) SCATTERPLOT MATRIX: pairwise relationships between quantitative variables
# Different model architectures are represented in different colours. See lateral legend

    # SD acceptable, Acceptable configurations
    # Biomass loss vs. non-biomass loss - Should we consider just cases with non-biomass loss?
    # Subdivision by model architecture
# -----------------------------------------------------------------------------

scatter_variables = ["sucr_upt", "frc_upt", "nh4_Ec", "nh4_KT", "global_init_biomass", "global_final_biomass", "MetNar_mM", "Consortium_Arch"]  # Length = 7, "fitFunc"
adapted_scatter_table = global_dataframe_architectures_SD_acc[scatter_variables]

sns.set_style("darkgrid")
scatterp_matrix = sns.pairplot(adapted_scatter_table, hue="Consortium_Arch")  # 'hue' is reference variable for filtering
scatterp_matrix.savefig("scatterp_matrix_consArch.png")


# -----------------------------------------------------------------------------
# (5D) Scatterplot: SD vs. fitness
# Different model architectures are represented in different colours. See lateral legend

    # SD acceptable, Acceptable configurations
    # Biomass loss vs. non-biomass loss: see legend (0: non-biomass loss; 1: biomass loss)
    # Subdivision by model architecture
# -----------------------------------------------------------------------------

# Column name adaotation ("DeadTracking") for 'style' variable in 'scatter_fitness_SD.png' plot
for row in global_dataframe_architectures_SD_acc.itertuples():
    if global_dataframe_architectures_SD_acc.loc[row[0], "DeadTracking"] == 0: global_dataframe_architectures_SD_acc.loc[row[0], "DeadTracking"] = "nonBL"
    else: global_dataframe_architectures_SD_acc.loc[row[0], "DeadTracking"] = "BL"
    
sns.set_style("darkgrid")
fit_scatter = plt.figure(num=0, clear=True, figsize=(7, 7))
sns.scatterplot(data=global_dataframe_architectures_SD_acc, x="fitFunc", y="SD", hue="Consortium_Arch", style="DeadTracking")
plt.title("Fitness vs. SD", fontsize = 14)
fit_scatter.savefig("scatter_fitness_SD.png")
plt.close(fit_scatter)

###############################################################################
###############################################################################



















