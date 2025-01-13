# chemsctipts
A set of scripts for quantum chemists.  
## Description
All scripts are a shell over the ORCA software package and are aimed at automating and simplifying the execution of certain types of calculations.  
Currently contains the following scripts:
- startorca.py  
Convenient launch of jobs in ORCA, supports launching multiple files and specifying the number of threads.
- free_energy_liquid.py  
Calculation of the Gibbs free energy in the solvent using the method given in 10.1039/D2CP04720A.
- logP.py  
Calculation of the lipophilicity index using continuous solvent models.
- cosmo-rs.py  
Calculation of solvation energy using the COSMO-RS model.
- orca2xyz.py  
Extracting trajectories from ORCA output files.
## Requirements:
- ORCA 6
- Python 3
