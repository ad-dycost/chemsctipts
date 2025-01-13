#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  free_energy_liquid.py
#  
#  Copyright 2023 Ad <ad.dycost@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

import sys, os, re, argparse, math, glob, time
from subprocess import Popen, PIPE

T_0 = time.time()

VERSION = 0.6

HISTORY = '''
			0.01 -- start project
			0.1 -- added all base operations
			0.2 -- added processed of errors in ORCA jobs
			0.3 -- added input temperature from command-line arguments
			0.4 -- added all calculations
			0.5 -- added formatted output
			0.51 -- fix minor bags
			0.6 -- change version ORCA to 6
'''

# working directories, may be changed of user
WORK_DIR = "/mnt/scratch/orca/"
ORCA_DIR = "/mnt/programs/orca6/"
ORCA = ORCA_DIR + "orca"

# Constants
BOHR_to_ANGS = 0.52917721
HARTREE = 2625.49953026
K_BOLTZMANN = 1.380649 * pow(10,- 23)
H_PLANCK = 6.62607015 * pow(10, -34)
R_GAZ_CONST = 8.314
AMU = 1.66053873 * pow(10, -27)

# function for parsing command line parameters
def args_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument ("--job", metavar="FILE", required=True, help = 'jobname for files with coordinates data (XYZ format) and hessian data (ORCA format)')
	parser.add_argument ("-c", "--charge", type=int, default=0, help = 'charge of system')
	parser.add_argument ("-t", "--temperature", nargs='+', default=[298], help = 'temperature')

	return parser


parser = args_parser()
namespace = parser.parse_args()

# read parameters from command-line arguments
filename_xyz = namespace.job + ".xyz"
filename_hess = namespace.job + ".hess"
charge = namespace.charge
temperature = list(map(float,namespace.temperature))

# read data from files
XYZ_file = open(filename_xyz, "r")
XYZ_data = XYZ_file.read()
XYZ_file.close()
N_atoms = int(XYZ_data.partition("\n")[0])
XYZ_coords = "\n".join(XYZ_data.split("\n")[2:2 + N_atoms])

INPUT_DIR = os.getcwd()

# function calculate of free volume, angstrom^3
def V_free(V_mol, V_cav):
	return math.pow((math.pow(V_cav, 1/3.) - math.pow(V_mol, 1/3.)) * BOHR_to_ANGS, 3.)

# function calculate of product S*T, Hartree
def ST_liquid(V_free, T, m):
	Lambda = H_PLANCK / math.sqrt (2 * math.pi * m * AMU * K_BOLTZMANN * T)
	return T * R_GAZ_CONST * (2.5 + math.log(V_free / math.pow(Lambda  * math.pow(10, 10), 3))) / 1000. / HARTREE

def str_f(f):
	return "%.8f\t" % f


# templates from job

# Volume_Bader.inp
Volume_Bader = '''* xyz ''' + str(charge) + ''' 1 \n''' + XYZ_coords + '''
*

! RHF SVP NOITER

%cpcm
	smd true
	SMDsolvent "water"
	num_leb 770
	radius[8] 1.7
	radius[1] 1.52
	radius[6] 1.92
	radius[16] 2.14
	radius[7] 1.79
	radius[17] 2.08
	radius[9] 1.61
	radius[15] 2.23
	radius[35] 2.27
end'''

# Volume_IDSCRF.inp
Volume_IDSCRF = '''* xyz ''' + str(charge) + ''' 1 \n''' + XYZ_coords + '''
*

! RHF SVP NOITER

%cpcm
	smd true
	SMDsolvent "water"
	num_leb 770
	radius[8] 1.87
	radius[1] 1.77
	radius[6] 2.22
	radius[16] 2.48
	radius[7] 2.05
	radius[17] 2.39
	radius[9] 1.89
	radius[15] 2.52
	radius[35] 2.54
end'''

# Thermochem.inp
Thermochem = '''! printthermochem

%geom
	inhessname "''' + INPUT_DIR + "/" + filename_hess + '''"
end

%freq
	temp ''' + ",".join(list(map(str, temperature))) + '''
 end

%cpcm
	smd true
	SMDsolvent "water"
end

* xyz ''' + str(charge) + ''' 1 \n''' + XYZ_coords + '''\n*'''

# regular expression for parsing output files
EXPRESSIONS = {}
EXPRESSIONS["Volume"] = re.compile(r"Cavity Volume\s*...\s*" + r"(.*?)" + "\n")
EXPRESSIONS["Molar"] = re.compile(r"Total Mass\s*...\s*" + r"(.*?)" + "AMU\n")
EXPRESSIONS["G"] = re.compile(r"Final Gibbs free energy\s*...\s*" + r"(.*?)" + "Eh\n")
EXPRESSIONS["ST"] = re.compile(r"Translational entropy\s*...\s*" + r"(.*?)" + r"Eh\s*\d*\.\d*\s*kcal\/mol\n")
EXPRESSIONS["SR"] = re.compile(r"Rotational entropy\s*...\s*" + r"(.*?)" + r"Eh\s*\d*\.\d*\s*kcal\/mol\n")


# start of job and processing of results
os.chdir(WORK_DIR)
DATA_RES = {}

for num, input_data in enumerate([Thermochem, Volume_IDSCRF, Volume_Bader]):
	input_filename = "free_energy.inp"
	output_filename = "free_energy.out"
	f = open(input_filename, "w")
	f.write(input_data)
	f.close()
	cmdline = 'nice -n 10 %s "%s" > "%s"' % (ORCA, input_filename, output_filename)
	proc = Popen(cmdline, shell=True, stdout=PIPE, stderr=PIPE, executable = '/bin/bash')
	proc.wait()
	f = open(output_filename, "r")
	DATA_RES[num] = f.read()
	f.close()
	for f in glob.glob("free_energy*"):
		os.remove(f)
	

try:
# calculate free volume for liquid
	V_CAV = float(EXPRESSIONS["Volume"].findall(DATA_RES[1])[0])
	V_MOL = float(EXPRESSIONS["Volume"].findall(DATA_RES[2])[0])
	V_FREE = V_free(V_MOL, V_CAV)
	
# read other properierties
	MOLAR_M = float(EXPRESSIONS["Molar"].findall(DATA_RES[0])[0])
	GIBBS_GAS = list(map(float, EXPRESSIONS["G"].findall(DATA_RES[0])))
	ST_GAS = list(map(float, EXPRESSIONS["ST"].findall(DATA_RES[0])))
	SR_GAS = list(map(float, EXPRESSIONS["SR"].findall(DATA_RES[0])))
except:
	os.chdir(INPUT_DIR)
	f = open("error.log", "w")
	f.write(DATA_RES[1])
	f.write("\n-----------------------------------------------\n")
	f.write(DATA_RES[2])
	f.write("\n-----------------------------------------------\n")
	f.write(DATA_RES[3])
	f.write("\n-----------------------------------------------\n")
	f.close()

# calculate translational entropy in liquid
N_POINTS = len(temperature)
ST_LIQUID = list(map(ST_liquid, [V_FREE] * N_POINTS, temperature, [MOLAR_M] * N_POINTS))

# calculate total Gibbs free energy in liquid
G_LIQUID = list(map(lambda x, y, z: x + y - z, GIBBS_GAS, ST_GAS, ST_LIQUID))

# return of results
print("Molar mass, amu".ljust(45, " "), " =", MOLAR_M)
print("Volume Bader, Bohr^3".ljust(45, " "), " =", V_MOL)
print("Volume IDSCRF, Bohr^3".ljust(45, " "), " =", V_CAV)
print("Free Volume, Angsrtrom^3".ljust(45, " "), " = %.8f" % V_FREE)
print("Temperature, Kelvin".ljust(45, " "), " =", "\t\t".join(map(str, temperature)))
print("Total Gibbs in gas, Hartree".ljust(45, " "), " =", "\t".join(map(str, GIBBS_GAS)))
print("Translational entropy in gas, Hartree".ljust(45, " "), " =", "\t".join(map(str, ST_GAS)))
print("Rotational entropy in gas, Hartree".ljust(45, " "), " =", "\t".join(map(str, SR_GAS)))
print("Translational entropy in liquid, Hartree".ljust(45, " "), " =", "".join(list(map(str_f, ST_LIQUID))))
print("Total Gibbs energy in liquid, Hartree".ljust(45, " "), " =", "".join(list(map(str_f, G_LIQUID))))


print("Total execution time: ", "%.3f" % (time.time() - T_0), " sec.")
