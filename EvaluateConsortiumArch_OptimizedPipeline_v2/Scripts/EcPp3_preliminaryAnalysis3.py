#!/usr/bin/python3

############ FLYCOP ############
# Author: Beatriz García-Jiménez, Iván Martín Martín
# April 2018, April 2021
################################

"""
PRELIMINARY ANALYSIS of the 'configurationsResults' information (III)
# -----------------------------------------------------------------------------

# BLOCK 4: PLOTTING THE DISTRIBUTION OF CONFIGURATIONS DEPENDING ON CONSORTIUM ARCHITECTURE

	* Compose a global dataframe with required details of all possible architectures. Filter by acceptable SD [ID_SD = 0].

	* Comparison of acceptable vs. non-optimal configurations, in terms of model architecture (barplot).
		- SD acceptable
	    - Acceptable vs. Non-optimal configurations
	    - Subdivision by model architecture

	* Comparison of acceptable vs. non-optimal configurations, in terms of model architecture (barplot).
		- SD acceptable
		- Further subdivision by biomass loss vs. non-biomass loss
	    - Acceptable vs. Non-optimal configurations
	    - Subdivision by model architecture

	* Fitness evaluation by model architecture (boxplot-scatter).
		- SD acceptable
	    - Only non-biomass loss cases
	    - Acceptable vs. Non-optimal configurations
	    - Subdivision by model architecture

# -----------------------------------------------------------------------------
"""


import re
import sys
import os.path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
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

# COMBINATION OF BOXPLOT AND SCATTERPLOT through seaborn package
# alpha: from 0 to 1. Level of opacity of the boxplots, so that the scatter-points can be easily visualized

def basic_boxplot_scatter(dataframe, x_var, y_var, x_label, y_label, filename, plot_title):
    
    fig = plt.figure(num=0, clear=True, figsize=(7, 7))
    ax_boxplot = sns.boxplot(x = x_var, y = y_var, data = dataframe, boxprops=dict(alpha=0.2))
    sns.stripplot(x=x_var, y=y_var, jitter = True, data = dataframe)
    ax_boxplot.set(xlabel = x_label, ylabel = y_label)
    
    plt.title(plot_title, fontsize = 14)
    fig.savefig(filename+".png")
    plt.close(fig)



# BARPLOT OF CONFIGURATIONS

# y_categories: e.g. 'model_architecture_categories' = '2_models', '3_models'
# y_variable_count: baseline column to determine height of every bar in the plot, e.g. "Consortium_Arch"
# x_categories: ordered list of categories in x-axis. e.g. ["Nonoptimal_nonBL", "Nonoptimal_BL", "Acceptable_nonBL", "Acceptable_BL"]

def basic_barplot(dataframe, y_variable_count, y_categories, x_categories, x_label, y_label, filename, plot_title):
    
    # Lists for each y_category, depending on the y_variable_count (Dictionary format)
    y_counts_dict = {}
    for y_category in y_categories:
        y_cat_values = []  # List of configuration cases for a given consortium architecture
        
        for x_category in x_categories: 
            # One of the categories in 'x_categories'
            x_category_prefilter_df = dataframe[dataframe["ConfigKey"] == x_category]  
            
            # Count the number of cases of a given 'y_category' for each 'x_category': e.g. '2_models' with 'Acceptable_nonBL', 'Acceptable_BL', 'Nonoptimal_nonBL', 'Nonoptimal_BL'
            y_cat_values.append(x_category_prefilter_df[x_category_prefilter_df[y_variable_count] == y_category].count()[0])
        
        # Include the new list to the associated dictionary
        y_counts_dict[y_category] = y_cat_values
    
    # Create figure
    fig, axes = plt.subplots(num=0, clear=True, figsize=(7, 7))

    colors = cm.rainbow(np.linspace(0, 1, len(y_categories)))
    bottom_flag = False
    
    # 'Bottom' refers to the height of a column in the barplot when a new consortium architecture is included,
    # since it is a stacked barplot
    
    for n_categories in range(len(y_categories)):
        if not bottom_flag:
            axes.bar(x_categories, y_counts_dict[y_categories[n_categories]], color=colors[n_categories], label=y_categories[n_categories])
            bottom = np.array(y_counts_dict[y_categories[n_categories]])
            bottom_flag = True
        else:
            axes.bar(x_categories, y_counts_dict[y_categories[n_categories]], color=colors[n_categories], bottom=bottom, label=y_categories[n_categories])
            bottom = bottom + np.array(y_counts_dict[y_categories[n_categories]])
    
    # Legend, labels, title
    plt.legend(loc="lower left", bbox_to_anchor=(0.8,1.0))
    plt.ylabel(y_label)
    plt.xlabel(x_label)  
    plt.title(plot_title, fontsize = 12)
    
    # Adjust y-axis
    # plt.ylim(top=len(dataframe))
    plt.yticks(np.linspace(0, len(dataframe), len(dataframe)//10))
    
    # Bar labels
    bars = axes.patches  # Bars
    labels = [bars[i].get_height() for i in range(len(bars))]  # Labels
    prev_height = 0
    
    # Position the bar labels in the middle of the bar and color category, if there is such a bar
    for bar, label in zip(bars, labels):
        mid_height = bar.get_height() / 2
        axes.text(bar.get_x() + bar.get_width() / 2, mid_height + prev_height, label, fontfamily='sans', fontsize=12, color = "black")
        prev_height += bar.get_height()

    # Save and close figure
    fig.savefig(filename+".png")
    plt.close(fig)
    
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
columns_of_interest = ["Consortium_Arch", "fitFunc", "SD", "ID_SD", "MetNar_mM", "DeadTracking", "ConfigKey", \
                       "sucr_upt", "frc_upt", "nh4_Ec", "nh4_KT", "global_init_biomass", "global_final_biomass"]
global_dataframe_architectures = pd.DataFrame(columns=columns_of_interest)


###############################################################################
###############################################################################
# BLOCK 4: PLOTTING THE DISTRIBUTION OF CONFIGURATIONS DEPENDING ON CONSORTIUM ARCHITECTURE
# Always acceptable SD for plotting: SD < 0.1*(average_fitness)
# -----------------------------------------------------------------------------

# (1) COMPOSE A GLOBAL DATAFRAME with details of all possible architectures
with pd.ExcelFile(configResults_excel) as xls:
    for architecture in xls.sheet_names:  # Every sheet_name is a different architecture
        if architecture == "Sheet": continue
        
        configResults = pd.read_excel(xls, sheet_name=architecture)
        fraction_configResults = configResults[columns_of_interest]
        global_dataframe_architectures = pd.concat([global_dataframe_architectures, fraction_configResults], ignore_index = True)
    
    
# Save 'global_dataframe_architectures' in xlsx format for further plotting purposes
global_dataframe_architectures.to_excel("global_dataframe_architectures.xlsx", header=True, index=False, index_label=None)
# Acceptable SD for plotting
global_dataframe_architectures_SD = global_dataframe_architectures[global_dataframe_architectures["ID_SD"] == 0]  
    

# CATEGORIES
model_architecture_categories = global_dataframe_architectures_SD["Consortium_Arch"].unique().tolist()
configkey_categories = global_dataframe_architectures_SD["ConfigKey"].unique().tolist()
biomass_evolution_categories = global_dataframe_architectures_SD["DeadTracking"].unique().tolist()
    
# -----------------------------------------------------------------------------

# (2) COMPARISON OF ACCEPTABLE vs. NON-OPTIMAL ARCHITECTURES, BY MODEL ARCHITECTURE
    # SD acceptable
    # Acceptable vs. Non-optimal configurations
    # Subdivision by model architecture
    
# BARPLOT OF MODEL ARCHITECTURE vs. Acceptable or NonOptimal configurations
basic_barplot(global_dataframe_architectures_SD, y_variable_count="Consortium_Arch", y_categories = model_architecture_categories, 
              x_categories=["Nonoptimal", "Acceptable"], x_label="Configuration Key", y_label="Consortium Architecture", 
              filename="consortiumArchitectureEvaluation_acc_nonOpt", plot_title="Consortium Architecture Evaluation I")

# -----------------------------------------------------------------------------

# (3) COMPARISON OF ACCEPTABLE vs. NON-OPTIMAL ARCHITECTURES, BY MODEL ARCHITECTURE (II)
    # SD acceptable
    # Acceptable vs. Non-optimal configurations
    # Biomass loss vs. non-biomass loss (new!)
    # Subdivision by model architecture
    
plotting_globaldf = pd.DataFrame(columns=columns_of_interest)
    
for configkey in configkey_categories:
    for biomass_ev in biomass_evolution_categories: 
        
        fraction_globaldf2 = global_dataframe_architectures_SD[(global_dataframe_architectures_SD["ConfigKey"] == configkey) & (global_dataframe_architectures_SD["DeadTracking"] == biomass_ev)]
        biomass_ev = "nonBL" if biomass_ev == 0 else "BL"
        fraction_globaldf2["ConfigKey"] = configkey+"_"+biomass_ev
        plotting_globaldf = pd.concat([plotting_globaldf, fraction_globaldf2], ignore_index = True)
    
# BARPLOT OF MODEL ARCHITECTURE vs. Acceptable or NonOptimal configurations, with further subdivision of biomass loss vs. non-biomass loss
basic_barplot(plotting_globaldf, y_variable_count="Consortium_Arch", y_categories = model_architecture_categories,
              x_categories=["Nonoptimal_nonBL", "Nonoptimal_BL", "Acceptable_nonBL", "Acceptable_BL"], 
              x_label="Configuration Key (BL vs. nonBL)", y_label="Consortium Architecture", 
              filename="consortiumArchitectureEvaluation_BL_nonBL", plot_title="Consortium Architecture Evaluation II")   

# -----------------------------------------------------------------------------
    
# (4) FITNESS EVALUATION (quantitative), BY MODEL ARCHITECTURE
    # SD acceptable
    # Only non-biomass loss cases are considered
    # Acceptable vs. Non-optimal configurations
    # Subdivision by model architecture

global_dataframe_architectures_SD_nonBL = global_dataframe_architectures_SD[global_dataframe_architectures_SD["DeadTracking"] == 0] 
fitnessGlobal_df = pd.DataFrame(columns=columns_of_interest)

for configkey in configkey_categories: 
    for architecture in cons_architecture_list:
        
        fraction_fitnessGlobal = global_dataframe_architectures_SD_nonBL[(global_dataframe_architectures_SD_nonBL["Consortium_Arch"] == architecture) & (global_dataframe_architectures_SD_nonBL["ConfigKey"] == configkey)]
        fraction_fitnessGlobal["ConfigKey"] = configkey+"_"+architecture
        fitnessGlobal_df = pd.concat([fitnessGlobal_df, fraction_fitnessGlobal], ignore_index = True)


# PLOT OF FITNESS vs. Acceptable or NonOptimal configurations, with further subdivision depending on model architecture (categorical, scatter-boxplot)
basic_boxplot_scatter(fitnessGlobal_df, "ConfigKey", "fitFunc", "Configuration Key - model arch", "Fitness (mM/gL)",
                      "consortiumArchitectureEvaluation_fitness", "Consortium Architecture Evaluation III")
###############################################################################
###############################################################################




















