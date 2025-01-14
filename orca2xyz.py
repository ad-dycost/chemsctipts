#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  orca2xyz.py
#  
#  Copyright 2019 Ad <ad.dycost@gmail.com>
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

import sys, os, re, argparse

VERSION = 0.3
HISTORY = '''
			0.3 -- added parsing of scan jobs by coordinate
'''


# function for parsing command line parameters
def args_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument ("-t", "--type", choices = ["opt", "scan"], default = "opt", help = 'choice type of job, optimization geometry or relaxation scan')
	parser.add_argument ("-f", "--files", nargs='+', help = 'processed files (output files for jobs)')

	return parser

# function for create one frame to XYZ file 
def create_frame(coords, energy):
	frame = " " + str(len(coords)) + "\n" + " Energy = " + energy + "\n" + "\n".join(coords)
	return frame


parser = args_parser()
namespace = parser.parse_args()
names = map(lambda x: x[:-4] , namespace.files)


TAG_1 = r"CARTESIAN\ COORDINATES\ \(ANGSTROEM\)\n---------------------------------\n"
TAG_2 = r"FINAL\ SINGLE\ POINT\ ENERGY"
TAG_3 = r"\ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \*\*\*\ FINAL\ ENERGY\ EVALUATION\ AT\ THE\ STATIONARY\ POINT\ \*\*\*"
TAG_4 = r"\*\*\*\ OPTIMIZATION\ RUN\ DONE\ \*\*\*"
TAG_5 = r"GEOMETRY\ OPTIMIZATION\ CYCLE"

# one step optimization
expression_1 = re.compile(TAG_1 + r"(.*?)" + "\n\n", re.S)
expression_2 = re.compile(TAG_2 + r"(.*?)" + "\n")
# one step scanning
expression_3 = re.compile(TAG_3 + r"(.*?)" + TAG_4, re.S)


for name in names:
	
	try:
		f = open(name + ".out", "r")
	except:
		print("Orca outpute file not found")
		sys.exit(1)

	data_all = f.read()
	data_out = []


	if namespace.type == "opt":
		data_coord = expression_1.findall(data_all)
		data_energy = expression_2.findall(data_all)
	elif namespace.type == "scan":
		data_scan_step = expression_3.findall(data_all)
		data_coord = map(lambda x: expression_1.search(x).group(1), data_scan_step)
		data_energy = map(lambda x: expression_2.search(x).group(1), data_scan_step)

	for data in zip(data_coord, data_energy):
		energy = data[1].strip(" ")
		coords = data[0].split("\n")
		frame = create_frame(coords, energy)
		data_out.append(frame + "\n")
	
	o = open(name + ".xyz", "w")
	o.write("".join(data_out))
	o.close()
