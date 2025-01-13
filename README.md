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

### free_energy_liquid.py
Run:
```
free_energy_liquid.py [-h] --job FILE [-c CHARGE] [-t TEMPERATURE [TEMPERATURE ...]]
```
FILE - file name (without extension) with atomic coordinates (in XYZ format) and Hessian are taken from previous job on geometry optimization and Hessian calculation in ORCA  
CHARGE - charge of system, default 0  
TEMPERATURE - temperarure(s) in Kelvin at which thermodynamic parameters will be calculated (separated by spaces), default 298

The script contains variables that you can override according to your own settings:
- WORK_DIR  
Scratch directory.
- ORCA_DIR  
The directory where the ORCA package is installed.

Example (startup directory must contain the following files: NH3.r2SCAN-3c.SMD(H2O).xyz and NH3.r2SCAN-3c.SMD(H2O).hess):
```
free_energy_liquid.py --job "NH3.r2SCAN-3c.SMD(H2O)" -t 400 600
```
```
Molar mass, amu                                = 17.03
Volume Bader, Bohr^3                           = 252.1761
Volume IDSCRF, Bohr^3                          = 361.1701
Free Volume, Angsrtrom^3                       = 0.07691522
Temperature, Kelvin                            = 400.0		600.0
Total Gibbs in gas, Hartree                    = 0.00834676	-0.00776754
Translational entropy in gas, Hartree          = 0.02288501	0.03625355
Rotational entropy in gas, Hartree             = 0.00785661	0.01294053
Translational entropy in liquid, Hartree       = 0.00582050	0.00988632	
Total Gibbs energy in liquid, Hartree          = 0.02541127	0.01859969	
Total execution time:  1.722  sec.
```
The result given by the program is an addition for electronic energy.
