# Author: Dany Lachance-Quirion
# Created: February 2018; last update: February 16 2018

import os
import numpy as np
os.chdir('C:\Program Files (x86)\Labber\Script')
from Labber import ScriptTools
import csv
import time
import matplotlib
import matplotlib.pyplot as plt

ScriptTools.setExePath('C:\Program Files (x86)\Labber\Program')

## Paths and filenames

# Path of reference measurements files
reference_path = 'C:\\Users\\Demo\\Labber\\Data\\Reference_files'
# Path for data; if folder does not exist, please manually create it before
data_path = 'C:\\Users\\Demo\\Labber\\Data\\2018\\04\\Data_0421'

# Reference filenames
reference_filename = 'CW_SSB_mixer_calibration_readout'
# Data filenames; if a file already exist, data will be appended
calibration_result_filename = 'K2018-04-21_001'

## Parameters

# Local oscillator power (in dBm)
LO_power = 19
# Local oscillator frequency (in Hz)
LO_frequency = 10.4991E9
# AWG frequency (in Hz, max: 400 MHz)
IF_frequency_list = np.linspace(50E6, 70E6, 3)
#IF_frequency_list = 100E6
# Sideband to use; -1: lower sideband (RF=LO-IF), +1: upper sideband (RF=LO+IF)
sideband = -1
# AWG amplitude range for characterizing the calibration (in V)
AWG_amplitude = np.linspace(0, 1.5, 151)
# Bandwidth of the spectrum analyzer (in Hz); it should not be below 1 kHz as the sideband frequency is detuned from LO+/-IF by about 1.5 kHz for an IF frequency of 400 MHz
analyzer_bandwidth = 1E3
# Attenuation between the AWG and the IF inputs of the mixer (in dB); used to calculate the input IF power and the conversion loss
IF_att = 3 + 3
# Impedance (in Ohm); used to calculate the input IF power and the conversion loss
Z = 50
# Attenuation between the RF output of the mixer and the spectrum analyzer (in dB); used to calculate the RF power and conversion loss
RF_att = 0

## Initialize variables
sideband_power_list = np.zeros(len(IF_frequency_list))
isolation_list = np.zeros(len(IF_frequency_list))
sb_suppression_list = np.zeros(len(IF_frequency_list))

## Define measurement objects
Calibration_result = ScriptTools.MeasurementObject(\
                	 os.path.join(reference_path, reference_filename + '.hdf5'),		# reference
                	 os.path.join(data_path, calibration_result_filename + '.hdf5'))		# data

## Calibration

## Loop through all IF frequencies for while the calibration is done
for i, IF_frequency in enumerate(IF_frequency_list):

	sideband_power = np.zeros(len(AWG_amplitude))
	carrier_power = np.zeros(len(AWG_amplitude))
	suppressed_sideband_power = np.zeros(len(AWG_amplitude))

	for j in range(0, 3):
		if j == 0:
			sideband_to_probe = sideband
		elif j == 1:
			sideband_to_probe = 0
		elif j == 2:
			sideband_to_probe = -sideband

		Calibration_result.updateValue('LO1 - Frequency', LO_frequency, 'SINGLE');
		Calibration_result.updateValue('LO1 - Power', LO_power, 'SINGLE');

		Calibration_result.updateValue('Agilent Spectrum Analyzer - Center frequency', LO_frequency + sideband_to_probe * IF_frequency, 'SINGLE');
		Calibration_result.updateValue('Agilent Spectrum Analyzer - IF bandwidth', analyzer_bandwidth, 'SINGLE');

		Calibration_result.updateValue('AWG - Ch1 - Phase', 0.0, 'SINGLE');
		Calibration_result.updateValue('AWG - Ch1 - Frequency', IF_frequency, 'SINGLE');
		Calibration_result.updateValue('AWG - Ch1 - Amplitude', AWG_amplitude[0], 'START');
		Calibration_result.updateValue('AWG - Ch1 - Amplitude', AWG_amplitude[-1], 'STOP');
		Calibration_result.updateValue('AWG - Ch1 - Amplitude', len(AWG_amplitude), 'N_PTS');
		Calibration_result.updateValue('AWG - Ch1 - Offset', 0.0, 'SINGLE');

		(x, data) = Calibration_result.performMeasurement()
		if j == 0:
			sideband_power = data
		elif j == 1:
			carrier_power = data
		elif j == 2:
			suppressed_sideband_power = data

	IF_power = 10 * np.log10((AWG_amplitude[-1]**2 / (2 * Z))) + 30 - IF_att
	RF_power = sideband_power[-1] + RF_att

	sideband_power_list[i] = RF_power
	isolation_list[i] = sideband_power[-1] - carrier_power[-1]
	sb_suppression_list[i] = sideband_power[-1] - suppressed_sideband_power[-1]

	print('----------------------------------------')
	print('IF frequency=', IF_frequency * 1E-6, 'MHz')
	print('Calibration report')
	print('----------------------------------------')
	print('AWG amplitude', AWG_amplitude[-1], 'V')
	print('Sideband power', RF_power, 'dBm')
	print('Conversion loss', IF_power - RF_power, 'dB')
	print('LO to RF isolation', sideband_power[-1] - carrier_power[-1], 'dB')
	print('Sideband suppression', sideband_power[-1] - suppressed_sideband_power[-1], 'dB')
	print('----------------------------------------')

## Save figures in png format for different quantities
fig, axes = plt.subplots(1, 1, figsize=(6, 4))
axes.plot(IF_frequency_list, isolation_list, '-o')
axes.plot(IF_frequency_list, sb_suppression_list, '-o')
axes.set_xlabel('IF frequency (MHz)')
axes.set_ylabel('Isolation and suppresion (dB)')
fig.savefig(data_path + '\\' + calibration_result_filename + '_result.png', bbox_inches='tight')