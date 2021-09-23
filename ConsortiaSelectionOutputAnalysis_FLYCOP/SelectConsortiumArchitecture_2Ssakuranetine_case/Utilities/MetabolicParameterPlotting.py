#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  6 11:53:03 2021
@author: Iván Martín Martín

See function descriptions before their respective code blocks.
"""

import seaborn as sns
import matplotlib.pyplot as plt
import math
import numpy as np
import collections
# import os
# import re



# -----------------------------------------------------------------------------
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


"""
Parsing external file (file = continuous_variables.txt), defined as follows:

        - Header lines are not considered (those starting by '#'), they have just organizational purposes
        - NO blank spaces, comma as separator character
        - Single line file
        
        - FORMAT: list of parameters
        - RESULT: list type
                
        EXAMPLE for continuous_variables.txt: 
            global_init_biomass,global_final_biomass,MetNar_mM,Nar_mM
        
"""

def parsing_external_file_to_list(file):
    # parameters_list = []
    
    with open(file, "r") as params_file:
            
        lines = params_file.readlines()
        for line in lines:
            
            if len(line) > 1 and line[0] != "#":  # Avoid header or empty lines
                parameters_list = line.strip("\n").split(",")

    return parameters_list



# -----------------------------------------------------------------------------
# NEW COLUMN FOR CONFIGURATIONS CATEGORICAL CLASSIFICATION
# -----------------------------------------------------------------------------

"""
Creates a new Dataframe column classifying configurations on biochemically correct
(compatible, 0) or wrong (incompatible, 1).

COLUMN NAME: "BiochemCompat"
VALUES: 0 (biochemically compatible), 1 (biochemically incompatible)

COLUMN OF REFERENCE TO DETERMINE BIOCHEMICAL INCOMPATIBILITY: chosen by user.
    A good choice might be the 'endCycle' column (the ending cycle for a given
    simulation), in case its values are specially low (i.e. lower than 10 cycles).
    
CUTOFF: numerical limit for the biochemical incompatibility, with respect to the
    column of reference. It can be an upper or lower limit, depending on the 'ref_column'
    meaning.
    
    For example, ref_column = 'endCycle', upper_cutoff = 10 (cycles). MEANING: under
    10 cycles of simulation, a given configuration is considered to be BIOCHEMICALLY
    INCOMPATIBLE (i.e. ["BiochemCompat"] = 1).


"""

def biochemical_incompatibility_column_builder(dataframe, ref_column, upper_cutoff=-1, lower_cutoff=-1):
    
    # Categories (BiochemCompat): 0 (yes = compatible), 1 (no = incompatible)
    dataframe["BiochemCompat"] = 0
    
    for row in dataframe.itertuples():
        row_index = row[0]
        
        # If upper_cutoff = -1, this conditional has no sense and does not operate
        if upper_cutoff > 0 and dataframe.loc[row_index, ref_column] < upper_cutoff:  
            dataframe.loc[row_index, "BiochemCompat"] = 1
            
        # If lower_cutoff = -1, this conditional has no sense and does not operate
        elif lower_cutoff > 0 and dataframe.loc[row_index, ref_column] > lower_cutoff:  
            dataframe.loc[row_index, "BiochemCompat"] = 1

# -----------------------------------------------------------------------------



# -----------------------------------------------------------------------------
# BOXPLOT + SCATTER COMBINATION
# -----------------------------------------------------------------------------

"""
COMBINATION OF BOXPLOT AND SCATTERPLOT through seaborn package, for a compound figure with several plots.
alpha: from 0 to 1. Level of opacity of the boxplots, so that the scatter-points can be easily visualized.
"""

def basic_boxplot_scatter_ax(ax, dataframe, x_var, y_var, y_label=None, hue=None, legend=True, title=None):
    
    sns.set(style="whitegrid")  # TO BE IMPLEMENTED
    sns.stripplot(ax=ax, x=x_var, y=y_var, jitter = True, dodge = True, data = dataframe, hue=hue)
    ax_boxplot = sns.boxplot(ax=ax, x = x_var, y = y_var, data = dataframe, boxprops=dict(alpha=0.2), hue=hue, width=0.8)  # Default width: 0.8
    
    # Special y_label (if desired)
    if y_label: ax_boxplot.set(ylabel = y_label)
    # Show just one legend (plot) code, instead of repeating the entries
    handles, labels = ax_boxplot.get_legend_handles_labels()
    # Remove individual legend in each subplot
    if not legend: ax_boxplot.get_legend().remove()
    if title: plt.title(title)
    
    return handles, labels
    

# -----------------------------------------------------------------------------
# BARPLOT OF CONFIGURATIONS
# -----------------------------------------------------------------------------

"""
x_variable: e.g. "Consortium_Arch": 2_models, 3_models
first_categorical: biomass loss in configurations, "BL" vs. "nonBL" distinction
second_categorical: "Acceptable" vs. "nonOptimal" configurations distinction
"""

def barplot_of_configurations(dataframe, x_variable, first_categorical, second_categorical, filename):
    
    fig = sns.displot(data=dataframe, x=x_variable, hue=first_categorical, col=second_categorical, multiple="dodge")
    fig.savefig(filename+".png")
    plt.close()
    
    
    
# -----------------------------------------------------------------------------
# FVA PLOTTING
# -----------------------------------------------------------------------------

""" FIGURE-LEVEL FUNCTION
Composes a Kernel Density Estimation plot (2D), with one FVA variable in one of
the axis. If a column with categorical groups of configurations is given 
('categorical_column'), the KDE plot makes the associated distinction between groups.

PARAMETERS:
    
    * kde_plot_params: dictionary of pair of numerical rates to be used in the 2D plots.
    A numerical rate can be an uptake or secretion rate, an FVA rate, etc.
        Dictionary already processed from FVA_rates.txt.
    
    * dataframe: Pandas dataframe.
    
    * categorical_column: parameter to make a distinction between groups of 
        configurations ('hue' parameter in Seaborn jointplot)
"""

def kde_plotting(kde_plot_params, dataframe, categorical_column=None, kind="kde"):
    
    # Theme Style
    sns.set_theme(style="darkgrid")
    sns.set_context('paper', font_scale=1, rc={'line.linewidth': 2.5, 
                    'font.sans-serif': [u'Times New Roman']})
    
    # KDE Plotting
    for kde_pair in kde_plot_params.keys():
    
        FVA_rates = kde_plot_params[kde_pair]  # First metFVA, second metFVA
        fig1 = sns.jointplot(data=dataframe, x=FVA_rates[0], y=FVA_rates[1], 
                             hue=categorical_column, kind=kind)  
        fig1.plot_joint(sns.kdeplot, levels=2, thresh=0.5)
        fig1.plot_marginals(sns.histplot, element="bars", stat="count", legend=False, kde=False, multiple="dodge")
        # fig1.set(ylims=(min(dataframe[FVA_rates[0]]), 1), xlims=(min(dataframe[FVA_rates[1]]), 1))
        
        # Save & Close figure
        fig1.savefig(f"{FVA_rates[0]}_vs_{FVA_rates[1]}.png")
        plt.close()  
        
# -----------------------------------------------------------------------------


      
# -----------------------------------------------------------------------------  
# PAIRPLOT: pairwise relationships between numerical variables
# -----------------------------------------------------------------------------

"""
Plotting pairwise relationships in a dataset, with distinction according to 
categorical subgroups within the dataset ('categorical_column').

Pairgrid: https://seaborn.pydata.org/generated/seaborn.PairGrid.html
Pairplot: https://seaborn.pydata.org/generated/seaborn.pairplot.html#seaborn.pairplot

# Grid Diagonal: histograms
# Grid Upper Corner: scatterplot + regression line (might not always have sense to draw a regline)
# Grid Lower Corner: kdeplot without filling (for a proper visualization of each subgroup distribution)
"""

def pairgrid_plot(dataframe, plot_name, categorical_column=None):
    
    # PAIRGRID
    fig1 = sns.PairGrid(dataframe, hue=categorical_column)
    
    # UPPER CORNER OF PAIRGRID
    fig1.map_lower(sns.regplot)  # sns.scatterplot as a different alternative
    
    # LOWER CORNER OF PAIRGRID
    fig1.map_upper(sns.kdeplot, fill=False, levels=5, thresh=0.2, common_norm=False)
    
    # DIAGONAL
    fig1.map_diag(sns.histplot, kde=True)
    
    # LEGEND
    fig1.add_legend()
    
    # SAVE FIGURE
    fig1.savefig(plot_name+"_pairgrid_plot.png")
    plt.close()
           
        
        
# -----------------------------------------------------------------------------
# HISTOGRAM PLOTTING: histplot or equivalent for a series of numerical (discrete) variables
# -----------------------------------------------------------------------------

""" FIGURE-LEVEL FUNCTION
Discrete variables: number of configurations vs. a series of discrete values 
given by a variable, with a further distinction by:
    
    - Consortium architecture
    - Biomass Loss effect

Note that this is a Figure-level function.
"""

def histplotting(dataframe, variable, first_categorical, second_categorical):
    
    fig = sns.displot(data=dataframe, x=variable, hue=first_categorical, col=second_categorical, multiple="dodge")
    fig.savefig(variable+".png")
    plt.close()
    

    
# -----------------------------------------------------------------------------
# SCATTER PLOTTING: scatter or equivalent for a series of numerical (continuous) variables
# -----------------------------------------------------------------------------

""" FIGURE-LEVEL FUNCTION
Continuous variables: a given variable vs. Consortium Architecture classification,
with further distinction by biomass Loss effect.

Note that this is a Figure-level function.
"""

def scatterplotting(x_var, y_var, dataframe, filename, first_categorical=None):
    
    fig = plt.figure(num=0, clear=True, figsize=(7, 7))
    ax_boxplot = sns.boxplot(x = x_var, y = y_var, data = dataframe, boxprops=dict(alpha=0.2), hue=first_categorical)
    sns.stripplot(x=x_var, y=y_var, jitter = True, dodge = True, data = dataframe, hue=first_categorical)
    
    # Show just one legend (plot) code, instead of repeating the entries
    handles, labels = ax_boxplot.get_legend_handles_labels()
    ax_boxplot.legend(handles[2:4], labels[2:4])
    
    fig.savefig(filename+".png")
    plt.close(fig)
    


# -----------------------------------------------------------------------------
# INDIVIDUAL INPUT VARIABLE ANALYSIS
# Last two functions combined in a single one through sns.catplot
# -----------------------------------------------------------------------------

""" FIGURE-LEVEL FUNCTION
Discrete variables: number of configurations vs. a series of discrete values 
given by a variable, with a further distinction by:
    
    - Consortium architecture
    - Biomass Loss effect
    
Continuous variables: a given variable vs. Consortium Architecture classification,
with further distinction by biomass Loss effect.

Note that this is a Figure-level function.
"""

def individual_input_variable_analysis(x_var, y_var, dataframe, plot_title, first_categorical=None, second_categorical=None, kind="strip"):
    
    fig = sns.catplot(x=x_var, y=y_var, hue=first_categorical, col=second_categorical, data=dataframe, kind=kind, height=8, aspect=1);
    fig.savefig(plot_title+".png")
    plt.close()



# -----------------------------------------------------------------------------
# AXES-LEVEL UTILITY FOR PLOTTING SCATTER+BOXPLOTS
# -----------------------------------------------------------------------------

""" AXES-LEVEL FUNCTION
Number of plots per row: default, 4 (it can be changed) (i.e. number of columns)
Number of rows: as many as necessary to fit all plots, given the number of plots per row (i.e. columns)

The function recieves a dictionary with: 
    
    key (variable name) : value (plot title)
"""

def axes_level_scatterplot(variables_list, dataframe, plot_title, ncols = None, suptitle=None, legend=True, hue="BiomassLoss", single_scatter=False):

    # GLOBAL DISPLAY
    # ==============
    sns.set_theme(style="darkgrid")
    
    # Number of columns = 4, since it seems like a nice display. Feel free to change if desired!
    if not ncols: ncols = len(variables_list) if len(variables_list) < 4 else 4
    # Number of rows in the global_figure
    nrows = math.ceil(len(variables_list)/ncols)
    
    # Series of subplots for each of the numerical variables
    figsize = (6 * ncols, 8 * nrows)
    
    global_figure, axes = plt.subplots(num=0, clear=True, figsize=figsize, nrows=nrows, ncols=ncols)
    plt.tight_layout(pad=4, h_pad=4, w_pad=4, rect=None)  # Margins between subplots
    
    # SUPTITLE
    if suptitle: global_figure.suptitle(suptitle, fontsize = 20, fontfamily='DejaVu Sans')
        
    # Automatic fitting of subplots in the grid
    n_figs = 0; row = 0; col = 0
    
    
    # Subplots
    # --------
    
    for parameter in variables_list:
        
        if not single_scatter:
            if nrows != 1:
                handles, labels = basic_boxplot_scatter_ax(axes[row, col], dataframe, x_var="Consortium_Arch", y_var=parameter, 
                                                           hue=hue, legend=legend)
            else:
                handles, labels = basic_boxplot_scatter_ax(axes[col], dataframe, x_var="Consortium_Arch", y_var=parameter, 
                                                           hue=hue, legend=legend)
        
        else:
            if nrows != 1:
                scatter = sns.scatterplot(ax=axes[row, col], data=dataframe, x=parameter, y="fitFunc",
                                                  hue="Consortium_Arch", legend=legend)
                
            else:
                scatter = sns.scatterplot(ax=axes[col], data=dataframe, x=parameter, y="fitFunc", 
                                                  hue="Consortium_Arch", legend=legend)
                
            # Show just one legend (plot) code, instead of repeating the entries
            # handles, labels = scatter.get_legend_handles_labels()
        
        
        # Figure display updating
        # -----------------------
        n_figs += 1
        if (n_figs%ncols) == 0: row += 1
        col = 0 if col == ncols-1 else col + 1
    
    
    # Save and close global_figure
    # ----------------------------
    n_cat = len(dataframe[hue].unique())
    # print("n_cat for nutrients: ", n_cat)  # 2 plots (scatter, boxplot) x n_cat categories = number of elements in handles, labels
    if not legend: global_figure.legend(handles[-n_cat:], labels[-n_cat:], loc=7)  # Take only the existing categories without repetition
    
    if not single_scatter: global_figure.savefig(plot_title+"_scatter_boxplots.png")
    else: global_figure.savefig(plot_title+"_scatter.png")
    plt.close(global_figure)
    
    
    
# -----------------------------------------------------------------------------
# AXES-LEVEL UTILITY FOR PLOTTING COUNTPLOTS
# -----------------------------------------------------------------------------

""" AXES-LEVEL FUNCTION
Number of plots per row: default, 4 (it can be changed) (i.e. number of columns)
Number of rows: as many as necessary to fit all plots, given the number of plots per row (i.e. columns)

The function recieves a list with all the parameters to be individually plotted.
"""

def axes_level_histplot(variables_list, dataframe, plot_title, ncols = None, suptitle=None, hue="Consortium_Arch"):

    # GLOBAL DISPLAY
    # ==============
    sns.set_theme(style="darkgrid")
    
    # Number of columns = 4, since it seems like a nice display. Feel free to change if desired!
    if not ncols: ncols = len(variables_list) if len(variables_list) < 4 else 4
    # Number of rows in the global_figure
    nrows = math.ceil(len(variables_list)/ncols)
    
    # Series of subplots for each of the numerical variables
    figsize = (6 * ncols, 8 * nrows)
    
    global_figure, axes = plt.subplots(num=0, clear=True, figsize=figsize, nrows=nrows, ncols=ncols)
    plt.tight_layout(pad=4, h_pad=4, w_pad=4, rect=None)  # Margins between subplots
    
    # SUPTITLE
    if suptitle:
        global_figure.suptitle(suptitle, fontsize = 20, fontfamily='DejaVu Sans')
        
    # Automatic fitting of subplots in the grid
    n_figs = 0
    row = 0
    col = 0
    
    
    # Subplots
    # --------
    
    for parameter in variables_list:
        
        if nrows != 1: 
            sns.countplot(ax=axes[row, col], data=dataframe, x=parameter, hue=hue, dodge=True)
                
        else: 
            hist = sns.countplot(ax=axes[col], data=dataframe, x=parameter, hue=hue, dodge=True)
            handles, labels = hist.get_legend_handles_labels()
            hist.get_legend().remove()

        
        # Figure display updating
        # -----------------------
        n_figs += 1
        if (n_figs%ncols) == 0: row += 1
        col = 0 if col == ncols-1 else col + 1
    
    
    # Save and close global_figure
    # ----------------------------
    n_cat = len(dataframe[hue].unique())
    # print("n_cat for nutrients: ", n_cat)  # 2 plots (scatter, boxplot) x n_cat categories = number of elements in handles, labels
    global_figure.legend(handles[-n_cat:], labels[-n_cat:], loc="upper right")
    global_figure.savefig(plot_title+"_countplot.png")
    plt.close(global_figure)



# -----------------------------------------------------------------------------
# FACETGRID: catplot functionality with AXES-LEVEL REPRESENTATION
# DOCS: https://seaborn.pydata.org/generated/seaborn.FacetGrid.html
# -----------------------------------------------------------------------------

""" AXES-LEVEL FUNCTION

"""

def facetgrid_catplotting(dataframe, plotting_parameter, col="BiomassLoss", hue="Consortium_Arch"):
    
    g = sns.FacetGrid(dataframe, col=col,  hue=hue)
    g.map_dataframe(sns.histplot, x=plotting_parameter)



# -----------------------------------------------------------------------------
# BIOMASS PLOTTING FUNCTION
# -----------------------------------------------------------------------------

""" AXES-LEVEL FUNCTION
See BiomassProductionAnalysis.py script.
"""

def biomass_plotting(cons_architecture_list, biomassDataframe, plotname):
    
    # Global Figure
    sns.set(style="darkgrid")
    figsize = (20, 10)
    ncols=len(cons_architecture_list)
    col = 0
    
    global_figure, axes = plt.subplots(num=0, clear=True, figsize=figsize, ncols=ncols)  # as many columns as consortium architectures
    plt.tight_layout(pad=4, h_pad=4, w_pad=4, rect=None)  # Margins between subplots
    
    for architecture in biomassDataframe["Consortium Architecture"].unique():
        handles, labels = basic_boxplot_scatter_ax(ax=axes[col], 
                                                   dataframe=biomassDataframe[biomassDataframe["Consortium Architecture"] == architecture], 
                                                   x_var="Microbial model", y_var="Biomass (g/L)", 
                                                   hue="Moment during simulation", legend=False)
        axes[col].title.set_text("Consortium Architecture: "+architecture)
        col += 1

            
    # Save and close global_figure
    # ----------------------------
    n_cat = len(biomassDataframe["Moment during simulation"].unique())
    # print("n_cat for biomassDataframe: ", n_cat)  # 2 plots (scatter, boxplot) x n_cat categories = number of elements in handles, labels
    global_figure.legend(handles[-n_cat:], labels[-n_cat:], loc=1)  # Take only the existing categories without repetition
    global_figure.savefig("biomassAnalysis_"+plotname+".png")
    plt.close(global_figure)



# -----------------------------------------------------------------------------
# ENDCYCLE ANALYSIS ()
# -----------------------------------------------------------------------------

""" STATISTICS DRAWING FUNCTION

"""

def statistics_description(dataframe, hue, descriptive_columns, filename=None):
    
    # File to write statistical description
    if filename: file = open(filename+"_statsDescription.txt", "w")
    else: file = open("statsDescription.txt", "w")
    
    dataframe_fractions = dataframe[hue].unique()
    
    for df_fraction in dataframe_fractions:
    
        dataframe_fraction = dataframe[dataframe[hue] == df_fraction]
        file.write(str(df_fraction))
        file.write(str("\n====================================================\n\n"))
        
        # Write whole statistical description for each column in descriptive_columns
        for column in descriptive_columns:
            stat_description = dataframe_fraction[column].describe()
            file.write(str(stat_description))
            file.write("\n-----------------------------------------------------\n")
        file.write("\n\n\n")
    

    file.close()
    
    













