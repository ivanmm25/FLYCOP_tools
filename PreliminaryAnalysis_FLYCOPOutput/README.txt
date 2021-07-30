09th APRIL - 10th JULY 2021
OUTPUT ANALYSIS AFTER FLYCOP
=============================
=============================

With the available output analysis scripts and depending on your research interests, here are some suggested analysis to be performed after executing FLYCOP.

A. ErrorAnalysis
----------------
	
	1. Obtaining the number of configurations with:
		- Acceptable Standard Deviation (SD)
		- Excessive Standard Deviation (SD)
		- Wrong configurations because of biomass exhaustion during the simulation ('ZeroDivisionError' Python error)
		
	2. Further evaluating those wrong configurations with 'ZeroDivisionError': related information in table format (exhausted microbe, final biomasses, final metabolite production)
	3. Further evaluating those configurations with excessive SD
	
	ASSOCIATED SCRIPTS: ConfigAnalysis_Error.py (2), ConfigAnalysis_NonError_SDexcess.py (3). See full description within the scripts themselves.
	
	
	
B. IndivFLYCOPRun_parameterAnalysis (input, output)
---------------------------------------------------

	1. Input Parameters Analysis. Script: InputParametersAnalysis.py
	2. Output Parameters Analysis. Script: OutputParametersAnalysis.py
	3. Statistical Analysis for input and output parameters. Script: InputOutputParameters_StatsAnalysis.py
		- count, mean, std, min, max, quartiles
	


C. IndividualFLYCOPComparison_fitnessRanks
------------------------------------------

	Description of the idea of fitness ranks
	----------------------------------------
The total number of final configurations obtained in the FLYCOP run are organized according to the final fitness value, in approximate even ranks. This operation would allow to understand how the input parameters condition the final fitness values (and the final production of the metabolite(s) of interest), and how the output parameters are related to each fitness interval.

Currently, the lower and upper limits for each fitness rank have to be stablished by hand. Afterwards, several fitness ranks can be compared in terms of input parameters or final production results.


	Related scripts
	---------------

	1.IndivFitnessRankAnalysis.py (individual comparison of the pre-selected fitness ranks in a given FLYCOP execution)
	2.IndivFitnessRankComparativeAnalysis.py (full comparison of all fitness ranks in a given FLYCOP execution. In this case, every configuration is included in a fitness rank within those previously defined).



D. MultipleFLYCOPrunsComparison
-------------------------------

	Description
	-----------
Several FLYCOP runs are compared in terms of their input and output parameters. Ideally, these FLYCOP runs should be equivalent except in one input (reference) parameter (or, at most, a few parameters). Thus the output differences between the different FLYCOP runs could be unequivocally attributed to the mentioned reference parameter.

	Scripts
	-------

	1. MultipleComparativeAnalysis.py
	


E. RELATED UTILITIES ('Utilities' folder)
-----------------------------------------

See full description within the auxiliary scripts themselves.

	- Plotting.py
	- FitnessRanks.py



F. OTHER CONSIDERATIONS
-----------------------

	* The current examples here displayed are specific to the example on naringenin production in the E.coli_iEC1364-P.putida_KT2440 consortium.
	
	* In case of using these scripts for a different metabolic example, they should be properly adapted as described in the comments within each of them.





