#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  startorca.py
#  
#  Copyright 2019 ad <ad.dycost@gmail.com>
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

HISTORY = '''
			0.3 -- added saving XYZ trajectory file
			0.32 -- added thread number check
			0.33 -- temporary files have been moved to a separate directory
			0.34 -- added base processing of %Compound directive
			0.35 -- added expanded processing of %Compound directive
			0.36 -- adapted for ORCA 5.0
			0.37 -- switch to python 3, added processing of %base directive
'''


import os, sys, shutil, datetime, re, string
from subprocess import Popen, PIPE
from glob import glob

VERSION = 0.37
HOME_DIR = os.environ['HOME']  + "/programs_data/orca/"
WORK_DIR = "/mnt/scratch/orca/"
ORCA_DIR = "/opt/orca/"
ORCA = ORCA_DIR + "orca"
NPROC = sys.argv[1]

try:
	int(NPROC)
except:
	print("Number of thread value error")
	sys.exit(1)

PAR_STR = "%pal nprocs " + NPROC + " end"

# Regular expression for parsing Compound files
EXPRESSIONS = {}
EXPRESSIONS["job_names"] = re.compile(r"#Alias_Step" + r"(.*?)" + "\n")
EXPRESSIONS["base_name"] = re.compile(r"%base" + r"(.*?)" + "\n")

INPUT_FILES =  sys.argv[2:]
os.chdir(HOME_DIR)

for f in INPUT_FILES:
	af = open(f, "r")
	DATA = af.read()
	if "%pal nprocs" in DATA:
		expression_pal = re.compile(r"\%pal\ nprocs\ \d+\ end", re.S)
		pal_old = expression_pal.findall(DATA)[0]
		DATA = DATA.replace(pal_old, PAR_STR)
	else:
		DATA = PAR_STR + "\n" + DATA 
	af = open(f, "w")
	af.write(DATA)
	af.close()

for f in INPUT_FILES:
	name = f[:-4]
	input_filename = "active_" + datetime.datetime.today().strftime("%Y-%m-%d_%H_%M_%S") + ".inp"
	output_filename = name + ".out"
	
	
	# processind compound jobs
	active_file = open(f, "r")
	job_data = active_file.read()
	if "%Compound" in job_data:
		job_names = map(lambda s: s.strip(), EXPRESSIONS["job_names"].findall(job_data))
	
		
	# change base name of job
	if "%base" in job_data:
		input_filename = EXPRESSIONS["base_name"].findall(job_data)[0].strip('" ') + ".inp"

	shutil.copy(f, WORK_DIR + input_filename)
	os.chdir(WORK_DIR)
	cmdline = 'nice -n 10 %s "%s" > "%s"' % (ORCA, input_filename, HOME_DIR + output_filename)
	proc = Popen(cmdline, shell=True, stdout=PIPE, stderr=PIPE, executable = '/bin/bash')
	proc.wait()
	
	# moving files
	if "%Compound" in job_data:
		for i, job_name in enumerate(job_names):
			try:
				tmp_list_files = filter(lambda x: "tmp" not in x, glob(input_filename[:-4] + "_Compound_" + str(i+1) + "*"))
				for f in tmp_list_files:
					shutil.move(f, f.replace("_Compound_" + str(i+1), job_name))
			except:
				pass
	
	os.remove(input_filename)
	list_files = filter(lambda x: "tmp" not in x, glob(input_filename[:-4] + "*"))
	for f in list_files:
		shutil.move(f, HOME_DIR + f.replace(input_filename[:-4], name))


	active_file.close()
	os.chdir(HOME_DIR)
