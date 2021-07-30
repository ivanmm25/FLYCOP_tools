#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 11:52:44 2021

@author: Iván Martín Martín
"""

"""
DESCRIPTION (see detailed description in each plotting function)

    Plotting script for Input & Output Analysis in:
        - InputParametersAnalysis.py
        - OutputParametersAnalysis.py
        - Others (...)
    
NOTE THAT:
    
    xxx
    
"""

import matplotlib.pyplot as plt
import seaborn as sns


# =============================================================================
# 2 subplots with the SAME x, y labels

    # First subplot: the axes comprise the whole extension of the data (x, y dimensions)
    # Second subplot: y-axis with UPPER limitation, 'subset_ylim', to amplify the scale
    
# =============================================================================

def two_subplots_subsetylim(x_label, y_label, DataFrame, subset_ylim, name_image, plot_title):
    
    fig1 = plt.figure(num=0, clear=True, figsize=(7, 7))
    plt.title(plot_title, fontsize = 14)
    
    # First subplot
    plt.subplot(211)
    plt.xlabel(x_label)  
    plt.ylabel(y_label)
    plt.plot(DataFrame[x_label], DataFrame[y_label], '^g') 
    
    # Second subplot: subset to amplify y-axis scale
    plt.subplot(212)
    plt.xlabel(x_label)  
    plt.ylabel(y_label)
    subset_ratiosDataframe = DataFrame[DataFrame[y_label] < subset_ylim]
    plt.plot(subset_ratiosDataframe[x_label], subset_ratiosDataframe[y_label], '^c')  
    
    fig1.savefig(name_image+".png")  # If it is desired to save the figure
    plt.close(fig1)


# =============================================================================
# 2 subplots with the SAME x, y labels

    # First subplot: the axes comprise the whole extension of the data (x, y dimensions)
    # Second subplot: x-axis with UPPER limitation, 'subset_xlim', to amplify the scale
    
# =============================================================================

def two_subplots_subsetxlim(x_label, y_label, DataFrame, subset_xlim, name_image, plot_title):

    fig1 = plt.figure(num=0, clear=True, figsize=(7, 7))
    plt.title(plot_title, fontsize = 14)
    
    # First subplot
    plt.subplot(211)
    plt.xlabel(x_label)  
    plt.ylabel(y_label)
    plt.plot(DataFrame[x_label], DataFrame[y_label], '^g') 
    
    # Second subplot: subset to amplify x-axis scale
    plt.subplot(212)
    plt.xlabel(x_label)  
    plt.ylabel(y_label)
    subset_ratiosDataframe = DataFrame[DataFrame[x_label] < subset_xlim]
    plt.plot(subset_ratiosDataframe[x_label], subset_ratiosDataframe[y_label], '^c')  
    
    fig1.savefig(name_image+".png")  # If it is desired to save the figure
    plt.close(fig1)
    
    
# =============================================================================
# 2 subplots with the SAME x, y labels

    # First subplot: the axes comprise the whole extension of the data (x, y dimensions)
    # Second subplot: x-axis with LOWER limitation, 'subset_xlim', to amplify the scale
    
# =============================================================================

def two_subplots_subset_x_lowerlim(x_label, y_label, DataFrame, subset_xlim, name_image, plot_title):

    fig1 = plt.figure(num=0, clear=True, figsize=(7, 7))
    plt.title(plot_title, fontsize = 14)
    
    # First subplot
    plt.subplot(211)
    plt.xlabel(x_label)  
    plt.ylabel(y_label)
    plt.plot(DataFrame[x_label], DataFrame[y_label], '^g') 
    
    # Second subplot: subset to amplify x-axis scale
    plt.subplot(212)
    plt.xlabel(x_label)  
    plt.ylabel(y_label)
    subset_ratiosDataframe = DataFrame[DataFrame[x_label] > subset_xlim]
    plt.plot(subset_ratiosDataframe[x_label], subset_ratiosDataframe[y_label], '^c')  
    
    fig1.savefig(name_image+".png")  # If it is desired to save the figure
    plt.close(fig1)


# =============================================================================
# 2 subplots with the SAME x, y labels

    # First subplot: the axes comprise the whole extension of the data (x, y dimensions)
    # Second subplot: x-axis and y-axis with UPPER limitation, 'subset_xlim' & 'subset_ylim', 
        # to amplify the scale
    
# =============================================================================

def two_subplots_subsetlims(x_label, y_label, DataFrame, subset_xlim, subset_ylim, name_image, plot_title):

    fig1 = plt.figure(num=0, clear=True, figsize=(7, 7))
    plt.title(plot_title, fontsize = 14)
    
    # First subplot
    plt.subplot(211)
    plt.xlabel(x_label)  
    plt.ylabel(y_label)
    plt.plot(DataFrame[x_label], DataFrame[y_label], '^g') 
    
    # Second subplot: subset to amplify x,y-axes scale
    plt.subplot(212)
    plt.xlabel(x_label)  
    plt.ylabel(y_label)
    subset_ratiosDataframe = DataFrame[DataFrame[x_label] < subset_xlim]
    subset_ratiosDataframe = subset_ratiosDataframe[subset_ratiosDataframe[y_label] < subset_ylim]
    plt.plot(subset_ratiosDataframe[x_label], subset_ratiosDataframe[y_label], '^c')  
    
    fig1.savefig(name_image+".png")  # If it is desired to save the figure
    plt.close(fig1)
    
    
# =============================================================================
# 2 subplots with the TWO DIFFERENT y labels (same x label)

    # First subplot: x_label, y_label1
    # Second subplot: x_label, y_label2
    
# =============================================================================
    
def two_plots_twolabels(x_label, y_label1, y_label2, DataFrame, name_image, plot_title):

    fig1 = plt.figure(num=0, clear=True, figsize=(7, 7))
    plt.title(plot_title, fontsize = 14)
    
    # First subplot
    plt.subplot(211)
    plt.xlabel(x_label)  
    plt.ylabel(y_label1)
    plt.plot(DataFrame[x_label], DataFrame[y_label1], '^g') 
    
    # Second subplot: subset to amplify y-axis scale
    plt.subplot(212)
    plt.xlabel(x_label)  
    plt.ylabel(y_label2)
    plt.plot(DataFrame[x_label], DataFrame[y_label2], '^c')  
    
    fig1.savefig(name_image+".png")  # If it is desired to save the figure
    plt.close(fig1)
    
    
# =============================================================================
# 2 subplots with the TWO DIFFERENT y labels (same x label)
# x-axis with UPPER limitation, 'xlim', to amplify the scale

    # First subplot: x_label, y_label1
    # Second subplot: x_label, y_label2
    
# =============================================================================
    
def two_plots_twolabels_xlim(x_label, y_label1, y_label2, DataFrame, xlim, name_image, plot_title):

    fig1 = plt.figure(num=0, clear=True, figsize=(7, 7))
    subset_ratiosDataframe = DataFrame[DataFrame[x_label] < xlim]
    plt.title(plot_title, fontsize = 14)
    
    # First subplot
    plt.subplot(211)
    plt.xlabel(x_label)  
    plt.ylabel(y_label1)
    plt.plot(subset_ratiosDataframe[x_label], subset_ratiosDataframe[y_label1], '^g') 
    
    # Second subplot: subset to amplify y-axis scale
    plt.subplot(212)
    plt.xlabel(x_label)  
    plt.ylabel(y_label2)
    plt.plot(subset_ratiosDataframe[x_label], subset_ratiosDataframe[y_label2], '^c')  
    
    fig1.savefig(name_image+".png")  # If it is desired to save the figure
    plt.close(fig1)
    

# =============================================================================
# 2 subplots with the TWO DIFFERENT y labels (same x label)
# x-axis with LOWER limitation, 'xlim', to amplify the scale

    # First subplot: x_label, y_label1
    # Second subplot: x_label, y_label2
    
# =============================================================================

def two_plots_twolabels_x_lowerlim(x_label, y_label1, y_label2, DataFrame, xlim, name_image, plot_title):

    fig1 = plt.figure(num=0, clear=True, figsize=(7, 7))
    subset_ratiosDataframe = DataFrame[DataFrame[x_label] > xlim]
    plt.title(plot_title, fontsize = 14)
    
    # First subplot
    plt.subplot(211)
    plt.xlabel(x_label)  
    plt.ylabel(y_label1)
    plt.plot(subset_ratiosDataframe[x_label], subset_ratiosDataframe[y_label1], '^g') 
    
    # Second subplot: subset to amplify y-axis scale
    plt.subplot(212)
    plt.xlabel(x_label)  
    plt.ylabel(y_label2)
    plt.plot(subset_ratiosDataframe[x_label], subset_ratiosDataframe[y_label2], '^c')  
    
    fig1.savefig(name_image+".png")  # If it is desired to save the figure
    plt.close(fig1)
    
    
# =============================================================================
# One plot (x_label, y_label)
# =============================================================================

def one_plot(x_label, y_label, DataFrame, name_image, plot_title):

    fig2 = plt.figure(num=0, clear=True, figsize=(7, 7))
    
    # One Plot
    plt.subplot(111)
    plt.xlabel(x_label)  
    plt.ylabel(y_label)
    plt.plot(DataFrame[x_label], DataFrame[y_label], '^c')  
    plt.title(plot_title, fontsize = 14)
    
    fig2.savefig(name_image+".png")  # If it is desired to save the figure
    plt.close(fig2)
    
    
# =============================================================================
# One plot (x_label, y_label)
# x-axis with UPPER limitation, 'xlim', to amplify the scale
# =============================================================================
    
def one_plot_xlim(x_label, y_label, DataFrame, xlim, name_image, plot_title):

    fig2 = plt.figure(num=0, clear=True, figsize=(7, 7))
    subset_ratiosDataframe = DataFrame[DataFrame[x_label] < xlim]
    
    # One Plot
    plt.subplot(111)
    plt.xlabel(x_label)  
    plt.ylabel(y_label)
    plt.plot(subset_ratiosDataframe[x_label], subset_ratiosDataframe[y_label], '^c')  
    plt.title(plot_title, fontsize = 14)
    
    fig2.savefig(name_image+".png")  # If it is desired to save the figure
    plt.close(fig2)


# =============================================================================
# One plot (x_label, y_label)
# x-axis with LOWER limitation, 'xlim', to amplify the scale
# =============================================================================

def one_plot_x_lowerlim(x_label, y_label, DataFrame, xlim, name_image, plot_title):

    fig2 = plt.figure(num=0, clear=True, figsize=(7, 7))
    subset_ratiosDataframe = DataFrame[DataFrame[x_label] > xlim]
    
    # One Plot
    plt.subplot(111)
    plt.xlabel(x_label)  
    plt.ylabel(y_label)
    plt.plot(subset_ratiosDataframe[x_label], subset_ratiosDataframe[y_label], '^c')  
    plt.title(plot_title, fontsize = 14)
    
    fig2.savefig(name_image+".png")  # If it is desired to save the figure
    plt.close(fig2)
    
    
# =============================================================================
# Basic BoxPlot (x_var, y_var)
# Default whiskers: 1.5*(IQR)
# =============================================================================

def basic_boxplot(dataframe, x_var, y_var, x_label, y_label, filename, plot_title):
    
    fig = plt.figure(num=0, clear=True, figsize=(7, 7))
    ax_boxplot = sns.boxplot(x = x_var, y = y_var, data = dataframe)
    ax_boxplot.set(xlabel = x_label, ylabel = y_label)
    
    plt.title(plot_title, fontsize = 14)
    fig.savefig(filename+".png")
    plt.close(fig)


# =============================================================================
# Basic BoxPlot (x_var, y_var)
# Default whiskers: 1.5*(IQR)
    # 'ylims': (lower, upper) to limit y-axis scale
    # Note that 'ylims' should be a tuple: ylims[0]: lower limit; ylims[1]: upper limit
# =============================================================================

def basic_boxplot_ylims(dataframe, x_var, y_var, x_label, y_label, filename, ylims, plot_title):
    
    fig = plt.figure(num=0, clear=True, figsize=(7, 7))
    plt.ylim(ylims[0], ylims[1])
    ax_boxplot = sns.boxplot(x = x_var, y = y_var, data = dataframe)
    ax_boxplot.set(xlabel = x_label, ylabel = y_label)
    
    plt.title(plot_title, fontsize = 14)
    fig.savefig(filename+".png")
    plt.close(fig)


# =============================================================================
# Basic ScatterPlot (x_col, y_col)
# =============================================================================

def basic_scatter(dataframe, x_col, y_col, x_label, y_label, filename, plot_title):
    
    fig = plt.figure(num=0, clear=True, figsize=(7, 7))
    ax_cat = sns.stripplot(x=x_col, y=y_col, jitter = True, data = dataframe)
    ax_cat.set(xlabel=x_label, ylabel=y_label)
    
    plt.title(plot_title, fontsize = 14)
    # plt.xticks(rotation=20)
    fig.savefig(filename+".png")
    plt.close(fig)
    

# =============================================================================
# Basic ScatterPlot (x_col, y_col)
# y-axis with UPPER limitation, 'ylim', to amplify the scale
# =============================================================================

def basic_scatter_ylim(dataframe, x_col, y_col, x_label, y_label, ylim, filename, plot_title):
    fig = plt.figure(num=0, clear=True, figsize=(7, 7))
    ax_cat = sns.stripplot(x=x_col, y=y_col, jitter = True, data = dataframe)
    ax_cat.set(xlabel=x_label, ylabel=y_label)
    plt.ylim(0, ylim)
    
    plt.title(plot_title, fontsize = 14)
    fig.savefig(filename+".png")
    plt.close(fig)


# =============================================================================
# BoxPlot + ScatterPlot (x_var, y_var)
# Default whiskers: 1.5*(IQR)
# =============================================================================

# reverse_colum: if the dataframe series to be plotted have to be read from the bottom
    # to the top, instead of the other way around

def basic_boxplot_scatter(dataframe, x_var, y_var, x_label, y_label, filename, plot_title, reverse_dataframe = False):
    
    fig = plt.figure(num=0, clear=True, figsize=(7, 7))
    
    if reverse_dataframe:
        ax_boxplot = sns.boxplot(x = x_var, y = y_var, data = dataframe[::-1], boxprops=dict(alpha=0.2))
        sns.stripplot(x=x_var, y=y_var, jitter = True, data = dataframe[::-1])
    else:
        ax_boxplot = sns.boxplot(x = x_var, y = y_var, data = dataframe, boxprops=dict(alpha=0.2))
        sns.stripplot(x=x_var, y=y_var, jitter = True, data = dataframe)
        
    ax_boxplot.set(xlabel = x_label, ylabel = y_label)
    
    plt.title(plot_title, fontsize = 14)
    # plt.xticks(rotation=20)
    fig.savefig(filename+".png")
    plt.close(fig)



# =============================================================================
# BoxPlot + ScatterPlot (x_var, y_var)
# Default whiskers: 1.5*(IQR)
# Upper y-limit: 
# =============================================================================

def basic_boxplot_scatter_upper_ylim(dataframe, x_var, y_var, x_label, y_label, filename, plot_title, upper_ylim):
    
    fig = plt.figure(num=0, clear=True, figsize=(7, 7))
    ax_boxplot = sns.boxplot(x = x_var, y = y_var, data = dataframe, boxprops=dict(alpha=0.2))
    sns.stripplot(x=x_var, y=y_var, jitter = True, data = dataframe)
    ax_boxplot.set(xlabel = x_label, ylabel = y_label)
    
    plt.title(plot_title, fontsize = 14)
    plt.ylim(0, upper_ylim)
    fig.savefig(filename+".png")
    plt.close(fig)




























