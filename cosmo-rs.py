#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  cosmo-rs.py
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

import sys, os, re, argparse, math, glob, time, shutil
from subprocess import Popen, PIPE

T_0 = time.time()
T_00 = T_0

VERSION = "0.13"
HISTORY = '''
			0.01 -- start project
			0.1 -- added choice method for optimisation
			0.11 -- added support geometry file for solvent
			0.12 -- added multithreading + fix minor bugs
			0.13 -- added the option to skip calculation in vacuum
'''

# working directories, may be changed of user
WORK_DIR = "/mnt/scratch/orca/"
ORCA_DIR = "/mnt/programs/orca6/"
ORCA = ORCA_DIR + "orca"

# Constants
HARTREE = 2625.49953026
R_GAZ_CONST = 8.314
T = 298.15



# function for parsing command line parameters
def args_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument ("--job", metavar="FILE", nargs='+', required=True, help = 'jobname for files with coordinates data (XYZ format)')
	parser.add_argument ("--method", type=str, required=True, help = 'method for calculated properties in vacuum')
	parser.add_argument ("--solventfile", metavar="FILE", help = 'solvent file for calculate free energy')
	parser.add_argument ("--solvent", type=str, default="water", help = 'solvent for calculate free energy')
	parser.add_argument ("-n", "--nthreads", type=int, default=1, help = 'number of CPUs')
	parser.add_argument ("-v", "--version", action="version", version=VERSION, help = 'print version')
	parser.add_argument ("-c", "--charge", type=int, default=0, help = 'charge of system')
	parser.add_argument ("--novacuum", help = 'to skip calculation in vacuum', nargs='*')
	return parser


parser = args_parser()
namespace = parser.parse_args()

# read parameters from command-line arguments
filenames_xyz = namespace.job
NPROC = namespace.nthreads
SOLVENT = namespace.solvent
METHOD = namespace.method
CHARGE = str(namespace.charge)
SOLVENTFILE = namespace.solventfile

# read coordinates and name from XYZ file
def read_xyz_coord(file_xyz):
	# read data from files
	XYZ_file = open(file_xyz, "r")
	XYZ_data = XYZ_file.read()
	XYZ_file.close()
	data =  XYZ_data.split("\n")
	N_atoms = int(data[0])
	job_name = data[1].lstrip()
	XYZ_coords = "\n".join(data[2:2 + N_atoms])
	return N_atoms, job_name, XYZ_coords


PAR_STR = '''%pal nprocs ''' + str(NPROC) + ''' end\n'''
INPUT_DIR = os.getcwd()


# templates from job
def job_CRS(coords):
	if SOLVENTFILE:
		par = '''%cosmors
	solventfilename "''' + INPUT_DIR + "/" + ".".join(SOLVENTFILE.split(".")[:-1]) + '''"
end\n'''
	else:
		par = '''%cosmors
	solvent "''' + SOLVENT + '''"
end\n'''
	return PAR_STR + par + '''* xyz ''' + CHARGE + ''' 1 \n''' + coords + '''\n*'''

def job_vac(coords):
	if namespace.novacuum == None:
		res = PAR_STR + ''' ! ''' + METHOD + '''
! freq KDIIS DAMP SOSCF LSHIFT rijcosx

* xyz ''' + CHARGE + ''' 1 \n''' + coords + '''\n*'''
	else:
		res = '''! NOITER
* xyz ''' + CHARGE + ''' 1 \n''' + coords + '''\n*'''
	return res


# Regular expression for parsing files
EXPRESSIONS = {}
EXPRESSIONS["G_solv"] = re.compile(r"Free\ energy\ of\ solvation\ \(dGsolv\)\  :" +r" \s*"  + r"(.*?)" + r"\sEh")
EXPRESSIONS["G_gas"] = re.compile(r"Final Gibbs free energy\s*...\s*" + r"(.*?)" + "Eh\n")
EXPRESSIONS["E_el"] = re.compile(r"FINAL\ SINGLE\ POINT\ ENERGY\s*"  + r"(.*?)" + r"\n")

# start of job and processing of results
for job in filenames_xyz:
	print("Job = " + job)
	os.chdir(INPUT_DIR)
	N_atoms, job_name, coords = read_xyz_coord(job)
	if job_name == "":
		job_name = job
	os.chdir(WORK_DIR)
	JOB_1 = job_vac(coords)
	JOB_2 = job_CRS(coords)
	for num, input_data in enumerate([JOB_1, JOB_2]):
		input_filename = "active_job.inp"
		output_filename = "active_job.out"
		f = open(input_filename, "w")
		f.write(input_data)
		f.close()
		cmdline = 'nice -n 10 %s "%s" > "%s"' % (ORCA, input_filename, output_filename)
		proc = Popen(cmdline, shell=True, stdout=PIPE, stderr=PIPE, executable = '/bin/bash')
		proc.wait()
		f = open(output_filename, "r")
		DATA_RES = f.read()
		f.close()
		if num == 0 and namespace.novacuum == None:
			G_gas = float(EXPRESSIONS["G_gas"].findall(DATA_RES)[-1])
			E_el = float(EXPRESSIONS["E_el"].findall(DATA_RES)[-1])
			print("Free energy in gas     : ", "%f" % G_gas, " Hartree")
			print("Electronic energy      : ", "%f" % E_el, " Hartree")
		elif num == 1:
			G_solv = float(EXPRESSIONS["G_solv"].findall(DATA_RES)[-1])
			print("Free energy solvalation: ", "%f" % G_solv, " Hartree")
		for f in glob.glob("active_job*"):
			os.remove(f)
	print("Job execution time  : ", "%.3f" % (time.time() - T_0), " sec.")
	print("Total execution time: ", "%.3f" % (time.time() - T_00), " sec.\n")
	T_0 = time.time()
	os.chdir(INPUT_DIR)
