""" This script will loop through a folder of TIFF files, open each image, 
and allow the user to click on objects in the image. It will store the coordinates
of these objects. It will then compute the length of the array of coordinates
to give a count of the objects. The user will also input an array of temperatures.
The script will take the counted objects and calculate the percentage of each
object relative to the whole. 

The second part of the script will fit the percentages vs temperature to 
a sigmoid curve. The user can extract the 50% mark and 95% confidence bounds.
The 50% value and the 95% confidence intervals will be stored in a .csv file.
This file will be indexed by the date, which is input by the user. """

import os 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.optimize as optimize
from skimage import io
from pylab import ginput
from collections import defaultdict


## Set global matplotlib parameter
plt.rcParams["font.family"] = "Sans"
plt.rcParams["font.size"] = 32
plt.rcParams["figure.figsize"] = (30,20)
plt.rcParams["image.cmap"] = "bone"

def MrSifter(root_dir):

	"""This function returns the file path of all the tiff files within root_dir."""

	fnames = []
	for root, dirs, files in os.walk(root_dir):

		## Loop through the files
		## Check for .tiff extension
		## save if it has one

		for file in files:
			if file.endswith(".tif"):
				fnames.append(os.path.join(root, file))

		## YOU HAVE BEEN SIFTED

		return fnames

def VesicleCounter(fnames):

	"""This function opens up tif files and allows the user to click and 
	collect coordinates for phase separated and mixed yeast vacuoles. It
	stores the coordinates in a dictionary with key:value = temperature:coordinates."""

	## Set up a dictionary of temperatures with corresponding coordinates
	PS_coords = {} # Phase separated vesicle coordinates
	MIX_coords = {} # Mixed vesicle coordinates
	
	## Loop through the files and open the tifs:
	for name in fnames:

		## Print the file name to obtain the temperature
		print("filename = ", name)

		## Open up the tiff stack and save as an array
		## the array has dimensions (z, x, y) where z
		## represents the number of slices in the stack
		ImageStack = io.imread(name)
		print("ImageStack Dimensions = ", ImageStack.shape)
		Position1 = int(input("Transpose? Then input -1, otherwise 0,: "))
		ImageStack = np.moveaxis(ImageStack, Position1 ,0) # Transpose the stack so that the z axis is the number of tiffs
		ImageStack = ImageStack[1:,:,:] # the first image is black, so skip
		
		## Store the variables
		ps_coords = []
		mix_coords = []

		## Loop through the images in the image stack:
		for image in ImageStack:

			## Display the image and count phase separated
			plt.imshow(image)
			print("Click on phase separated vacuoles")
			ps_coords.append((ginput(show_clicks=True, n=-1, timeout=0)))
			plt.close()
		
			## Display the image and count mixed
			plt.imshow(image)
			print("Click on mixed vacuoles")
			mix_coords.append((ginput(show_clicks=True, n=-1, timeout=0)))
			plt.close()

			## User inputs the temperature
			temp = input("Input the temperature")

		## Populate the dictionary with coordinates and temperature	
		PS_coords[temp] = ps_coords
		MIX_coords[temp] = mix_coords

	return PS_coords, MIX_coords

def ExtractDictValues(PS_coords, MIX_coords):

	"""Loop through the temperatures and replace the coordinates
	with the number of phase separated and the number of mixed 
	vacuoles at each temperature."""

	## Set up a new dictionary of temperatures and counted coordinates
	PS_num = {}
	MIX_num = {}

	## Loop through the temperatures in PS_coords
	for temp in PS_coords:
		# Extract the values for each temperature
		values = PS_coords[temp]

		# Concatenate the sublists within the "values" list
		new_values = [j for i in values for j in i]
		#new_values = sum(values) ## this should be faster

		# Replace the coordinates of the clicks with the number of clicks in
		# the new dictionary
		PS_num[temp] = len(new_values)

	## Loop through the temperatures in MIX_coords
	for temp in MIX_coords:
		# Extract the values for each temperature
		values = MIX_coords[temp]

		# Concatenate the sublists within the "values" list
		new_values = [j for i in values for j in i]

		# Replace the coordinates of the clicks with the number of clicks in
		# the new dictionary
		MIX_num[temp] = len(new_values)

	return PS_num, MIX_num


if __name__ == "__main__":

	## Define the root directory
	root_dir = "C:\\Users\\caitl\\Documents\\YeastProject\\20190418_30c\\Exp3"

	## Get the file names
	fnames = MrSifter(root_dir)

	## Load the images and count the vacuoles
	PS_coords, MIX_coords = VesicleCounter(fnames)


	## Extract the vacuole numbers from coordinates
	PS_num, MIX_num = ExtractDictValues(PS_coords, MIX_coords)

	## Calculate the total number of vacuoles counted
	#VacuoleNum = PS_num + MIX_num
	
	## Combine the two dictionaries under the same key
	CombinedDict = defaultdict(list)
	# Loop through the two dictionaries and combine them under one key
	for dictionary in (PS_num, MIX_num): # these are the input dictionaries
		for key, value in dictionary.items():
			CombinedDict[key].append(value)

	# Create an empty list of phase separation values
	PercentPS = []

	# Loop through the temperatures and calculate the percent PS at each
	for temp in CombinedDict:
		Pair = CombinedDict[temp]
		PS = (Pair[0] / (Pair[0] + Pair[1])) * 100
		PercentPS.append(PS)

	## Extract a list of temperatures as integers in list
	Temperatures = list(map(int, CombinedDict.keys()))

	## Get the name of the first file in the stack
	name = fnames[0]

	## Save the data as a dataframe of Temperatures and Percent PS
	## Save the arrays to the location where
	## fname lives.
	df = pd.DataFrame({"Temperatures":pd.Series(Temperatures,name="Temperatures"),
					   "PercentPS":pd.Series(PercentPS,name="PercentPS")})			   
	df.to_csv(name[:name.rfind(".tif")]+"_results.csv")
















