23th SEPTEMBER 2021
OUTPUT ANALYSIS AFTER FLYCOP
Pipeline of Selection of Consortium Architecture
================================================
================================================

Description of folder organization within a 'SelectConsortiumArchitecture case' for further output analysis, using the current pipeline.


FLYCOP_analysis FOLDER
######################

In this folder, there should be:

	* InputFiles folder for proper working of the present pipeline (see description within each individual Python script)
	* configurationResults_consArchitecture.xlsx file for the FLYCOP run to be analyzed



Scripts FOLDER
##############

A. GeneralAnalysis
----------------
	
	- Obtain desired ratios (for input and output variables)
	- General display of FLYCOP configurations
	- Input variable analysis
	

B. PairwiseVariableAnalysis
-------------------------

	- Scatterplot with SD vs. fitness values
	- Pairgrid and heatmap for input variable, depending on consortium architecture
	
	
C. BiomassProductionAnalysis.py
-------------------------------

	- Specific study of individual biomass (scatter + boxplot)
	- Production study (scatter + boxplot, statistical description)
	
	

Utilities FOLDER
################

Two Python files with plotting functions used in main scripts (see further description within each script).

	* MetabolicParameterPlotting.py
	* Plotting
	


Report FOLDER
################

If an output analysis report has already been written.


* general_output_analysis.sh FILE
#################################

Main bash file to be run in order to use the current pipeline. See description within the script itself.
	









