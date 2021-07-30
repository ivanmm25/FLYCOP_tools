30th JULY 2021
OUTPUT ANALYSIS AFTER FLYCOP
Pipeline of Selection of Consortium Architecture
================================================
================================================

A. BasicAnalysis
----------------
	
	- Obtain desired ratios (for input and output variables)
	- Plot fitness vs. input and output parameters for: i) acceptable and NonOptimal configurations; ii) Acceptable configurations

	Required files: configurationResults_consArchitecture.xlsx, BasicAnalysis_specifications.txt. 
	Script of command line use.
	

B. FitnessRanksComparison
-------------------------

	- Building of fitness ranks
	- Ulterior comparison and plotting
	
	FUNCTIONS FROM 'UTILITIES' (see next section)
	Script of command line use.
	
	
C. UTILITIES
------------	
	
	- Utility to divide a table of configurationResults in a series of ranks, depending on the fitness (i.e. fitness ranks, with lower and upper limit)
		
			- Number of fitness ranks set by the user
			- The number of configurations in the execution also has to be provided
			- The distribution of configurations in the different fitness ranks might not always be even
		
		* Automatic building of fitness rank (FUNCTION: build_fitness_ranks)
		* Previous definition of fitness rank by the user (FUNCTION: fitness_ranks_by_user)
	
		
	- Utility to colorize the column on fitness values in the configurationResults table, according to the fitness ranks previously defined (visual purposes) (FUNCTION: organize_colorize_fitness_ranks)
	
	- Excel Unifier: individual ExcelFiles in a unique workbook with several worksheets (FUNCTION: multiple_excel_unifier). INCONVENIENCE: it does not keep the 'fitFunc' column colorized by fitness ranks.
	
	
	- Utility to define a new column of categorical classification of fitness ranks for ulterior (categorical) plotting (BoxPlot representation by fitness ranks). Example: FR1 (fitness rank 1), FR2, etc.
	
		* Categories are represented by the interval itself in string format, i.e. 25-50. (FUNCTION: plotting_categorical_fitnessRanks)
		* Categories are represented by keywords such as 'FR1' (fitness rank 1). (FUNCTION: plotting_categorical_fitnessRanks_by_keywords)

	
	Required files: configurationResults_consArchitecture.xlsx, fitness_ranks_user.txt, plotting_parameters_by_fitness.
	
	
D. TO-DO
--------

	* Utility to retrieve Statistical Description of each of the fitness ranks in an external file
	* New function for building fitness ranks where the intervals are properly defined as quartiles (groups of closer fitness values), instead of having groups with an approximate equivalent number of configurations in each of them (without regarding whether the values are closer or more separated between them)
	
	* MULTIPLE COMPARISON OF DIFFERENT CONSORTIUM ARCHITECTURES
	
		a. By fitness ranks
		b. Considering the whole set of valid fitness values







