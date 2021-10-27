23th September 2021
IVÁN MARTÍN MARTÍN
National Center for Biotechnology, CNB-CSIC (Madrid, Spain)
===========================================================

The following repository contains Python tools for FLYCOP (FLexible sYnthetic Consortium OPtimization), a framework for the simulation and optimization of microbial communities by using genome-scale models (see https://github.com/beatrizgj/FLYCOP).

CONTENTS
========

1) Three examples for the new pipeline of selection of consortium architecture
-----------------------------------------------------------------------------
	FLYCOP is now able of selecting the best consortium architecture for a given metabolic objective: for instance, if a metabolic path should be divided into two, three or more strains (i.e. GEMs) for optimizing community fitness and final production objectives. The test cases are:

		-  SelectConsortiumArchitecture_2Ssakuranetine, for production of 2S-sakuranetine in a 2-model or 3-model consortium.

		- SelectConsortiumArchitecture_6GeranylNar, for production of 6-Geranyl Naringenin production in a 2-model or 3-model consortium.

		- SelectConsortiumArchitecture_GlycNaringenin, for production of glycosilated naringenin in a 2-model or 3-model consortium.

	These three test cases are further analyzed by using Python tools for output analysis in folder ConsortiaSelectionOutputAnalysis_FLYCOP.


2) ConsortiaSelectionOutputAnalysis_FLYCOP
------------------------------------------

	FLYCOP output analysis tools for the new pipeline on selection of consortium architecture. Files adapted to test cases:

		-  SelectConsortiumArchitecture_2Ssakuranetine
		- SelectConsortiumArchitecture_6GeranylNar

	The main tools are focused on: i) a general analysis of configurations; ii) a pairwise variable analysis of variables considered in the FLYCOP execution and current community project; iii) a biomass and production analysis for the community. The analysis is performed by means of Pandas and several plotting alternatives (i.e. heatmaps, pairwise matrices, boxplots and scatterplots, raw statistics, etc.).

	See code documentation on each file and reports explaining results in each individual pipeline test case.


3) GeneralOutputAnalysis_FLYCOP
-------------------------------

	FLYCOP output analysis tools for the basic pipeline (https://github.com/beatrizgj/FLYCOP), without selection of consortium architecture. See description of files and main analysis utilities within the folder README.txt file.

	The main focus of the analysis ares: i) classification of error configurations; ii) statistical analysis of input and output variables and further plotting; iii) analysis of configurations in terms of fitness ranks; iv) script of comparison of different FLYCOP runs (i.e. different in silico experiments for a given consortium, to be compared among them).


Footnote1: examples of input variables can be initial biomass for each microbe model, carbon or nitrogen uptake rates, etc. Moreover, examples of output variables can be final production of the metabolite of interest, fitness values, final biomass for each of the microbes or for the whole community, etc.