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

Example:
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

Startup directory must contain the following files: NH3.r2SCAN-3c.SMD(H2O).xyz and NH3.r2SCAN-3c.SMD(H2O).hess

### logP.py
Run:
```
logP.py [-h] --job FILE [FILE ...] [-n NTHREADS] [-v]
```
FILE - file name atomic coordinates (in XYZ format)  
NTHREADS - number of threads

The script contains variables that you can override according to your own settings:
- WORK_DIR  
Scratch directory.
- ORCA_DIR  
The directory where the ORCA package is installed.

Example:
```
logP.py --job NH3.r2SCAN-3c.SMD\(H2O\).xyz HNCO.r2SCAN-3c.SMD\(H2O\).xyz -n 6
```
```
For job NH3 LogP = -1.2798004583245164
Job execution time  :  90.885  sec.
Total execution time:  90.885  sec.

For job HNCO LogP = 0.648563488539062
Job execution time  :  156.961  sec.
Total execution time:  247.846  sec.
```
The comment for the job is taken from the comment line (second) of the file.

Geometry optimization in water and octanol is performed using the B3LYP-D4/def2-SVPD method and SMD models for the solvent. The solvation energy is calculated using the COSMO-RS model. Only solvation energies are taken into account, the vibrational-rotational energies are assumed to be the same in both solvents.

### cosmo-rs.py
Run:
```
cosmo-rs.py [-h] --job FILE [FILE ...] --method METHOD [--solventfile FILE] [--solvent SOLVENT] [-n NTHREADS] [-v] [-c CHARGE] [--novacuum [NOVACUUM ...]]

```
FILE - file name atomic coordinates (in XYZ format)  
METHOD - method for calculated properties in vacuum  
solventfile - solvent file for calculate free energy (see ORCA6 manual, page 1027)  
solvent - solvent name for calculate free energy (see ORCA6 manual, table of solvents), default water  
CHARGE - charge of system, dafault 0  
NOVACUUM - skip calculation in vacuum  
NTHREADS - number of threads

The script contains variables that you can override according to your own settings:
- WORK_DIR  
Scratch directory.
- ORCA_DIR  
The directory where the ORCA package is installed.

Example:
```
cosmo-rs.py --job NH3.r2SCAN-3c.SMD\(H2O\).xyz --method "r2SCAN-3c" --solvent "ethanol" -n 6
```
```
Job = NH3.r2SCAN-3c.SMD(H2O).xyz
Job = NH3.r2SCAN-3c.SMD(H2O).xyz
Free energy in gas     :  -56.525536  Hartree
Electronic energy      :  -56.541858  Hartree
Free energy solvalation:  -0.005961  Hartree
Job execution time  :  20.506  sec.
Total execution time:  20.506  sec.

Job = HNCO.r2SCAN-3c.SMD(H2O).xyz
Free energy in gas     :  -168.663383  Hartree
Electronic energy      :  -168.661779  Hartree
Free energy solvalation:  -0.006904  Hartree
Job execution time  :  25.769  sec.
Total execution time:  46.275  sec.
```
The comment for the job is taken from the comment line (second) of the file.

Geometry optimization in water and octanol is performed using the B3LYP-D4/def2-SVPD method and SMD models for the solvent. The solvation energy is calculated using the COSMO-RS model. Only solvation energies are taken into account, the vibrational-rotational energies are assumed to be the same in both solvents.
