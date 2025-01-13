# chemsctipts
A set of scripts for quantum chemists.  
## Description
All scripts are an add-on to the ORCA software package and are aimed at automating and simplifying the execution of certain types of calculations.  
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
## Manual
### startorca.py
Run:
```
startorca.py N_proc INPUTS
```
N_proc - number of threads  
INPUTS - inpit files separated by spaces

The script contains variables that you can override according to your own settings:
- HOME_DIR  
Directory with input files and where calculation results will be copied.
- WORK_DIR  
Scratch directory.
- ORCA_DIR  
The directory where the ORCA package is installed.

In scratch directory, input files are renamed according to the template active_%Y-%m-%d_%H_%M_%S. This is done because ORCA does not accept special characters like "(", ")" in file names.
