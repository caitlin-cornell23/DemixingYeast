''' This script takes temperature vs phase separation data from multiple experiments and
plots them on top of eachother. The user loads in .csv files from one folder and each file
is assigned to its own experiment. '''

import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy.optimize as optimize

## Set global matplotlib parameters
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.size"] = 14
plt.rcParams["savefig.dpi"] = 600
plt.rcParams["axes.linewidth"] = 2.0
plt.rcParams["xtick.major.width"] = 1.5
plt.rcParams["ytick.major.width"] = 1.5

def Sigmoid(x, c, d, a):

	"""This function computes a sigmoid from percentage data and
	temperature data"""

	## a = asymptote 
	## c = Tmix value (inflection point of the curve)
	## d = rate of the sigmoid decay

	return a * (1 - 1 / (1 + np.exp(-(x - c) / d)))

def ConfidenceIntervals(temperature, percentPS, Fit, popt):
	'''Sample the fit and determine confidence intervals.'''

	## Get the coordinates for the fit curve
	coor_y = [np.min(Fit),np.max(Fit)]
	coor_x = [np.min(temperature), np.max(temperature)]

	## Predict the y-values of the original data from the fit parameters
	## popt[0] = c (tmix) and popt[1] = d
	pred_y = Sigmoid(temperature, *popt)

	## Calculate the y-error (residuals)
	y_err = percentPS - pred_y

	## Create a series of text x-values to sample
	pred_x = np.arange(np.min(temperature), np.max(temperature)+1,1)

	## Set up the variables to calculate confidence intervals
	mean_x = np.mean(temperature) # mean of temperatures
	n = len(temperature) # length of temperature array (number of samples)
	t = 2.093 # this value changes based on the confindence interval and the sample size (look up)
	std_err = np.sum(np.power(y_err,2)) # sum of the squares of the residuals

	## Calculate the confidence intervals from the new test values
	conf_int = t * np.sqrt((std_err/n-2))*(1.0/n + (np.power((pred_x - mean_x),2)/
					((np.sum(np.power(temperature,2)))-n*(np.power(mean_x,2)))))

	## Predict y-values based on test x-values
	pred_y = Sigmoid(pred_x, *popt)

	## Get upper and lower confidence limits based on the confidence intervals
	## and predicted y-values

	upper = pred_y + abs(conf_int)
	lower = pred_y - abs(conf_int)

	return upper, lower

def MrSifter(root_dir):

	"""This function returns the file path of all the tif files within root_dir."""

	fnames = []
	for root, dirs, files in os.walk(root_dir):

		## Loop through the files
		## Check for .tiff extension
		## save if it has one

		for file in files:
			if file.endswith(".csv"):
				fnames.append(os.path.join(root, file))

		## YOU HAVE BEEN SIFTED

	return fnames

if __name__ == "__main__":

	## Define the root directory
	root_dir = "C:\\Users\\caitl\\Documents\\YeastProject\\20190418_30c\\"

	## Get the filenames
	fnames = MrSifter(root_dir)

	## Loop through the filenames and sort them based on the number that appears
	## after "date_Exp#results_#.csv"

	# Create empty arrays for however many experiments you plan to load
	Exp1 = []
	Exp2 = []
	#Exp3 = []

	for name in fnames:
		## Parse the file name to get the parent folder
		sample = name[name.rfind("results")+7:name.rfind(".csv")+4]

		if sample == "_1.csv":
			Exp1 = pd.read_csv(name, header=0, index_col=0)

		if sample == "_2.csv":
			Exp2 = pd.read_csv(name, header=0, index_col=0)

		#if sample == "_3.csv":
			#Exp3.append(pd.read_csv(name, header=0, index_col=0))


	## Sort the data by temperature in each dataframe
	Exp1 = Exp1.sort_values("Temperatures")
	Exp2 = Exp2.sort_values("Temperatures")
	#Exp3 = Exp3.sort_values("Temperatures")

	## Extract the values for temperature and percentPS for each experiment
	Exp1_temp = Exp1["Temperatures"].tolist()
	Exp1_ps = Exp1["PercentPS"].tolist()
	Exp2_temp = Exp2["Temperatures"].tolist()
	Exp2_ps = Exp2["PercentPS"].tolist()
	#Exp3_temp = Exp3["Temperatures"].tolist()
	#Exp3_ps = Exp3["PercentPS"].tolist()
	

	## fit a sigmoid to the data in each experiment
	## Compute the optimization parameters and the covariance matrix
		#popt = optimizaiton parameters
		#pcov = covariance matrix (we will calculate confidence from this)
	popt1, pcov1 = optimize.curve_fit(Sigmoid, Exp1_temp, Exp1_ps, p0=(46,20,60)) # estimate parameters
	Fit1 = Sigmoid(Exp1_temp, *popt1)
	popt2, pcov2 = optimize.curve_fit(Sigmoid, Exp2_temp, Exp2_ps, p0=(46,20,60)) # estimate parameters
	Fit2 = Sigmoid(Exp2_temp, *popt2)
	#popt3, pcov3 = optimize.curve_fit(Sigmoid, Exp3_temp, Exp3_ps, p0=(46,20,60)) # estimate parameters
	#Fit3 = Sigmoid(Exp3_temp, *popt3)

	## Calculate confidence intervals for each curve

	upper1, lower1 = ConfidenceIntervals(Exp1_temp, Exp1_ps, Fit1, popt1)
	upper2, lower2 = ConfidenceIntervals(Exp2_temp, Exp2_ps, Fit2, popt2)
	#upper3, lower3 = ConfidenceIntervals(Exp3_temp, Exp3_ps, Fit3, popt3)

	###### Plot the data ######

	## Set up the plot
	fig, axes = plt.subplots(1,1, figsize=(10,8))

	axes.grid(color="grey", alpha=0.3, linestyle="-")
	axes.plot(Exp1_temp, Fit1, linestyle="-", color="#324851", linewidth=3)
	axes.plot(Exp1_temp, Exp1_ps, marker="o", linestyle="None", markersize=10, color="#324851")
	#axes.plot(Exp1_temp, upper1, linestyle="-", linewidth=2, color="#34675C", alpha=0.7)
	#axes.plot(Exp1_temp, lower1, linestyle="-", linewidth=2, color="#34675C", alpha=0.7)
	#axes.fill_between(Exp1_temp, upper1, lower1, color="#7DA3A1", alpha=0.5)

	axes.plot(Exp2_temp, Fit2, linestyle="-", color="#324851", linewidth=3)
	axes.plot(Exp2_temp, Exp2_ps, marker="o", linestyle="None", markersize=10, color="#324851")
	#axes.plot(Exp2_temp, upper2, linestyle="-", linewidth=2, color="#34675C", alpha=0.7)
	#axes.plot(Exp2_temp, lower2, linestyle="-", linewidth=2, color="#34675C", alpha=0.7)
	#axes.fill_between(Exp2_temp, upper2, lower2, color="#7DA3A1", alpha=0.5)

	#axes.plot(Exp3_temp, Fit, linestyle="-", color="#324851", linewidth=5)
	#axes.plot(Exp3_temp, Exp3_ps, marker="o", linestyle="None", markersize=20, color="#324851")
	#axes.plot(Exp3_temp, upper3, linestyle="-", linewidth=2, color="#34675C", alpha=0.7)
	#axes.plot(Exp3_temp, lower3, linestyle="-", linewidth=2, color="#34675C", alpha=0.7)
	#axes.fill_between(Exp3_temp, upper3, lower3, color="#7DA3A1", alpha=0.5)

	axes.set_ylabel("Percent of Vacuoles with Domains")
	axes.set_xlabel("Temperature")

	plt.tight_layout()
	#plt.savefig("Combined25degree.pdf")
	plt.show()










		

	


