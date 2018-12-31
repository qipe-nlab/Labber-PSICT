import PSICT_UIF
import numpy as np
import os
import sys

import Labber

## Create pulse definitions (list of dicts)
lMPSpecOriginal = []
lMPSpecOriginal.append({'a': 0.3, 'w': 60e-9, 'v': 100e-9, 'f': 90e6, 'o': 2, 'p': 0})
lMPSpecOriginal.append({'a': 0.5, 'w': 0e-9, 'v': 90e-9, 'f': 60e6, 'o': 4, 'p': 0})
lMPSpecOriginal.append({'a': 0.0, 'w': 0e-9, 'v': 40e-9, 'f': 0e6, 'o': 4, 'p': 0})
## Serialize pulse definitions
lSpecKeyOrder = ['a', 'w', 'v', 'f', 'p', 'o']
def listifyMPSpec(lMPSpecIn, lKeyOrder):
	lSpecOut = []
	for oMPSpec in lMPSpecIn:
		lSpecInner = []
		for sSpecKey in lKeyOrder:
			lSpecInner.append(oMPSpec[sSpecKey])
		lSpecOut.append(lSpecInner)
	return lSpecOut
lMPSpecList = listifyMPSpec(lMPSpecOriginal, lSpecKeyOrder)

## Write to file
pulse_def_path = os.path.abspath('definitions_001.txt')
## Check directory existence
if not os.path.exists(os.path.dirname(pulse_def_path)):
	os.makedirs(os.path.dirname(pulse_def_path))
## Write to file
with open(pulse_def_path, 'w') as pd_file:
	pd_file.write(','.join(lSpecKeyOrder)+'\n')
	for pulse_def in lMPSpecList:
		pd_file.write(','.join(str(quant) for quant in pulse_def)+'\n')
## Status message
print('Pulse definitions written to file: {}'.format(pulse_def_path))

## Generate permutations for GST, write to file, and the pass file path to MultiPulse

## Generate list of lists of pulse sequences
all_pulse_seqs = []
# all_pulse_seqs.append([0])
# all_pulse_seqs.append([1])
# all_pulse_seqs.append([2])
# all_pulse_seqs.append([0,0])
# all_pulse_seqs.append([0,1])
# all_pulse_seqs.append([0,2])
# all_pulse_seqs.append([1,0])
# all_pulse_seqs.append([1,0,2,1,2,0])
# all_pulse_seqs.append([0,0,0,1,1,1,2,2,2])
all_pulse_seqs.append([1,0,2,0,1,2,0])

## Write to file
pulse_seq_path = os.path.abspath('sequence_001.txt')
## Check directory existence
if not os.path.exists(os.path.dirname(pulse_seq_path)):
	os.makedirs(os.path.dirname(pulse_seq_path))
## Write to file
with open(pulse_seq_path, 'w') as ps_file:
	for pulse_seq in all_pulse_seqs:
		ps_file.write(','.join(str(pulse) for pulse in pulse_seq)+'\n')
## Status message
print('Pulse sequences written to file: {}'.format(pulse_seq_path))

##############################################################################
## Do not change the script structure beyond this point!

pulse_sequence = 'MultiPulse-Test01'

slave_PSICT_options = {
	'running_as_slave': True,
	'config_path': '../PSICT_config.py',
	## Set template file directory and name
	'template_dir': 'C:/Users/Pierre/Google Drive/Quantum magnonics/Data/Reference_files/',
	'template_file': 'MultiPulse_test02',
	## Set output file directory and name (where result will be saved)
	'output_dir': 'C:/Users/Pierre/Google Drive/Quantum magnonics/Data/2018/12/Data_1228',
	'output_file': 'MultiPulse_test_0001',
	## Script copy options
	'script_copy_target_dir': 'C:/Users/Pierre/Google Drive/Quantum magnonics/Data/Measurement_scripts/MultiPulse/',
}

slave_general_options = {
	'sideband': -1,
	# IF frequency in Hz of the readout square pulse
	'readout_IF_frequency': 90e6,
	# Power in dBm of the local oscillator used for readout (LO1)
	'readout_LO_power': 19,
	# Optimal target frequency in Hz of the readout square pulse
	'readout_frequency_opt': 8.412050e9,
	# Optimal amplitude in V of the readout square pulse
	'readout_amplitude_opt': 0.23,
	# ''Optimal'' duration in seconds of the readout square pulse
	'readout_plateau_opt': 400e-9,

	# IF frequency in Hz of the qubit control pulse
	'qubit_IF_frequency': 95e6,
	# Power in dBm of the local oscillator used for qubit control (LO2)
	'qubit_LO_power': 16,
	# Target control frequency in Hz of the qubit control gaussian pulse
	'qubit_frequency_opt': 7.924759e9,

	# IF frequency in Hz of the magnon control pulse
	'magnon_IF_frequency': 115e6,
	# Power in dBm of the local oscillator used for qubit control (LO3)
	'magnon_LO_power': 16,
	# Target control frequency in Hz of the qubit control gaussian pulse
	'magnon_frequency_opt': 7.787615e9,

	## Parameters for pi pulses
	'qubit_width_pi': 12e-9,
	## Gaussian pulses
	'qubit_amplitude_pi_dict': {12e-9: 1.109358, 200e-9: 0.073707, },
	#1.068168, },
	## Lambda values for different pi-pulse durations
	'lambda_dict': {},

	## Square pulses
	'qubit_plateau_pi': 0e-9,

	## General settings for pulse sequences
	# Truncation range for gaussian pulses according to the definition of the 'Single-qubit pulse generator'
	'SQPG_truncation_range': 3,
	# Sampling rate in samples/second for the pulse sequence/AWG
	'SQPG_sampling_rate': 1e09,
	# Duration in seconds of the pulse sequence
	'SQPG_sequence_duration': 4000e-9,

	## General settings for the digitizer
	# Number of repetitions (shots) averaged at the digitizer, 1: single-shot
	'N_shots': 1e04,
	# Length in seconds of the measured time trace
	'digitizer_length': 600e-9,
	# Sampling rate in samples/second of the digitizer
	'digitizer_sampling_rate': 5e08,

	## General setting for the demodulation
	# Time in seconds to start the demodulation, takes into account the delay before the readout pulse arrive
	'demodulation_skip_start': 200e-9,
	# Length in seconds of the demodulation, should be close to readout_plateau, and at maximum digitizer_length
	'demodulation_length': 400e-9,

	# Current in amperes for the coil
	'current': -7.97e-3,
}

slave_pulse_sequence_options = {

	'MultiPulse-Test01': {
		##
	},

}

## SCRIPT COPY BREAKPOINT

def run_pulse_sequence(pulse_sequence_name, PSICT_options, general_options, pulse_sequence_options_all, *, verbose = 0):
	'''
	Run the pulse sequence specified by pulse_sequence_name.

	Options passed in via parameter dicts.
	'''

	pulse_sequence = pulse_sequence_name
	pulse_sequence_options = pulse_sequence_options_all[pulse_sequence]

	#############################################################################
	## PSICT and directory setup

	print('-------------------------------------------')
	print('==>', pulse_sequence)
	print('PSICT_UIF version is', PSICT_UIF.__version__)

	## Initialise PSICT-UIF interface object
	psictInterface = PSICT_UIF.psictUIFInterface(verbose = 0)
	psictInterface.is_slave = PSICT_options['running_as_slave']

	## Set file paths
	config_path = PSICT_options['config_path']
	template_dir = PSICT_options['template_dir']
	template_file = PSICT_options['template_file']
	output_dir = PSICT_options['output_dir']
	output_file = PSICT_options['output_file']
	script_copy_target_dir = PSICT_options['script_copy_target_dir']
	psictInterface.load_config_file(config_path, verbose = 0)
	psictInterface.set_template_file(template_dir, template_file, verbose = 0)
	psictInterface.set_output_file(output_dir, output_file, verbose = 1)
	psictInterface.set_script_copy_target_dir(script_copy_target_dir, verbose = 0)

	#############################################################################
	## General options

	## Converting dictionary-defined parameters to variables
	## This has the beneficial side effect of ensuring each of these parameters
	##      exists in the options dict passed to the function

	sideband = general_options['sideband']
	readout_IF_frequency = general_options['readout_IF_frequency']
	readout_LO_power = general_options['readout_LO_power']
	readout_frequency_opt = general_options['readout_frequency_opt']
	readout_amplitude_opt = general_options['readout_amplitude_opt']
	readout_plateau_opt = general_options['readout_plateau_opt']
	qubit_IF_frequency = general_options['qubit_IF_frequency']
	qubit_LO_power = general_options['qubit_LO_power']
	qubit_frequency_opt = general_options['qubit_frequency_opt']
	magnon_IF_frequency = general_options['magnon_IF_frequency']
	magnon_LO_power = general_options['magnon_LO_power']
	magnon_frequency_opt = general_options['magnon_frequency_opt']
	qubit_width_pi = general_options['qubit_width_pi']
	qubit_amplitude_pi_dict = general_options['qubit_amplitude_pi_dict']
	qubit_amplitude_pi = qubit_amplitude_pi_dict[qubit_width_pi]
	lambda_dict = general_options['lambda_dict']
	qubit_plateau_pi = general_options['qubit_plateau_pi']
	SQPG_truncation_range = general_options['SQPG_truncation_range']
	SQPG_sampling_rate = general_options['SQPG_sampling_rate']
	SQPG_sequence_duration = general_options['SQPG_sequence_duration']
	N_shots = general_options['N_shots']
	digitizer_length = general_options['digitizer_length']
	digitizer_sampling_rate = general_options['digitizer_sampling_rate']
	demodulation_skip_start = general_options['demodulation_skip_start']
	demodulation_length = general_options['demodulation_length']
	current = general_options['current']


	#############################################################################
	## Pulse sequences

	if pulse_sequence == 'MultiPulse-Test01':

		# Target frequency in Hz of the readout square pulse
		readout_frequency = readout_frequency_opt
		# Amplitude in V of the readout square pulse
		readout_amplitude = readout_amplitude_opt
		# Duration in seconds of the readout square pulse
		readout_plateau = readout_plateau_opt

		# Target control frequency in Hz of the qubit control gaussian pulse
		qubit_frequency = qubit_frequency_opt
		# Amplitude in V of the qubit control gaussian pulse
		qubit_amplitude = qubit_amplitude_pi
		# Width in seconds of the qubit control gaussian pulse
		qubit_width = qubit_width_pi

		# Target control frequency in Hz of the magnon control gaussian pulse
		magnon_frequency = magnon_frequency_opt

		point_values = {
		'MultiPulse': {
				'TestField02': 9,
				'Number of points': 3E3,
			}, # end MultiPulse
		# 'SQPG': {
		# 	## Parameters for overall pulse sequence - general SGPQ parameters
		# 	'main': {'Truncation range': SQPG_truncation_range, 'Sample rate': SQPG_sampling_rate, 'sequence_duration': SQPG_sequence_duration},
		# 	'qubit1': {
		# 		'time_reference': 'absolute',
		# 		'time_offset': 0.0, 'pulse_number': 1,
		# 		'a': qubit_amplitude, 'w': qubit_width, 'v': 0.0, 'f': qubit_IF_frequency,
		# 		'o': 2
		# 		},
		# 	'qubit2': {'relative_to': 'qubit1',
		# 		'time_offset': 0.0, 'time_reference': 'relative', 'relative_marker': 'end',
		# 		'a': qubit_amplitude, 'w': qubit_width, 'v': 0.0, 'f': qubit_IF_frequency,
		# 		'o': 2
		# 		},
		# 	'trigger': {'relative_to': 'qubit2',
		# 		'time_offset': 0.0, 'time_reference': 'relative', 'relative_marker': 'end',
		# 		'a': 1.5, 'w': 0.0, 'v': 20E-9, 'f': 0.0,
		# 		'o': 4
		# 		},
		# 	'readout': {'relative_to': 'trigger',
		# 		'time_offset': 0.0, 'time_reference': 'relative', 'relative_marker': 'end',
		# 		'a': readout_amplitude, 'w': 0.0, 'v': readout_plateau, 'f': readout_IF_frequency,
		# 		'o': 1
		# 		}
			# }, # end SQPG
		'Manual': {
				'Value 1': 100,
			}
		} # end point values

		Labber_api_client_values = {
			'MultiPulse': {
			}, # end MultiPulse
		} # end api client values
		instr_config_values = {
			'MultiPulse': {
				'Pulse definitions file': pulse_def_path,
				'Pulse sequences file': pulse_seq_path,
			}, # end MultiPulse
		} # end instr_config_values
		Labber_api_hardware_names = {'MultiPulse': 'PSICT MultiPulse'}

		iteration_values = {
			}

		iteration_order = [
			] # end iteration order
		# end reference

		## Channel relations - set available quantities (could be outsourced to rcfile?)
		channel_defs = {
			} # end relation channels

		channel_relations = {

			} # end channel relations
		## end Qubit_Ramsey

	#############################################################################
	## Set parameters & measure
	#############################################################################

	## Set input parameter values
	psictInterface.set_point_values(point_values, verbose = 0)
	psictInterface.set_api_client_values(Labber_api_client_values, \
				hardware_names = Labber_api_hardware_names, server_name = 'localhost', verbose = 0)
	psictInterface.set_instr_config_values(instr_config_values, \
				hardware_names = Labber_api_hardware_names, server_name = 'localhost', \
				verbose = 0)
	psictInterface.set_iteration_values(iteration_values, iteration_order, verbose = 1)
	psictInterface.set_channel_relations(channel_defs, channel_relations, verbose = 0)

	## Run measurement
	psictInterface.perform_measurement(dry_run = False, verbose = 1)

	return psictInterface.fileManager.output_path

	##

if __name__ == '__main__':
	## This block will only be executed if the slave is run explicitly as a standalone script

	# print('Running as a standalone script...')

	slave_PSICT_options['running_as_slave'] = False

	run_pulse_sequence(pulse_sequence, slave_PSICT_options, slave_general_options, slave_pulse_sequence_options, verbose = 1)

else:
	## This block will only be run when the slave is imported (ie 'run' through a master script)

	# print('Running as slave script...')
	slave_PSICT_options['running_as_slave'] = True

##
