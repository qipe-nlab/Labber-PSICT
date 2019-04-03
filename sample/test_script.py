import os
import sys
import shutil
import numpy as np

import PSICT_UIF
from PSICT_extras.PSICT_MultiPulse.PSICT_MultiPulse_tools import writePulseDefs, writePulseSeqs, countNSequences

## Do not change script structure beyond this point!
##############################################################################

pulse_sequence = 'Qubit_Ramsey'

worker_PSICT_options = {
	## Master/worker settings - do not change directly
	'running_as_worker': True,
	'parent_logger_name': 'WSMgr',
	## Global PSICT settings
	'config_path': 'PSICT_config.py',
	## Set template file directory and name
	'template_dir': '../../test_template_files',
	'template_file': 'K2019-03-25_reference_averaged',
	## Set output file directory and name (where result will be saved)
	'output_dir': '../../test_output_files/results',
	'output_file': 'labber_test_0019',
	## Script copy options
	'script_copy_target_dir': '../../test_output_files/scripts',
}

worker_general_options = {
	'sideband': -1,
	# IF frequency in Hz of the readout square pulse
	'readout_IF_frequency': 60e6,
	# Power in dBm of the local oscillator used for readout (LO1)
	'readout_LO_power': 19,
	# Optimal target frequency in Hz of the readout square pulse
	'readout_frequency_opt': 10.712650e9,
	# Optimal amplitude in V of the readout square pulse
	'readout_amplitude_opt': 1.0000,
	# ''Optimal'' duration in seconds of the readout square pulse
	'readout_plateau_opt': 400e-9,

	# IF frequency in Hz of the qubit control pulse
	'qubit_IF_frequency': 95e6,
	# Power in dBm of the local oscillator used for qubit control (LO2)
	'qubit_LO_power': 16,
	# Target control frequency in Hz of the qubit control gaussian pulse
	'qubit_frequency_opt': 7.826855e9,

	## Parameters for pi pulses
	'qubit_width_pi': 8e-9,
	## Gaussian pulses
	'qubit_amplitude_pi_dict': {5e-9: 1.500000, 6e-9: 1.225781, 8e-9: 0.918900, 12e-9: 0.611659, 15e-9: -0.491846, 7e-9: 1.046382, 9e-9: 0.812801, 10e-9: 0.735974, 11e-9: 0.666401, 13e-9: 0.569072, 14e-9: 0.527675, 16e-9: 0.461379, 17e-9: 0.430891, 18e-9: 0.403928, 19e-9: 0.389747, 20e-9: 0.365237, },
	## DRAG coefficient
	'DRAG_coefficient': {8e-09: -1.425e-10, 1.2e-08: -2.5e-11},

	# Values related to the pump will be updated if True
	'use_pump': False,
	# IF frequency in Hz of the pump control pulse
	'pump_IF_frequency': 110e6,
	# Power in dBm of the local oscillator used for the pump (LO3)
	'pump_LO_power': 16,
	# Target control frequency in Hz of the pump control pulse
	'pump_frequency_opt': 8.000000e9,

	## General settings for pulse sequences
	# Truncation range for gaussian pulses according to the definition of the 'Single-qubit pulse generator'
	'SQPG_truncation_range': 3,
	# Sampling rate in samples/second for the pulse sequence/AWG
	'SQPG_sampling_rate': 1e09,
	# Duration in seconds of the pulse sequence
	'SQPG_sequence_duration': 50000e-9,

	# Truncation range for gaussian pulses according to the definition of the 'Single-qubit pulse generator'
	'MultiPulse_truncation_range': 3,
	# Sampling rate in samples/second for the pulse sequence/AWG
	'MultiPulse_sampling_rate': 1e09,
	# Duration in seconds of the pulse sequence
	'MultiPulse_sequence_duration': 100000e-9,

	## General settings for the digitizer
	# Number of repetitions (shots) averaged at the digitizer, 1: single-shot
	'N_shots': 1e04,
	# Length in seconds of the measured time trace
	'digitizer_length': 700e-9,
	# Sampling rate in samples/second of the digitizer
	'digitizer_sampling_rate': 5e08,

	## General setting for the demodulation
	'measure_Q': False,
	# Time in seconds to start the demodulation, takes into account the delay before the readout pulse arrive
	'demodulation_skip_start': 330e-9,
	# Length in seconds of the demodulation, should be close to readout_plateau, and at maximum digitizer_length
	'demodulation_length': 300e-9,

	# Value of the current will be updated if True
	'use_current_source': False,
	# Current in amperes for the coil, if 'use_current_source', the value is meaningless
	'current': 0.000e-3,
}

worker_pulse_sequence_options = {

	'Qubit_Rabi_amplitude':
		{
			'reference': True,
			'fast_reference': True,

			## Amplitude in V of the qubit control gaussian pulse
			'qubit_amplitude_list': [0.000, 0.367, 101],
			## Width in s of the qubit control gaussian pulse
			'qubit_width': 20e-9,
			## Overall repetitions
			'N_repetitions': 5e00,
		},##

	'Qubit_T1':
		{
			'reference': True,
			'fast_reference': True,
			## Free evolution time in seconds
			'tau_list': [0e-9, 10000e-9, 101],
			## Overall repetitions
			'N_repetitions': 1e00,
		},##

	'Qubit_Ramsey':
		{
			'reference': True,
			'fast_reference': True,
			## Intentional detuning from the current qubit frequency estimate
			'intentional_detuning': -4.000e6,
			## Free evolution time in seconds
			'tau_list': [0e-9, 4000e-9, 201],
			## Initial delay
			'delay': 0.0,
			## Use DRAG parameter for qubit pulse
			'use_DRAG': True,
			## Overall repetitions
			'N_repetitions': 1e00,
		},##

	'Qubit_echo':
		{
			'reference': True,
			'fast_reference': True,
			## Free evolution time in seconds
			'tau_list': [0e-9, 1000e-9, 101],
			## Overall repetitions
			'N_repetitions': 1e00,
		},##

	'Qubit_single_shot': ## single_shot
		{
			'N_single_shots': 1e03,
			'N_repetitions': 1e02,
		},##

	'DRAG_optimization': {
		## MultiPulse driver options
		'First pulse delay': 1e-07,
		'Generate from final pulse': 1,
		'Final pulse time': 5e-05,
		'Use global DRAG': 1,
		'iterate_DRAG': True,
		'DRAG_list': [-1e-09, 1e-09, 51],
		##
		'pulse_def_file': '../../test_output_files/definitions.txt',
		'pulse_seq_file': '../../test_output_files/sequences.txt',

		## Number of gates (sequence length)
		'number_of_gates': [0, 100, 101],
		## Add extra X90 to end to invert final state
		# 'end_on_X90': False, # DON'T DO THIS JUST YET PLEASE

		'N_repetitions': 1e00,
		},##

}

## SCRIPT COPY BREAKPOINT

def run_pulse_sequence(pulse_sequence_name, PSICT_options, general_options, pulse_sequence_options_all):
	'''
	Run the pulse sequence specified by pulse_sequence_name.

	Options passed in via parameter dicts.
	'''

	pulse_sequence = pulse_sequence_name
	pulse_sequence_options = pulse_sequence_options_all[pulse_sequence]

	#############################################################################
	## PSICT and directory setup

	## Initialise PSICT-UIF interface object
	psictInterface = PSICT_UIF.psictUIFInterface(PSICT_options['config_path'], parent_logger_name = PSICT_options['parent_logger_name'])
	psictInterface.set_worker_status(PSICT_options['running_as_worker'])

	psictInterface.log('-------------------------------------------')
	psictInterface.log('==> {}'.format(pulse_sequence))
	psictInterface.log('PSICT_UIF version is {}'.format(PSICT_UIF.__version__))

	## Set file paths
	config_path = PSICT_options['config_path']
	template_dir = PSICT_options['template_dir']
	template_file = PSICT_options['template_file']
	output_dir = PSICT_options['output_dir']
	output_file = PSICT_options['output_file']
	script_copy_target_dir = PSICT_options['script_copy_target_dir']
	psictInterface.set_template_file(template_dir, template_file)
	psictInterface.set_output_file(output_dir, output_file)
	psictInterface.set_script_copy_target_dir(script_copy_target_dir)

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

	qubit_width_pi = general_options['qubit_width_pi']
	qubit_amplitude_pi_dict = general_options['qubit_amplitude_pi_dict']
	qubit_amplitude_pi = qubit_amplitude_pi_dict[qubit_width_pi]

	use_pump = general_options['use_pump']
	if use_pump:
		pump_IF_frequency = general_options['pump_IF_frequency']
		pump_LO_power = general_options['pump_LO_power']
		pump_frequency_opt = general_options['pump_frequency_opt']

	SQPG_truncation_range = general_options['SQPG_truncation_range']
	SQPG_sampling_rate = general_options['SQPG_sampling_rate']
	SQPG_sequence_duration = general_options['SQPG_sequence_duration']

	N_shots = general_options['N_shots']
	digitizer_length = general_options['digitizer_length']
	digitizer_sampling_rate = general_options['digitizer_sampling_rate']

	measure_Q = general_options['measure_Q']
	demodulation_skip_start = general_options['demodulation_skip_start']
	demodulation_length = general_options['demodulation_length']

	use_current_source = general_options['use_current_source']
	if use_current_source:
		current = general_options['current']

	#############################################################################
	## Pulse sequences

	if pulse_sequence == 'Qubit_Rabi_amplitude':#TESTED 2019.03.27

		reference = pulse_sequence_options['reference']
		fast_reference = pulse_sequence_options['fast_reference']

		reference_switch_list = [1, 0, 2]

		# Target frequency in Hz of the readout square pulse
		readout_frequency = readout_frequency_opt
		# Amplitude in V of the readout square pulse
		readout_amplitude = readout_amplitude_opt
		# Duration in seconds of the readout square pulse
		readout_plateau = readout_plateau_opt

		# Target control frequency in Hz of the qubit control gaussian pulse
		qubit_frequency = qubit_frequency_opt
		# Amplitude in V of the qubit control gaussian pulse
		qubit_amplitude_list = pulse_sequence_options['qubit_amplitude_list']
		qubit_amplitude = qubit_amplitude_list[0]
		# Width in seconds of the qubit control gaussian pulse
		qubit_width = pulse_sequence_options['qubit_width']

		if use_pump:
			# Target control frequency in Hz of the pump
			pump_frequency = pump_frequency_opt

		## Repetitions
		N_repetitions = pulse_sequence_options['N_repetitions']
		repetitions_list = [0, N_repetitions - 1, N_repetitions]

		data_format = 0
		if reference:
			data_format += 1
		if N_repetitions > 1:
			data_format += 2
		if fast_reference:
			data_format += 4

		point_values = {
			'SQPG': {
				## Parameters for overall pulse sequence - general SGPQ parameters
				'main': {'Truncation range': SQPG_truncation_range, 'Sample rate': SQPG_sampling_rate, 'sequence_duration': SQPG_sequence_duration},
				'qubit': {
					'time_reference': 'absolute',
					'time_offset': (qubit_width / 2) * (SQPG_truncation_range - 1), 'pulse_number': 1,
					'a': qubit_amplitude, 'w': qubit_width, 'v': 0.0, 'f': qubit_IF_frequency,
					'o': 2
					},
				'trigger': {
					'relative_to': 'qubit',
					'time_offset': 0.0, 'time_reference': 'relative', 'relative_marker': 'end',
					'a': 1.5, 'w': 0.0, 'v': 20E-9, 'f': 0.0,
					'o': 4
					},
				'readout': {
					'relative_to': 'trigger',
					'time_offset': 0.0, 'time_reference': 'relative', 'relative_marker': 'end',
					'a': readout_amplitude, 'w': 0.0, 'v': readout_plateau, 'f': readout_IF_frequency,
					'o': 1
					}
				}, # end SQPG
			'Digitizer': {'Number of samples': digitizer_length * digitizer_sampling_rate, 'Number of averages': N_shots},
			'I': {'Modulation frequency': readout_IF_frequency, 'Skip start': demodulation_skip_start, 'Length': demodulation_length},
			'LO1': {'Frequency': readout_frequency - sideband * readout_IF_frequency, 'Power': readout_LO_power},
			'LO2': {'Frequency': qubit_frequency - sideband * qubit_IF_frequency, 'Power': qubit_LO_power},
			'Manual': {
				'Value 1': reference_switch_list[0],
				'Value 2': N_repetitions,
				## Data format
				'Value 10': data_format,
				}
			} # end point values

		if reference:
			iteration_values = {
				'SQPG': {'qubit': {'a': qubit_amplitude_list}},
				'Manual': {'Value 1': reference_switch_list}
				}
			if fast_reference:
				iteration_order = [
					('Manual', 'Value 1'),
					('SQPG', ('qubit', 'Amplitude')),
					] # end iteration order
			else:
				iteration_order = [
					('SQPG', ('qubit', 'Amplitude')),
					('Manual', 'Value 1'),
					] # end iteration order
		else:
			iteration_values = {
				'SQPG': {'qubit': {'a': qubit_amplitude_list}},
				}
			iteration_order = [
				('SQPG', ('qubit', 'Amplitude')),
				] # end iteration order
		# Add repetitions as iteration
		if N_repetitions > 1:
			iteration_values['Manual']['Value 2'] = repetitions_list
			iteration_order.append(('Manual', 'Value 2'))

		## Channel relations - set available quantities
		channel_defs = {
			'SQPG': {
				'main': {'SQPG_delay': 'First pulse delay'},
				'qubit': {'q_w': 'Width', 'q_v': 'Plateau', 'q_s': 'Spacing', 'q_f': 'Mod. frequency', 'q_a': 'Amplitude'},
				'trigger': {'t_w': 'Width', 't_v': 'Plateau', 't_s': 'Spacing',},
				'readout': {'r_w': 'Width', 'r_v': 'Plateau', 'r_s': 'Spacing', 'r_f': 'Mod. frequency'}
				}, # end SQPG
			'Manual': {
				'reference_switch': 'Value 1',
				}  # end Manual
			} # end relation channels

		channel_relations = {
			'SQPG': {
				'qubit': {
					'Amplitude': ['reference_switch * q_a', ['reference_switch', 'q_a']],
					},
				'readout': {
					'Phase': ['(1/2 + 2 * r_f * (SQPG_delay + q_w + q_v + q_s + t_w + t_v + t_s)) * 180', ['SQPG_delay', 'r_f', 'q_w', 'q_v', 'q_s', 't_w', 't_v', 't_s']],
					}
				} # end SQPG
			} # end channel relations
		## end Qubit_Rabi_amplitude


	elif pulse_sequence == 'Qubit_T1':#TESTED 2019.03.27
		reference = pulse_sequence_options['reference']
		fast_reference = pulse_sequence_options['fast_reference']

		# Target frequency in Hz of the readout square pulse
		readout_frequency = readout_frequency_opt
		# Amplitude in V of the readout square pulse
		readout_amplitude = readout_amplitude_opt
		# Duration in seconds of the readout square pulse
		readout_plateau = readout_plateau_opt

		# Target control frequency in Hz of the qubit control gaussian pulse
		qubit_frequency = qubit_frequency_opt
		# Amplitude in V of the qubit control gaussian pulse
		if reference:
			qubit_amplitude_list = [qubit_amplitude_pi, 0.0, 2]
			qubit_amplitude = qubit_amplitude_list[0]
		else:
			qubit_amplitude = qubit_amplitude_pi
		# Width in seconds of the qubit control gaussian pulse
		qubit_width = qubit_width_pi

		if use_pump:
			# Target control frequency in Hz of the pump
			pump_frequency = pump_frequency_opt

		# Free evolution time in seconds
		tau_list = pulse_sequence_options['tau_list']
		max_tau = tau_list[1]

		## Repetitions
		N_repetitions = pulse_sequence_options['N_repetitions']
		repetitions_list = [0, N_repetitions - 1, N_repetitions]

		data_format = 0
		if reference:
			data_format += 1
		if N_repetitions > 1:
			data_format += 2
		if fast_reference:
			data_format += 4

		point_values = {
			'SQPG': {
				## Parameters for overall pulse sequence - general SGPQ parameters
				'main': {'Truncation range': SQPG_truncation_range, 'Sample rate': SQPG_sampling_rate, 'sequence_duration': SQPG_sequence_duration},
				'qubit': {
					'time_reference': 'absolute',
					'time_offset': 0.0, 'pulse_number': 1,
					'a': qubit_amplitude, 'w': qubit_width, 'v': 0.0, 'f': qubit_IF_frequency,
					'o': 2
					},
				'trigger': {'relative_to': 'qubit',
					'time_offset': (qubit_width / 2) * (SQPG_truncation_range - 1), 'time_reference': 'relative', 'relative_marker': 'end',
					'a': 1.5, 'w': 0.0, 'v': 20E-9, 'f': 0.0,
					'o': 4
					},
				'readout': {'relative_to': 'trigger',
					'time_offset': 0.0, 'time_reference': 'relative', 'relative_marker': 'end',
					'a': readout_amplitude, 'w': 0.0, 'v': readout_plateau, 'f': readout_IF_frequency,
					'o': 1
					}
				}, # end SQPG
			'Digitizer': {'Number of samples': digitizer_length * digitizer_sampling_rate, 'Number of averages': N_shots},
			'I': {'Modulation frequency': readout_IF_frequency, 'Skip start': demodulation_skip_start, 'Length': demodulation_length},
			'LO1': {'Frequency': readout_frequency - sideband * readout_IF_frequency, 'Power': readout_LO_power},
			'LO2': {'Frequency': qubit_frequency - sideband * qubit_IF_frequency, 'Power': qubit_LO_power},
			'Manual': {
				'Value 1': tau_list,
				'Value 2': max_tau,
				'Value 4': N_repetitions,
				##
				'Value 10': data_format,
				}
			} # end point values
		if measure_Q:
			point_values['Q'] = {'Modulation frequency': readout_IF_frequency, 'Skip start': demodulation_skip_start, 'Length': demodulation_length}
		if use_pump:
			point_values['LO3'] = {'Frequency': pump_frequency - sideband * pump_IF_frequency, 'Power': pump_LO_power}
		if use_current_source:
			point_values['Current source'] = {'Current': current}

		if reference:
			iteration_values = {
				'SQPG': {'qubit': {'a': qubit_amplitude_list}},
				'Manual': {'Value 1': tau_list}
				}
			if fast_reference:
				iteration_order = [
					('SQPG', ('qubit', 'Amplitude')),
					('Manual', 'Value 1'),
					] # end iteration order
			else:
				iteration_order = [
					('Manual', 'Value 1'),
					('SQPG', ('qubit', 'Amplitude')),
					] # end iteration order
		else: # no reference
			iteration_values = {
				'Manual': {'Value 1': tau_list}
				}
			iteration_order = [
				('Manual', 'Value 1')
				] # end iteration order
			# end reference
		# Add repetitions as iteration
		if N_repetitions > 1:
			iteration_values['Manual']['Value 4'] = repetitions_list
			iteration_order.append(('Manual', 'Value 4'))

		## Channel relations - set available quantities (could be outsourced to rcfile?)
		channel_defs = {
			'SQPG': {
				'main': {'SQPG_truncation_range': 'Truncation range', 'SQPG_delay': 'First pulse delay'},
				'qubit': {'q_w': 'Width', 'q_v': 'Plateau', 'q_s': 'Spacing', 'q_f': 'Mod. frequency'},
				'trigger': {'t_w': 'Width', 't_v': 'Plateau', 't_s': 'Spacing',},
				'readout': {'r_w': 'Width', 'r_v': 'Plateau', 'r_s': 'Spacing', 'r_f': 'Mod. frequency'}
				}, # end SQPG
			'Manual': {
			   'tau': 'Value 1',
			   'max_tau': 'Value 2',
				} # end Manual
			} # end relation channels

		channel_relations = {
			'SQPG': {
				'main': {
					'First pulse delay': ['max_tau - tau + (q_w / 2) * (SQPG_truncation_range - 1)', ['max_tau', 'tau', 'SQPG_truncation_range', 'q_w']],
					},
				'qubit': {
					'Spacing': ['tau + (q_w / 2) * (SQPG_truncation_range - 1)', ['SQPG_truncation_range', 'tau', 'q_w']],
					'Phase': ['(1/2 + 2 * q_f * (SQPG_delay)) * 180', ['SQPG_truncation_range', 'q_f', 'SQPG_delay']],
					},
				'readout': {
					'Phase': ['(1/2 + 2 * r_f * (SQPG_delay + q_w + q_v + q_s + t_w + t_v + t_s)) * 180', ['SQPG_delay', 'r_f', 'q_w', 'q_v', 'q_s', 't_w', 't_v', 't_s']]
					},
				}, # end SQPG
			} # end channel relations
		## end Qubit_T1

	elif pulse_sequence == 'Qubit_Ramsey':#TESTED 2019.03.27
		reference = pulse_sequence_options['reference']
		fast_reference = pulse_sequence_options['fast_reference']

		# Target frequency in Hz of the readout square pulse
		readout_frequency = readout_frequency_opt
		# Amplitude in V of the readout square pulse
		readout_amplitude = readout_amplitude_opt
		# Duration in seconds of the readout square pulse
		readout_plateau = readout_plateau_opt

		intentional_detuning = pulse_sequence_options['intentional_detuning']

		# Target control frequency in Hz of the qubit control gaussian pulse
		qubit_frequency = qubit_frequency_opt - intentional_detuning
		# Amplitude in V of the qubit control gaussian pulse
		if reference:
			qubit_amplitude_list = [qubit_amplitude_pi / 2, 0, 2]
			qubit_amplitude = qubit_amplitude_list[0]
		else:
			qubit_amplitude = qubit_amplitude_pi / 2
		# Width in seconds of the qubit control gaussian pulse
		qubit_width = qubit_width_pi

		if use_pump:
			# Target control frequency in Hz of the pump
			pump_frequency = pump_frequency_opt

		# Free evolution time in seconds
		tau_list = pulse_sequence_options['tau_list']
		max_tau = tau_list[1]

		## DRAG coefficient
		if pulse_sequence_options['use_DRAG']:
			DRAG_coefficient = general_options['DRAG_coefficient'][qubit_width]
		else:
			DRAG_coefficient = 0.0

		## Repetitions
		N_repetitions = pulse_sequence_options['N_repetitions']
		repetitions_list = [0, N_repetitions - 1, N_repetitions]

		data_format = 0
		if reference:
			data_format += 1
		if N_repetitions > 1:
			data_format += 2
		if fast_reference:
			data_format += 4

		point_values = {
			'SQPG': {
				## Parameters for overall pulse sequence - general SGPQ parameters
				'main': {'Truncation range': SQPG_truncation_range, 'Sample rate': SQPG_sampling_rate, 'sequence_duration': SQPG_sequence_duration},
				'qubit1': {
					'time_reference': 'absolute',
					'time_offset': 0.0, 'pulse_number': 1,
					'a': qubit_amplitude, 'w': qubit_width, 'v': 0.0, 'f': qubit_IF_frequency,
					'o': 2, 'DRAG': DRAG_coefficient,
					},
				'qubit2': {'relative_to': 'qubit1',
					'time_offset': 0.0, 'time_reference': 'relative', 'relative_marker': 'end',
					'a': qubit_amplitude, 'w': qubit_width, 'v': 0.0, 'f': qubit_IF_frequency,
					'o': 2, 'DRAG': DRAG_coefficient,
					},
				'trigger': {'relative_to': 'qubit2',
					'time_offset': 0.0, 'time_reference': 'relative', 'relative_marker': 'end',
					'a': 1.5, 'w': 0.0, 'v': 20E-9, 'f': 0.0,
					'o': 4
					},
				'readout': {'relative_to': 'trigger',
					'time_offset': 0.0, 'time_reference': 'relative', 'relative_marker': 'end',
					'a': readout_amplitude, 'w': 0.0, 'v': readout_plateau, 'f': readout_IF_frequency,
					'o': 1
					}
				}, # end SQPG
			'Digitizer': {'Number of samples': digitizer_length * digitizer_sampling_rate, 'Number of averages': N_shots},
			'I': {'Modulation frequency': readout_IF_frequency, 'Skip start': demodulation_skip_start, 'Length': demodulation_length},
			'LO1': {'Frequency': readout_frequency - sideband * readout_IF_frequency, 'Power': readout_LO_power},
			'LO2': {'Frequency': qubit_frequency - sideband * qubit_IF_frequency, 'Power': qubit_LO_power},
			'Manual': {
				'Value 1': tau_list,
				'Value 2': max_tau,
				'Value 3': intentional_detuning,
				'Value 4': N_repetitions,
				## Data format
				'Value 10': data_format,
				}
			} # end point values
		## Optional point values
		if measure_Q:
			point_values['Q'] = {'Modulation frequency': readout_IF_frequency, 'Skip start': demodulation_skip_start, 'Length': demodulation_length}
		if use_pump:
			point_values['LO3'] = {'Frequency': pump_frequency - sideband * pump_IF_frequency, 'Power': pump_LO_power}
		if use_current_source:
			point_values['Current source'] = {'Current': current}

		if reference:
			iteration_values = {
				'SQPG': {'qubit1': {'a': qubit_amplitude_list}},
				'Manual': {
					'Value 1': tau_list,
					},
				}
			if fast_reference:
				iteration_order = [
					('SQPG', ('qubit1', 'Amplitude')),
					('Manual', 'Value 1'),
					] # end iteration order
			else: # not fast reference
				iteration_order = [
					('Manual', 'Value 1'),
					('SQPG', ('qubit1', 'Amplitude')),
					] # end iteration order
		else:
			iteration_values = {
				'Manual': {
					'Value 1': tau_list,
					}
				}
			iteration_order = [
				('Manual', 'Value 1')
				] # end iteration order
		# Add repetitions as iteration
		if N_repetitions > 1:
			iteration_values['Manual']['Value 4'] = repetitions_list
			iteration_order.append(('Manual', 'Value 4'))

		## Channel relations - set available quantities (could be outsourced to rcfile?)
		channel_defs = {
			'SQPG': {
				'main': {'SQPG_truncation_range': 'Truncation range', 'SQPG_delay': 'First pulse delay'},
				'qubit1': {'q1_w': 'Width', 'q1_v': 'Plateau', 'q1_s': 'Spacing', 'q1_f': 'Mod. frequency', 'q1_a': 'Amplitude'},
				'qubit2': {'q2_w': 'Width', 'q2_v': 'Plateau', 'q2_s': 'Spacing', 'q2_f': 'Mod. frequency', 'q2_a': 'Amplitude'},
				'trigger': {'t_w': 'Width', 't_v': 'Plateau', 't_s': 'Spacing',},
				'readout': {'r_w': 'Width', 'r_v': 'Plateau', 'r_s': 'Spacing', 'r_f': 'Mod. frequency'}
				}, # end SQPG
			'Manual': {
			   'tau': 'Value 1',
			   'max_tau': 'Value 2',
				} # end Manual
			} # end relation channels

		channel_relations = {
			'SQPG': {
				'main': {
					'First pulse delay': ['max_tau - tau + (q1_w / 2) * (SQPG_truncation_range - 1)', ['max_tau', 'tau', 'SQPG_truncation_range', 'q1_w']],
					},
				'qubit1': {
					'Spacing': ['tau - (q1_w + q2_w) / 2', ['tau', 'q1_w', 'q2_w']],
					},
				 'qubit2': {
					'Amplitude': ['q1_a', ['q1_a']],
					},
				'readout': {
					'Phase': ['(1/2 + 2 * r_f * (SQPG_delay + q1_w + q1_v + q1_s + q2_w + q2_v + q2_s + t_w + t_v + t_s)) * 180', ['SQPG_delay', 'r_f', 'q1_w', 'q1_v', 'q1_s', 'q2_w', 'q2_v', 'q2_s', 't_w', 't_v', 't_s']]
					},
				}, # end SQPG
			} # end channel relations
		## end Qubit_Ramsey

	elif pulse_sequence == 'Qubit_echo':#TESTED 2019.03.27
		reference = pulse_sequence_options['reference']
		fast_reference = pulse_sequence_options['fast_reference']

		# Target frequency in Hz of the readout square pulse
		readout_frequency = readout_frequency_opt
		# Amplitude in V of the readout square pulse
		readout_amplitude = readout_amplitude_opt
		# Duration in seconds of the readout square pulse
		readout_plateau = readout_plateau_opt

		# Target control frequency in Hz of the qubit control gaussian pulse
		qubit_frequency = qubit_frequency_opt
		# Amplitude in V of the qubit control gaussian pulse
		if reference:
			qubit_amplitude_list = [qubit_amplitude_pi / 2, 0.0, 2]
			qubit_amplitude = qubit_amplitude_list[0]
		else:
			qubit_amplitude = qubit_amplitude_pi / 2
		# Width in seconds of the qubit control gaussian pulse
		qubit_width = qubit_width_pi

		if use_pump:
			# Target control frequency in Hz of the pump
			pump_frequency = pump_frequency_opt

		# Free evolution time in seconds
		tau_list = pulse_sequence_options['tau_list']
		max_tau = tau_list[1]

		## Repetitions
		N_repetitions = pulse_sequence_options['N_repetitions']
		repetitions_list = [0, N_repetitions - 1, N_repetitions]

		data_format = 0
		if reference:
			data_format += 1
		if N_repetitions > 1:
			data_format += 2
		if fast_reference:
			data_format += 4

		point_values = {
			'SQPG': {
				## Parameters for overall pulse sequence - general SGPQ parameters
				'main': {'Truncation range': SQPG_truncation_range, 'Sample rate': SQPG_sampling_rate, 'sequence_duration': SQPG_sequence_duration},
				'qubit1': {
					'time_reference': 'absolute',
					'time_offset': 0.0, 'pulse_number': 1,
					'a': qubit_amplitude, 'w': qubit_width, 'v': 0.0, 'f': qubit_IF_frequency,
					'o': 2
					},
				'qubit2': {'relative_to': 'qubit1',
					'time_offset': 0.0, 'time_reference': 'relative', 'relative_marker': 'end',
					'a': 2 * qubit_amplitude, 'w': qubit_width, 'v': 0.0, 'f': qubit_IF_frequency,
					'o': 2
					},
				'qubit3': {'relative_to': 'qubit2',
					'time_offset': 0.0, 'time_reference': 'relative', 'relative_marker': 'end',
					'a': qubit_amplitude, 'w': qubit_width, 'v': 0.0, 'f': qubit_IF_frequency, 'p': 180.0,
					'o': 2
					},
				'trigger': {'relative_to': 'qubit3',
					'time_offset': 0.0, 'time_reference': 'relative', 'relative_marker': 'end',
					'a': 1.5, 'w': 0.0, 'v': 20E-9, 'f': 0.0,
					'o': 4
					},
				'readout': {'relative_to': 'trigger',
					'time_offset': 0.0, 'time_reference': 'relative', 'relative_marker': 'end',
					'a': readout_amplitude, 'w': 0.0, 'v': readout_plateau, 'f': readout_IF_frequency,
					'o': 1
					}
				}, # end SQPG
			'Digitizer': {'Number of samples': digitizer_length * digitizer_sampling_rate, 'Number of averages': N_shots},
			'I': {'Modulation frequency': readout_IF_frequency, 'Skip start': demodulation_skip_start, 'Length': demodulation_length},
			'LO1': {'Frequency': readout_frequency - sideband * readout_IF_frequency, 'Power': readout_LO_power},
			'LO2': {'Frequency': qubit_frequency - sideband * qubit_IF_frequency, 'Power': qubit_LO_power},
			'Manual': {
				'Value 1': tau_list,
				'Value 2': max_tau,
				'Value 4': N_repetitions,
				## Data format
				'Value 10': data_format,
				}
			} # end point values
		## Optional point values
		if measure_Q:
			point_values['Q'] = {'Modulation frequency': readout_IF_frequency, 'Skip start': demodulation_skip_start, 'Length': demodulation_length}
		if use_pump:
			point_values['LO3'] = {'Frequency': pump_frequency - sideband * pump_IF_frequency, 'Power': pump_LO_power}
		if use_current_source:
			point_values['Current source'] = {'Current': current}

		if reference:
			iteration_values = {
				'SQPG': {'qubit1': {'a': qubit_amplitude_list}},
				'Manual': {'Value 1': tau_list}
				}
			if fast_reference:
				iteration_order = [
					('SQPG', ('qubit1', 'Amplitude')),
					('Manual', 'Value 1'),
					] # end iteration order
			else:
				iteration_order = [
					('Manual', 'Value 1'),
					('SQPG', ('qubit1', 'Amplitude'))
					] # end iteration order
		else:
			iteration_values = {
				'Manual': {'Value 1': tau_list}
				}
			iteration_order = [
				('Manual', 'Value 1'),
				] # end iteration order
			# end reference
		# Add repetitions as iteration
		if N_repetitions > 1:
			iteration_values['Manual']['Value 4'] = repetitions_list
			iteration_order.append(('Manual', 'Value 4'))

		## Channel relations - set available quantities (could be outsourced to rcfile?)
		channel_defs = {
			'SQPG': {
				'main': {'SQPG_truncation_range': 'Truncation range', 'SQPG_delay': 'First pulse delay'},
				'qubit1': {'q1_w': 'Width', 'q1_v': 'Plateau', 'q1_s': 'Spacing', 'q1_f': 'Mod. frequency', 'q1_a': 'Amplitude'},
				'qubit2': {'q2_w': 'Width', 'q2_v': 'Plateau', 'q2_s': 'Spacing', 'q2_f': 'Mod. frequency', 'q2_a': 'Amplitude'},
				'qubit3': {'q3_w': 'Width', 'q3_v': 'Plateau', 'q3_s': 'Spacing', 'q3_f': 'Mod. frequency', 'q3_a': 'Amplitude'},
				'trigger': {'t_w': 'Width', 't_v': 'Plateau', 't_s': 'Spacing',},
				'readout': {'r_w': 'Width', 'r_v': 'Plateau', 'r_s': 'Spacing', 'r_f': 'Mod. frequency'}
				}, # end SQPG
			'Manual': {
			   'tau': 'Value 1',
			   'max_tau': 'Value 2',
				} # end Manual
			} # end relation channels

		channel_relations = {
			'SQPG': {
				'main': {
					'First pulse delay': ['max_tau - tau + (q1_w / 2) * (SQPG_truncation_range - 1)', ['max_tau', 'tau', 'SQPG_truncation_range', 'q1_w']],
					},
				'qubit1': {
					'Spacing': ['(tau / 2) - (q1_w + q2_w) / 2', ['tau', 'q1_w', 'q2_w']],
					},
				'qubit2': {
					'Spacing': ['(tau / 2) - (q2_w + q3_w) / 2', ['tau', 'q2_w', 'q3_w']],
					'Amplitude': ['2 * q1_a', ['q1_a']],
					},
				'qubit3': {
					'Amplitude': ['q1_a', ['q1_a']],
					},
				'readout': {
					'Phase': ['(1/2 + 2 * r_f * (SQPG_delay + q1_w + q1_v + q1_s + q2_w + q2_v + q2_s + q3_w + q3_v + q3_s + t_w + t_v + t_s)) * 180', ['SQPG_delay', 'r_f', 'q1_w', 'q1_v', 'q1_s', 'q2_w', 'q2_v', 'q2_s', 'q3_w', 'q3_v', 'q3_s', 't_w', 't_v', 't_s']]
					},
				}, # end SQPG
			} # end channel relations
		## end Qubit_echo


	elif pulse_sequence == 'Qubit_single_shot':#single-shot

		# Overwrites the number of shots set for averaged measurements
		N_shots = 1

		# Target frequency in Hz of the readout square pulse
		readout_frequency = readout_frequency_opt
		# Amplitude in V of the readout square pulse
		readout_amplitude = readout_amplitude_opt
		# Duration in seconds of the readout square pulse
		readout_plateau = readout_plateau_opt

		# Target control frequency in Hz of the qubit control gaussian pulse
		qubit_frequency = qubit_frequency_opt
		# Amplitude in V of the qubit control gaussian pulse
		qubit_amplitude_list = [0.0, qubit_amplitude_pi, 2]
		# Width in seconds of the qubit control gaussian pulse
		qubit_width = qubit_width_pi

		if use_pump:
			# Target control frequency in Hz of the pump
			pump_frequency = pump_frequency_opt

		# Number of single shots per repetition
		N_single_shots = pulse_sequence_options['N_single_shots']
		# Number of repetitions, so the total number of shots is N_single_shots * N_repetitions
		N_repetitions = pulse_sequence_options['N_repetitions']

		repetitions_list = [0, N_repetitions - 1, N_repetitions]

		point_values = {
			'SQPG': {
				## Parameters for overall pulse sequence - general SGPQ parameters
				'main': {
					'Truncation range': SQPG_truncation_range, 'Sample rate': SQPG_sampling_rate, 'sequence_duration': SQPG_sequence_duration
					},
				'qubit': {
					'time_reference': 'absolute',
					'time_offset': (qubit_width / 2) * (SQPG_truncation_range - 1), 'pulse_number': 1,
					'a': qubit_amplitude_list[0], 'w': qubit_width, 'v': 0.0, 'f': qubit_IF_frequency,
					'o': 2
					},
				'trigger': {'relative_to': 'qubit',
					'time_offset': 0.0, 'time_reference': 'relative', 'relative_marker': 'end',
					'a': 1.5, 'w': 0.0, 'v': 20E-9, 'f': 0.0,
					'o': 4
					},
				'readout': {'relative_to': 'trigger',
					'time_offset': 0.0, 'time_reference': 'relative', 'relative_marker': 'end',
					'a': readout_amplitude, 'w': 0.0, 'v': readout_plateau, 'f': readout_IF_frequency,
					'o': 1
					}
				}, # end SQPG
			'Digitizer': {'Number of samples': digitizer_length * digitizer_sampling_rate, 'Number of averages': N_shots, 'Number of records': N_single_shots},
			'I': {'Modulation frequency': readout_IF_frequency, 'Skip start': demodulation_skip_start, 'Length': demodulation_length, 'Number of segments': N_single_shots},
			'LO1': {'Frequency': readout_frequency - sideband * readout_IF_frequency, 'Power': readout_LO_power},
			'LO2': {'Frequency': qubit_frequency - sideband * qubit_IF_frequency, 'Power': qubit_LO_power},
			'Manual': {
				'Value 1': repetitions_list,
				'Value 4': N_repetitions,
				## Data format
				'Value 10': data_format,
				}
			} # end point values
		## Optional point values
		if measure_Q:
			point_values['Q'] = {'Modulation frequency': readout_IF_frequency, 'Skip start': demodulation_skip_start, 'Length': demodulation_length}
		if use_pump:
			point_values['LO3'] = {'Frequency': pump_frequency - sideband * pump_IF_frequency, 'Power': pump_LO_power}
		if use_current_source:
			point_values['Current source'] = {'Current': current}

		iteration_values = {
			'SQPG': {'qubit': {'a': qubit_amplitude_list}},
			'Manual': {'Value 1': repetitions_list}
			}

		iteration_order = [
			('Manual', 'Value 1'),
			('SQPG', ('qubit', 'Amplitude'))
			] # end iteration order

		## Channel relations - set available quantities (could be outsourced to rcfile?)
		channel_defs = {
			'SQPG': {
				'main': {'SQPG_truncation_range': 'Truncation range', 'SQPG_delay': 'First pulse delay'},
				'qubit': {'q_w': 'Width', 'q_v': 'Plateau', 'q_s': 'Spacing', 'q_f': 'Mod. frequency'},
				'trigger': {'t_w': 'Width', 't_v': 'Plateau', 't_s': 'Spacing',},
				'readout': {'r_w': 'Width', 'r_v': 'Plateau', 'r_s': 'Spacing', 'r_f': 'Mod. frequency'}
				}, # end SQPG
			'Manual': {
			   'SQPG_sequence_duration': 'Value 2'
				} # end Manual
			} # end relation channels

		channel_relations = {
			'SQPG': {
				'readout': {
					'Phase': ['(1/2 + 2 * r_f * (SQPG_delay + q_w + q_v + q_s + t_w + t_v + t_s)) * 180', ['SQPG_delay', 'r_f', 'q_w', 'q_v', 'q_s', 't_w', 't_v', 't_s']]
					},
				}, # end SQPG
			} # end channel relations
		## end Qubit_single_shot# single-shot


	elif pulse_sequence == 'DRAG_optimization':#TESTED 2019.03.27#MultiPulse

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

		if use_pump:
			# Target control frequency in Hz of the pump
			pump_frequency = pump_frequency_opt

		# DRAG coefficient
		iterate_DRAG = pulse_sequence_options['iterate_DRAG']
		if iterate_DRAG:
			DRAG_coefficient_list = pulse_sequence_options['DRAG_list']
			DRAG_coefficient = DRAG_coefficient_list[0]
		else:
			DRAG_coefficient = general_options['DRAG_coefficient'][qubit_width]

		# Number of repetitions
		N_repetitions = pulse_sequence_options['N_repetitions']
		repetitions_list = [0, int(N_repetitions - 1), int(N_repetitions)]

		data_format = 0
		if N_repetitions > 1:
			data_format += 2

		## MultiPulse pulse definitions
		pulse_defs = []
		# Trigger
		pulse_defs.append({
			'a': 1.5,
			'w': 0e-9,
			'v': 20e-9,
			's': 0e-9,
			'f': 0e6,
			'o': 4,
			'p': 0})
		# Readout
		pulse_defs.append({
			'a': readout_amplitude,
			'w': 0e-9,
			'v': readout_plateau,
			's': 0e-9,
			'f': readout_IF_frequency,
			'o': 1,
			'p': 90,
			'fix_phase': 1})
		## Qubit pulses
		# X90
		pulse_defs.append({
			'a': qubit_amplitude / 2,
			'w': qubit_width,
			'v': 0e-9,
			's': qubit_width,
			'f': qubit_IF_frequency,
			'o': 2,
			'p': 0,
			'DRAG': 0.0})
		# Xr90
		pulse_defs.append({
			'a': qubit_amplitude / 2,
			'w': qubit_width,
			'v': 0e-9,
			's': qubit_width,
			'f': qubit_IF_frequency,
			'o': 2,
			'p': 180,
			'DRAG': 0.0})
		## Save pulse definitions to file
		pulse_def_key_order = ['a', 'w', 'v', 's', 'f', 'p', 'o', 'DRAG', 'fix_phase']
		pulse_def_path = os.path.abspath(pulse_sequence_options['pulse_def_file'])
		writePulseDefs(pulse_def_path, pulse_defs, pulse_def_key_order)
		psictInterface.log('Pulse definitions written to file: {}'.format(pulse_def_path))

		## Generate pulse sequences
		pulse_seq_list = []
		n_blocks_list = np.linspace(*pulse_sequence_options['number_of_gates'], dtype='int')
		for n_blocks in n_blocks_list:
			## Generate imperfect identities
			pulse_seq = [2,3]*n_blocks
			## Add trigger and readout pulses
			pulse_seq += [0,1]
			## Append to sequences list
			pulse_seq_list.append(pulse_seq)
		n_pulse_seqs = n_blocks_list.shape[0]
		## Write pulse sequences to file
		pulse_seq_path = os.path.abspath(pulse_sequence_options['pulse_seq_file'])
		writePulseSeqs(pulse_seq_path, pulse_seq_list)
		psictInterface.log('Pulse sequences written to file: {}'.format(pulse_seq_path))

		point_values = {
			'MultiPulse': {
					'Number of points': int(general_options['MultiPulse_sampling_rate']*general_options['MultiPulse_sequence_duration']),
					'First pulse delay': pulse_sequence_options['First pulse delay'],
					'Generate from final pulse': pulse_sequence_options['Generate from final pulse'],
					'Final pulse time': pulse_sequence_options['Final pulse time'],
					'Use global DRAG': pulse_sequence_options['Use global DRAG'],
					'Global DRAG coefficient': DRAG_coefficient,
					'Apply DRAG to square pulses': 0,
				}, # end MultiPulse
			'Digitizer': {'Number of samples': digitizer_length * digitizer_sampling_rate, 'Number of averages': N_shots},
			'I': {'Modulation frequency': readout_IF_frequency, 'Skip start': demodulation_skip_start, 'Length': demodulation_length},
			'LO1': {'Frequency': readout_frequency - sideband * readout_IF_frequency, 'Power': readout_LO_power},
			'LO2': {'Frequency': qubit_frequency - sideband * qubit_IF_frequency, 'Power': qubit_LO_power},
			'Manual': {
				'Value 10': data_format,
			},
		} # end point values
		if measure_Q:
			point_values['Q'] = {'Modulation frequency': readout_IF_frequency, 'Skip start': demodulation_skip_start, 'Length': demodulation_length}
		if use_pump:
			point_values['LO3'] = {'Frequency': pump_frequency - sideband * pump_IF_frequency, 'Power': pump_LO_power}
		if use_current_source:
			point_values['Current source'] = {'Current': current}

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

		if iterate_DRAG:
			if N_repetitions == 1:
				iteration_values = {
					'MultiPulse': {
						'Pulse sequence counter': [0, n_pulse_seqs - 1, n_pulse_seqs],
						'Global DRAG coefficient': DRAG_coefficient_list,
						},
					}

				iteration_order = [
					('MultiPulse', 'Pulse sequence counter'),
					('MultiPulse', 'Global DRAG coefficient'),
					] # end iteration order
			else: # multiple repetitions
				iteration_values = {
					'MultiPulse': {
						'Pulse sequence counter': [0, n_pulse_seqs - 1, n_pulse_seqs],
						'Global DRAG coefficient': DRAG_coefficient_list,
						},
					'Manual': {'Value 1': repetitions_list},
					}

				iteration_order = [
					('MultiPulse', 'Pulse sequence counter'),
					('MultiPulse', 'Global DRAG coefficient'),
					('Manual', 'Value 1'),
					] # end iteration order
		else: # Do not iterate DRAG parameter
			if N_repetitions == 1:
				iteration_values = {
					'MultiPulse': {
						'Pulse sequence counter': [0, n_pulse_seqs - 1, n_pulse_seqs],
						},
					}

				iteration_order = [
					('MultiPulse', 'Pulse sequence counter'),
					] # end iteration order
			else: # multiple repetitions
				iteration_values = {
					'MultiPulse': {'Pulse sequence counter': [0, n_pulse_seqs - 1, n_pulse_seqs]},
					'Manual': {'Value 1': repetitions_list},
					}

				iteration_order = [
					('MultiPulse', 'Pulse sequence counter'),
					('Manual', 'Value 1'),
					] # end iteration order

		## Channel relations - set available quantities (could be outsourced to rcfile?)
		channel_defs = {
			} # end relation channels

		channel_relations = {
			} # end channel relations
		## end DRAG_optimization

	#############################################################################
	## Set parameters & measure
	#############################################################################

	# psictInterface.labberExporter.set_server_name('localhost')

	## Set input parameter values
	psictInterface.set_point_values(point_values)
	psictInterface.set_iteration_values(iteration_values, iteration_order)
	psictInterface.set_channel_relations(channel_defs, channel_relations)

	## Run measurement
	psictInterface.perform_measurement(dry_run = True)

	## Copy additional files used in RB - this will be integrated at some point
	if pulse_sequence in ['DRAG_optimization', 'Randomized_benchmarking']:
		## Extract file ID component from output path
		file_ID = os.path.splitext(os.path.basename(psictInterface.fileManager.output_path))[0]
		## Copy pulse definitions file
		pulse_def_target_path = os.path.join(PSICT_options['script_copy_target_dir'], file_ID+'_MultiPulse_definitions.txt')
		shutil.copy(pulse_def_path, pulse_def_target_path)
		psictInterface.log('RB pulse definitions file copied to {}'.format(pulse_def_target_path))
		## Copy pulse sequences file
		pulse_seq_target_path = os.path.join(PSICT_options['script_copy_target_dir'], file_ID+'_MultiPulse_sequences.txt')
		shutil.copy(pulse_seq_path, pulse_seq_target_path)
		psictInterface.log('RB pulse sequences file copied to {}'.format(pulse_seq_target_path))

	return psictInterface.fileManager.output_path

	##

if __name__ == '__main__':
	## This block will only be executed if the worker is run explicitly as a standalone script

	# print('Running as a standalone script...')

	worker_PSICT_options['running_as_worker'] = False
	worker_PSICT_options['parent_logger_name'] = None

	run_pulse_sequence(pulse_sequence, worker_PSICT_options, worker_general_options, worker_pulse_sequence_options)

else:
	## This block will only be run when the worker is imported (ie 'run' through a master script)

	# print('Running as worker script...')
	worker_PSICT_options['running_as_worker'] = True

##
