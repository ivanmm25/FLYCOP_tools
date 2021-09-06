The current project (EvaluateConsortiumArch_OptimizedPipeline_v2) with metilation of naringenin did not work for the consortium architecture of 2 models. A potential reason was a bad distribution of ratios for the FVA (Flux Variability Analysis) utility, in the iEC1364 model (producer of fructose, p-coumarate and 2S-sakuranetine).

In this folder, the scripts for the FLYCOP execution are the same than in "EvaluateConsortiumArch_OptimizedPipeline_v2" but with a modification of the PCS file: i) to allow only communities of 2 models (consortium architecture); and ii) to optimize the distribution of fluxes in the different FVA to happen for the model of iEC1364: fructose, p-coumarate and 2S-sakuranetine.

FURTHER RESTORED TO 2_models & 3_models! (AUGUST, 2021)


-----------------------------------------------------------------------
TESTED VERSION (July 01th, 2021)
FLYCOP PIPELINE FOR EVALUATION AND SELECTION OF CONSORTIUM ARCHITECTURE
***NARINGENIN METILATION: only 2_models, with FVA valoration by SMAC***
-----------------------------------------------------------------------

Consortium: E. coli iEC1364W, P.putida iJN1463
----------

Metabolic roles in a 2-model consortium.

	* Fructose and p-coumarate production, naringenin metilation: E. coli iEC1364W.
	* Malon and naringenin production, cobalamin production: P.putida iJN1463.
