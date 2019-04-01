import os
import sys
import shutil
import numpy as np
import time

from numpy import pi

## WorkerScriptManager for automation
from PSICT_extras.WorkerScriptManager import WorkerScriptManager, get_user_confirmation, increment_filename

## Analysis functions
sys.path.append('../../Analysis/Analysis_scripts/')
from Qubit_Ramsey_lmfit import qubit_Ramsey_analysis_lmfit
# from Qubit_Rabi_amplitude import qubit_Rabi_amplitude_analysis
# from DRAG_optimization import DRAG_optimization_analysis

##############################################################################
## WorkerScriptManager object setup
##############################################################################

## Initialise WorkerScriptManager object
workerMgr = WorkerScriptManager('test_script.py')
workerMgr.set_PSICT_config('PSICT_config.py')

## Get options dicts from workerMgr object
PSICT_options = workerMgr.PSICT_options
general_options = workerMgr.general_options
pulse_sequence_options = workerMgr.pulse_sequence_options

## Set script copy target dir from worker
workerMgr.set_script_copy_target_dir(PSICT_options['script_copy_target_dir'])
## Set analysis path for saving figures
analysis_dir = '../../test_output_files/analysis'

#############################################################################
## Experiments

intentional_detuning = -4.0E6

#############################################################################
## Qubit_Ramsey

## Set values
pulse_sequence_options['Qubit_Ramsey']['fast_reference'] = True
pulse_sequence_options['Qubit_Ramsey']['intentional_detuning'] = intentional_detuning
pulse_sequence_options['Qubit_Ramsey']['tau_list'] = [0E-9, 4000E-9, 201]
pulse_sequence_options['Qubit_Ramsey']['repetitions'] = 4
## Update in workerMgr object
workerMgr.set_parameters(PSICT_options, general_options, pulse_sequence_options)

old_filename = PSICT_options['output_file']

## Run measurement
workerMgr.run_measurement('Qubit_Ramsey')
## Update master dicts to reflect new values
PSICT_options, general_options, pulse_sequence_options = workerMgr.get_parameters()

## Copy existing file (to work with auto-incrementation)
shutil.copy(os.path.join(PSICT_options['output_dir'], 'labber_test_0000.hdf5'), \
			os.path.join(PSICT_options['output_dir'], old_filename+'.hdf5'))

## Analysis
Ramsey_analysis_options = {'save_figures': True, 'show_figures': False}
Ramsey_analysis_parameters = {} #{'intentional_detuning': intentional_detuning}
Ramsey_results = qubit_Ramsey_analysis_lmfit(workerMgr.output_dir, analysis_dir, workerMgr.output_filename, **Ramsey_analysis_options, **Ramsey_analysis_parameters)

## Status messages
print(u'+++ T_2_star       = {:.1f} +/- {:.1f} ns'.format(Ramsey_results['T_2_star'][0], Ramsey_results['T_2_star'][1]))
print(u'+++ Delta_s/2pi    = {:.3f} +/- {:.3f} MHz'.format(Ramsey_results['Delta_s'][0] * 1E3 / (2 * pi), Ramsey_results['Delta_s'][1] * 1E3 / (2 * pi)))

#############################################################################
## Qubit_T1

## Set values
pulse_sequence_options['Qubit_T1']['fast_reference'] = True
pulse_sequence_options['Qubit_T1']['tau_list'] = [0E-9, 10000E-9, 101]
pulse_sequence_options['Qubit_T1']['repetitions'] = 4
## Update in workerMgr object
workerMgr.set_parameters(PSICT_options, general_options, pulse_sequence_options)

## Run measurement
workerMgr.run_measurement('Qubit_T1')
## Update master dicts to reflect new values
PSICT_options, general_options, pulse_sequence_options = workerMgr.get_parameters()

#############################################################################
## Qubit_echo

## Set values
pulse_sequence_options['Qubit_echo']['fast_reference'] = True
pulse_sequence_options['Qubit_echo']['tau_list'] = [0e-9, 1000e-9, 101]
pulse_sequence_options['Qubit_echo']['repetitions'] = 1
## Update in workerMgr object
workerMgr.set_parameters(PSICT_options, general_options, pulse_sequence_options)

## Run measurement
workerMgr.run_measurement('Qubit_echo')
## Update master dicts to reflect new values
PSICT_options, general_options, pulse_sequence_options = workerMgr.get_parameters()

##############################################################################
## Cleanup
##############################################################################

## Ensure worker script reflects latest values stored in workerMgr object
workerMgr.update_parameters()

##
