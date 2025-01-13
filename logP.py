#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  logP.py
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
T_00 = T_0

VERSION = "0.14"
HISTORY = '''
			0.01 -- start project
			0.10 -- add multiplity jobs, output in file, multiprocessing and other changes
			0.11 -- change output format
			0.12 -- add reading name job from comment string XYZ file
			0.13 -- add saving result of optimazation to XYZ file
			0.14 -- fix minor bags
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
	parser.add_argument ("-n", "--nthreads", type=int, default=1, help = 'number of CPUs')
	parser.add_argument ("-v", "--version", action="version", version=VERSION, help = 'print version')
	return parser


parser = args_parser()
namespace = parser.parse_args()

# read parameters from command-line arguments
filenames_xyz = namespace.job
NPROC = namespace.nthreads

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


# print program version and exit
def p_version():
	
	return XYZ_coords


PAR_STR = '''%pal nprocs ''' + str(NPROC) + ''' end\n'''
INPUT_DIR = os.getcwd()


# templates from job
def job_CRS(coords, solvent):
	return PAR_STR + '''%cosmors
	solvent "''' + solvent + '''"
end
* xyz ''' + '''0''' + ''' 1 \n''' + coords + '''\n*'''


def job_opt(coords, solvent):
	return PAR_STR + '''! opt B3LYP D4 rijcosx def2-SVPD
! KDIIS DAMP SOSCF LSHIFT

%cpcm
	smd true
	SMDsolvent "''' + solvent + '''"
end
* xyz 0 1 \n''' + coords + '''\n*'''



# regular expression for parsing output files
EXPRESSIONS = {}

EXPRESSIONS["G"] = re.compile(r"Free\ energy\ of\ solvation\ \(dGsolv\)\  :" +r" \s*"  + r"(.*?)" + r"\sEh")
EXPRESSIONS["XYZ"] = re.compile(r"CARTESIAN\ COORDINATES\ \(ANGSTROEM\)\n---------------------------------\n" + r"(.*?)" + "\n\n", re.S)



# start of job and processing of results

DATA_RES = {}
for job in filenames_xyz:
	os.chdir(INPUT_DIR)
	N_atoms, job_name, coords = read_xyz_coord(job)
	if job_name == "":
		job_name = job
	JOB_OPT_1 = job_opt(coords, "water")
	JOB_OPT_2 = job_opt(coords, "octanol")
	os.chdir(WORK_DIR)
	for num, input_data in enumerate([JOB_OPT_1, JOB_OPT_2]):
		input_filename = "active_job.inp"
		output_filename = "active_job.out"
		f = open(input_filename, "w")
		f.write(input_data)
		f.close()
		cmdline = 'nice -n 10 %s "%s" > "%s"' % (ORCA, input_filename, output_filename)
		proc = Popen(cmdline, shell=True, stdout=PIPE, stderr=PIPE, executable = '/bin/bash')
		proc.wait()
		f = open(output_filename, "r")
		DATA_RES[num] = f.read()
		f.close()
		if num == 0:
			coords = EXPRESSIONS["XYZ"].findall(DATA_RES[num])[-1]
			data_opt_H2O = str(N_atoms) + "\n" + job_name + "\n" + coords
			JOB_H2O = job_CRS(coords, "water")
		elif num == 1:
			coords = EXPRESSIONS["XYZ"].findall(DATA_RES[num])[-1]
			data_opt_OCTANOL = str(N_atoms) + "\n" + job_name + "\n" + coords
			JOB_OCTANOL = job_CRS(coords, "1-octanol")
		for f in glob.glob("active_job*"):
			os.remove(f)
	
	for num, input_data in enumerate([JOB_H2O, JOB_OCTANOL], start=2):
		input_filename = "active_job_cosmo-rs.inp"
		output_filename = "active_job_cosmo-rs.out"
		f = open(input_filename, "w")
		f.write(input_data)
		f.close()
		cmdline = 'nice -n 10 %s "%s" > "%s"' % (ORCA, input_filename, output_filename)
		proc = Popen(cmdline, shell=True, stdout=PIPE, stderr=PIPE, executable = '/bin/bash')
		proc.wait()
		f = open(output_filename, "r")
		DATA_RES[num] = f.read()
		f.close()
		for f in glob.glob("active_job_cosmo-rs*"):
			os.remove(f)

	os.chdir(INPUT_DIR)
	try:
	# get free energy
		G_H2O = float(EXPRESSIONS["G"].findall(DATA_RES[2])[0])
		G_OCTANOL = float(EXPRESSIONS["G"].findall(DATA_RES[3])[0])
		f = open("logP_output_data.txt", "a")
		# calculate logP
		LogP = -(G_OCTANOL-G_H2O)*HARTREE*1000/(R_GAZ_CONST*T*math.log(10));
		res = "For job " + job_name + " LogP = " + str(LogP) + "\n"
		f.write(res)
		f.close()
		# return of results
		print("LogP".ljust(20, " "), " =", LogP)
	except:
		f = open("error.log", "w")
		f.write(DATA_RES[0])
		f.write("\n-----------------------------------------------\n")
		f.write(DATA_RES[1])
		f.write("\n-----------------------------------------------\n")
		f.write(DATA_RES[2])
		f.write("\n-----------------------------------------------\n")
		f.write(DATA_RES[3])
		f.write("\n-----------------------------------------------\n")
		f.close()
	# write optimize XYZ coordinates to file
	f = open(job[:-4] + ".H2O.xyz", "w")
	f.write(data_opt_H2O)
	f.close()
	f = open(job[:-4] + ".OCTANOL.xyz", "w")
	f.write(data_opt_OCTANOL)
	f.close()
	
	print("Job execution time  : ", "%.3f" % (time.time() - T_0), " sec.")
	print("Total execution time: ", "%.3f" % (time.time() - T_00), " sec.")
	T_0 = time.time()