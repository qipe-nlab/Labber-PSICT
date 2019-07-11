import os
import sys
import re
import shutil
import importlib.util
import numpy as np
from datetime import datetime
import time
import pathlib
import logging

import PSICT_UIF._include36._LogLevels as LogLevels

## Worker script breakpoints - DO NOT MODIFY
OPTIONS_DICT_BREAKPOINT = '## OPTIONS DICT BREAKPOINT'
SCRIPT_COPY_BREAKPOINT = '## SCRIPT COPY BREAKPOINT'

##############################################################################

## Grouping formatting styles for worker script values
format_groups = {}

format_groups['GHz .6'] = ['readout_frequency_opt', 'qubit_frequency_opt', 'magnon_frequency_opt', 'pump_frequency_opt']
format_groups['MHz int'] = ['readout_IF_frequency', 'qubit_IF_frequency', 'magnon_IF_frequency', 'pump_IF_frequency']
format_groups['MHz .3'] = ['intentional_detuning', 'optimal_detuning']
format_groups['int'] = ['readout_LO_power', 'qubit_LO_power', 'magnon_LO_power', 'pump_IF_frequency', 'SQPG_truncation_range']
format_groups['.2'] = ['magnon_amplitude_alpha', 'magnon_amplitude_beta', 'magnon_phase_beta', 'n_m']
format_groups['.3'] = ['magnon_amplitude', 'pump_amplitude', 'qubit_amplitude', 'readout_amplitude']
format_groups['.4'] = ['readout_amplitude_opt']
format_groups['e rm0'] = ['N_shots', 'SQPG_sampling_rate', 'MultiPulse_sampling_rate', 'digitizer_sampling_rate', 'N_single_shots', 'N_repetitions', 'N_repetitions_2', 'N_pts']
format_groups['e-3 .6'] = ['current']
format_groups['ns'] = ['SQPG_sequence_duration', 'MultiPulse_sequence_duration', 'readout_plateau_opt', 'qubit_width_pi', 'qubit_plateau_pi', 'demodulation_skip_start', 'demodulation_length', 'qubit_width', 'qubit_plateau', 'magnon_width', 'magnon_plateau', 'tau_s', 'tau', 'tau_delay', 'digitizer_length']
format_groups['us'] = ['wait_time']

format_groups['list GHz rm0'] = ['readout_frequency_list', 'qubit_frequency_list', 'magnon_frequency_list']
format_groups['list MHz int'] = ['qubit_drive_detuning_list', 'intentional_detuning_list']
format_groups['list .3'] = ['readout_amplitude_list', 'qubit_amplitude_list', 'n_m_list', 'magnon_amplitude_alpha_list', 'magnon_real_alpha_list', 'magnon_imag_alpha_list']
format_groups['list ns'] = ['qubit_width_list', 'qubit_plateau_list', 'tau_list']

format_groups['dict ns:.6'] = ['qubit_amplitude_pi_dict', 'qubit_amplitude_pi_2_dict']
format_groups['dict ns:1.2'] = ['lambda_dict']

## Function to convert values to correct formatting style
def get_formatted_rep(key, value):
    if isinstance(value, str):
        value_rep = '\''+value+'\''
    ## Single-value formats
    elif key in format_groups['GHz .6']:
        value_rep = '{:.6f}e9'.format(value*1e-9)
    elif key in format_groups['MHz int']:
        value_rep = '{:.0f}e6'.format(value*1e-6)
    elif key in format_groups['MHz .3']:
        value_rep = '{:.3f}e6'.format(value*1e-6)
    elif key in format_groups['int']:
        value_rep = '{:d}'.format(int(value))
    elif key in format_groups['.2']:
        value_rep = '{:.2f}'.format(value)
    elif key in format_groups['.3']:
        value_rep = '{:.3f}'.format(value)
    elif key in format_groups['.4']:
        value_rep = '{:.4f}'.format(value)
    elif key in format_groups['e rm0']:
        mantissa, exponent = '{:e}'.format(value).split('e')
        value_rep = mantissa.rstrip('0').rstrip('.')+'e'+exponent.lstrip('+')
    elif key in format_groups['e-3 .6']:
        value_rep = '{:.6f}e-3'.format(value*1e3)
    elif key in format_groups['ns']:
        value_rep = '{:.0f}e-9'.format(value*1e9)
    elif key in format_groups['us']:
        value_rep = '{:.0f}e-6'.format(value*1e6)
    ## List formats
    elif key in format_groups['list GHz rm0']:
        start = value[0]
        stop = value[1]
        npts = value[2]
        str_start = ''.join(['{:f}'.format(start*1e-9).rstrip('0'), 'e9'])
        str_stop = ''.join(['{:f}'.format(stop*1e-9).rstrip('0'), 'e9'])
        str_npts = '{:d}'.format(npts)
        value_rep = ''.join(['[', str_start, ', ', str_stop, ', ', str_npts, ']'])
    elif key in format_groups['list MHz int']:
        start = value[0]
        stop = value[1]
        npts = value[2]
        str_start = ''.join(['{:.0f}'.format(start*1e-6), 'e6'])
        str_stop = ''.join(['{:.0f}'.format(stop*1e-6), 'e6'])
        str_npts = '{:d}'.format(npts)
        value_rep = ''.join(['[', str_start, ', ', str_stop, ', ', str_npts, ']'])
    elif key in format_groups['list .3']:
        start = value[0]
        stop = value[1]
        npts = value[2]
        str_start = '{:.3f}'.format(start)
        str_stop = '{:.3f}'.format(stop)
        str_npts = '{:d}'.format(npts)
        value_rep = ''.join(['[', str_start, ', ', str_stop, ', ', str_npts, ']'])
    elif key in format_groups['list ns']:
        start = value[0]
        stop = value[1]
        npts = value[2]
        str_start = '{:.0f}e-9'.format(start*1e9)
        str_stop = '{:.0f}e-9'.format(stop*1e9)
        str_npts = '{:d}'.format(npts)
        value_rep = ''.join(['[', str_start, ', ', str_stop, ', ', str_npts, ']'])
    ## Dict formats
    elif key in format_groups['dict ns:.6']:
        value_rep = '{'
        for inner_key, inner_value in value.items():
            key_string = '{:.0f}e-9'.format(inner_key*1e9)
            value_string = '{:.6f}'.format(inner_value)
            value_rep += key_string+': '+value_string+', '
        value_rep += '}'
    elif key in format_groups['dict ns:1.2']:
        value_rep = '{'
        for inner_key, inner_value in value.items():
            key_string = '{:.0f}e-9'.format(inner_key*1e9)
            value_string = '{:1.3f}'.format(inner_value)
            value_rep += key_string+': '+value_string+', '
        value_rep += '}'
    ## new formats go here...
    else:
        # print(key, 'is not a special class')
        value_rep = str(value)
    return value_rep

##############################################################################
## Labber Data folder structure

def split_labber_data_dir(original_dir):
    head, Data_MMDD_folder = os.path.split(original_dir)
    head, MM_folder = os.path.split(head)
    head, YYYY_folder = os.path.split(head)
    return head, YYYY_folder, MM_folder, Data_MMDD_folder

def update_labber_dates_dir(original_dir, time_obj = datetime.now()):
    ## Separate path into parts
    head, old_year_folder, old_month_folder, old_Data_folder = split_labber_data_dir(original_dir.rstrip('/'))
    ## Create updated year folder
    year_folder = '{:%Y}'.format(time_obj)
    ## Create updated month folder
    month_folder = '{:%m}'.format(time_obj)
    ## Create updated Data_MMDD folder
    Data_folder = 'Data_{:%m%d}'.format(time_obj)
    return pathlib.Path(head, year_folder, month_folder, Data_folder)

def increment_filename(fname_in):
    '''
    Re-implementation of the PSICT-UIF filename incrementation procedure.
    '''
    ## Split the file name into a head and sequential id
    fname_split = re.split(r'(\d+$)', fname_in)    # split by int searching from back
    if len(fname_split) < 2:                         # could not split properly
        raise RuntimeError("Could not identify sequential ID in filename:", fname_in)
    fname_head = fname_split[0]
    fname_id = fname_split[1]
    ## Increment the id
    new_id = increment_string(fname_id)
    ## Put path back together
    new_fname = "".join([fname_head, new_id])
    return new_fname

def increment_string(str_in):
    '''
    Increment a string, preserving leading zeros.

    eg "00567" -> "00568"
    '''
    return str(int(str_in)+1).zfill(len(str_in))

##############################################################################
## User interaction for hardware changes

def get_user_confirmation(message, MAX_ATTEMPTS = 5):
    '''
    Wait for a response from the user; use to hold off experiments until hardware changes have been carried out.
    '''
    n_attempts = 0
    positive_response = False

    while n_attempts < MAX_ATTEMPTS:
        ## Print and ask for input
        print(message)
        user_response = input('Confirm? ({:d}/{:d}) [y/N] '.format(n_attempts+1, MAX_ATTEMPTS))
        if user_response == '' or not user_response.lower()[0] == 'y':
            print('Response negative; please try again.')
        else:
            print('Positive response received; continuing...')
            positive_response = True
            break
        ## Increment to prevent infinite loops
        n_attempts += 1

    ## Raise error if number of attempts has run out
    if not positive_response:
        raise RuntimeError('Maximum number of confirmation attempts exceeded; stopping execution.')

##############################################################################

def scan_worker_blocks(worker_file):
    '''
    Scan the worker file and return the blocks corresponding to its different parts.
    '''
    ## re matches for options dicts
    re_match_pulse_sequence = re.compile('pulse_sequence ?= ?')
    re_match_PSICT_options = re.compile('worker_PSICT_options ?= ?')
    re_match_general_options = re.compile('worker_general_options ?= ?')
    re_match_pulse_sequence_options = re.compile('worker_pulse_sequence_options ?= ?')
    re_match_script_copy_breakpoint = re.compile(SCRIPT_COPY_BREAKPOINT)

    ## Prepare empty lists
    header_block = []
    PSICT_options_block = []
    general_options_block = []
    pulse_sequence_options_block = []
    end_block = []

    with open(worker_file, 'r') as worker:
        line = worker.readline()
        ## Read up to 'pulse_sequence = ...'
        while not re_match_pulse_sequence.match(line):
            header_block.append(line)
            line = worker.readline()
        ## Skip actual 'pulse_sequence = ...' line
        line = worker.readline()
        ## Read up to worker_PSICT_options
        while not re_match_PSICT_options.match(line):
            line = worker.readline()
        ## Read up to worker_general_options and add to PSICT_options_block
        while not re_match_general_options.match(line):
            PSICT_options_block.append(line)
            line = worker.readline()
        ## Read up to worker_pulse_sequence_options and add to general_options_block
        while not re_match_pulse_sequence_options.match(line):
            general_options_block.append(line)
            line = worker.readline()
        ## Read up to script copy breakpoint and add to pulse_sequence_options_block
        while not re_match_script_copy_breakpoint.match(line):
            pulse_sequence_options_block.append(line)
            line = worker.readline()
        ## Read the rest of the file and add to end_block
        end_block = worker.readlines()

    return header_block, PSICT_options_block, general_options_block, pulse_sequence_options_block, end_block

##############################################################################
##############################################################################

class WorkerScriptManager:

    def __init__(self, worker_script, PSICT_config):
        ## Load config (log after logger initialized)
        self.set_PSICT_config(PSICT_config)
        ## Logging
        self.init_logging()
        ## Log config loading for debugging
        self.logger.log(LogLevels.VERBOSE, 'Config file loaded from path: {}'.format(self.PSICT_config_path))
        ## Set up flags
        self._iscopied_master = False
        ## Get file details for master script copying
        self._master_wd = os.getcwd()
        self._master_inv = sys.argv[0]
        self._master_target_dir = None
        ## Create block placeholders to enable dict setters to function correctly
        self.PSICT_options_block = []
        self.general_options_block = []
        self.pulse_sequence_options_block = []
        ## Set worker script path
        self._worker_path = worker_script
        self.refresh_worker()

    def set_PSICT_config(self, PSICT_config_path):
        self.PSICT_config_path = PSICT_config_path
        ## Import config file as module
        config_spec = importlib.util.spec_from_file_location('', self.PSICT_config_path)
        self._PSICT_config = importlib.util.module_from_spec(config_spec)
        config_spec.loader.exec_module(self._PSICT_config)

    #############################################################################
    ## Logging

    def init_logging(self):
        '''
        Initialize logging for the WorkerScriptManager.
        '''
        ## Add extra logging levels
        logging.addLevelName(LogLevels.ALL, 'ALL')
        logging.addLevelName(LogLevels.TRACE, 'TRACE')
        logging.addLevelName(LogLevels.VERBOSE, 'VERBOSE')
        logging.addLevelName(LogLevels.SPECIAL, 'SPECIAL')
        ## Init logger
        logger_name = 'WSMgr'
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(LogLevels.ALL) # Log all possible events
        ## Add handlers if there are none already added - code copied from psictUIFInterface module
        if len(self.logger.handlers) == 0:
            ## Console stream handler
            if self._PSICT_config.logging_config['console_log_enabled']:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(self._PSICT_config.logging_config['console_log_level'])
                console_fmt = logging.Formatter(self._PSICT_config.logging_config['console_fmt'], \
                                                datefmt = self._PSICT_config.logging_config['console_datefmt'])
                console_handler.setFormatter(console_fmt)
                ## Add handler to logger
                self.logger.addHandler(console_handler)
            ## File handler
            if self._PSICT_config.logging_config['file_log_enabled']:
                log_dir = self._PSICT_config.logging_config['log_dir']
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                log_file = self._PSICT_config.logging_config['log_file'].format(datetime.now())+'.log'
                log_path = os.path.join(log_dir, log_file)
                file_handler = logging.FileHandler(log_path)
                file_handler.setLevel(self._PSICT_config.logging_config['file_log_level'])
                file_fmt = logging.Formatter(self._PSICT_config.logging_config['file_fmt'], \
                                                datefmt = self._PSICT_config.logging_config['file_datefmt'])
                file_handler.setFormatter(file_fmt)
                ## Add handler to logger
                self.logger.addHandler(file_handler)
        ## Add NullHandler if no other handlers are configured
        if len(self.logger.handlers) == 0:
            self.logger.addHandler(logging.NullHandler())
        ## Status message
        self.logger.debug('Logging initialization complete.')

    def log(self, msg, loglevel = 'special', *args, **kwargs):
        '''
        Log a message to the logger at the specified level.

        This method should be used instead of bare `print` functions in scripts at the master level. This method should NOT be used internally within the WorkerScriptManager or related classes.

        Log levels can be specified as an integer (the usual way), but can also be string corresponding to the name of the level. Available options are: TRACE, DEBUG, VERBOSE, INFO, SPECIAL, WARNING, ERROR, CRITICAL. Specifying an unsupported string will result in a logged ERROR-level message, but no execution error.
        '''
        if isinstance(loglevel, str):
            ## Convert to lowercase
            loglevel = loglevel.lower()
            ## Convert string to appropriate level
            if loglevel == 'trace':
                lvl = LogLevels.TRACE
            elif loglevel == 'debug':
                lvl = LogLevels.DEBUG
            elif loglevel == 'verbose':
                lvl = LogLevels.VERBOSE
            elif loglevel == 'info':
                lvl = LogLevels.INFO
            elif loglevel == 'special':
                lvl = LogLevels.SPECIAL
            elif loglevel == 'warning':
                lvl = LogLevels.WARNING
            elif loglevel == 'error':
                lvl = LogLevels.ERROR
            elif LogLevel == 'critical':
                lvl = LogLevels.CRITICAL
            else:
                self.logger.error('Invalid loglevel string specified in call to log(): {}'.format(loglevel))
                return
        else: # loglevel is assumed to be numeric
            lvl = loglevel
        ## Log message
        self.logger.log(lvl, msg, *args, **kwargs)

    #############################################################################
    ## Working with parameter dicts and text blocks

    @property
    def PSICT_options(self):
        return self._PSICT_options
    @PSICT_options.setter
    def PSICT_options(self, new_PSICT_options):
        ## Update stored parameter dict
        self._PSICT_options = new_PSICT_options
        ## Update stored block
        self.update_block(self.PSICT_options_block, self._PSICT_options)

    @property
    def general_options(self):
        return self._general_options
    @general_options.setter
    def general_options(self, new_general_options):
        ## Update stored parameter dict
        self._general_options = new_general_options
        ## Update stored block
        self.update_block(self.general_options_block, self._general_options)

    @property
    def pulse_sequence_options(self):
        return self._pulse_sequence_options
    @pulse_sequence_options.setter
    def pulse_sequence_options(self, new_pulse_sequence_options):
        ## Update stored parameter dict
        self._pulse_sequence_options = new_pulse_sequence_options
        ## Update stored block
        self.update_block(self.pulse_sequence_options_block, self._pulse_sequence_options, nested_dicts = True)

    def refresh_worker(self):
        '''
        Mount the worker and pull values from it.
        '''
        self.logger.debug('Refreshing worker...')
        self.mount_worker()
        self.pull_from_worker()

    def mount_worker(self):
        '''
        (Re)-import/'mount' the worker script.
        '''
        ## Invalidate caches as well, just in case
        importlib.invalidate_caches()
        ## Wait 1 second before mounting the worker - avoids blocking reload of module
        time.sleep(1)
        ## Import worker script as module
        worker_spec = importlib.util.spec_from_file_location('', self._worker_path)
        self._worker_script = importlib.util.module_from_spec(worker_spec)
        worker_spec.loader.exec_module(self._worker_script)
        ## Status message
        self.logger.debug('Worker file mounted as module.')

    def pull_from_worker(self):
        '''
        Pull option values from the worker script.
        '''
        self.logger.log(LogLevels.TRACE, 'Pulling options dicts from worker...')
        ## Scan blocks from worker - done first to avoid no-matches when updating options dicts
        scanned_blocks = scan_worker_blocks(self._worker_path)
        ## Allocate worker blocks to specific attributes
        self.header_block = scanned_blocks[0]
        self.PSICT_options_block = scanned_blocks[1]
        self.general_options_block = scanned_blocks[2]
        self.pulse_sequence_options_block = scanned_blocks[3]
        self.end_block = scanned_blocks[4]
        ## Import options dicts from worker script
        self.PSICT_options = self._worker_script.worker_PSICT_options
        self.general_options =  self._worker_script.worker_general_options
        self.pulse_sequence_options = self._worker_script.worker_pulse_sequence_options
        ## Status message
        self.logger.debug('Pulled options dicts from worker.')

    def get_parameters(self):
        '''
        Convenience method for returning all three options dicts
        '''
        return self.PSICT_options, self.general_options, self.pulse_sequence_options

    def set_parameters(self, new_PSICT_options, new_general_options, new_pulse_sequence_options):
        '''
        Set stored parameter dicts (and blocks).
        '''
        self.logger.log(LogLevels.VERBOSE, 'Setting parameters...')
        ## Update stored dicts and blocks
        self.PSICT_options = new_PSICT_options
        self.general_options = new_general_options
        self.pulse_sequence_options = new_pulse_sequence_options

    def update_parameters(self):
        '''
        Update script based on stored parameters, and then refresh stored parameters from script.
        '''
        self.logger.log(LogLevels.VERBOSE, 'Cycling parameters through worker...')
        ## Push to worker
        self.update_script(copy = False)
        ## Refresh worker and pull
        self.refresh_worker()

    def update_block(self, block, options_dict = {}, nested_dicts = False):
        if nested_dicts:
            for outer_key, nested_dict in options_dict.items():
                ## Define top-level match object (pulse sequence name)
                re_outer_match = re.compile('\t*[\"\']'+str(outer_key)+'[\'\"]:')
                ## Iterate over keys in the sub-dict
                for inner_key, inner_value in nested_dict.items():
                    ## Define inner match object
                    re_inner_match = re.compile('\t*[\"\']'+str(inner_key)+'[\"\'] ?: ?')
                    ## Find sub-block by top-level match
                    outer_key_found = False
                    inner_key_found = False
                    for line_index, line in enumerate(block):
                        if outer_key_found:
                            ## Check for inner match
                            match_obj = re_inner_match.match(line)
                            if match_obj:
                                self.logger.log(LogLevels.TRACE, 'Key {} matches line at index {}'.format(inner_key, line_index))
                                ## Get specific formatting
                                value_rep = get_formatted_rep(inner_key, inner_value)
                                ## Replace line in block
                                block[line_index] = ''.join([match_obj.group(), value_rep, ','])
                                ## Stop searching for key
                                inner_key_found = True
                                break
                        else:
                            ## Check for outer match
                            if re_outer_match.match(line):
                                outer_key_found = True
                                self.logger.log(LogLevels.TRACE, 'Outer key {} matches line at index {}'.format(outer_key, line_index))
                                continue
                    ## End looping over lines
                    if not inner_key_found:
                        self.logger.warning('Match not found for key: {}'.format(inner_key))
        else:
            ## Iterate over options_dict keys
            for key, value in options_dict.items():
                ## Generate re match object
                re_match = re.compile('\t*[\"\']'+str(key)+'[\"\'] ?: ?')
                ## Attempt to find a match in the block
                key_found = False
                for line_index, line in enumerate(block):
                    match_obj = re_match.match(line)
                    if match_obj:
                        self.logger.log(LogLevels.TRACE, 'Key {} matches line at index {}'.format(key, line_index))
                        ## Get specific formatting
                        value_rep = get_formatted_rep(key, value)
                        ## Replace line in block
                        block[line_index] = "".join([match_obj.group(), value_rep, ','])
                        ## Stop searching for key
                        key_found = True
                        break
                ## End looping over lines
                if not key_found:
                    self.logger.warning('Match not found for key: {}'.format(key))
        return block

    #############################################################################
    ## Writing text blocks to new worker file

    def write_block(self, stream, block):
        for line in block:
            stream.write(line.strip('\n')+'\n')

    def write_new_script(self, new_script_path):
        with open(new_script_path, 'w') as new_script:
            self.write_block(new_script, self.header_block)
            new_script.write('pulse_sequence = \''+self._pulse_sequence_name+'\'\n\n')
            self.write_block(new_script, self.PSICT_options_block)
            self.write_block(new_script, self.general_options_block)
            self.write_block(new_script, self.pulse_sequence_options_block)
            new_script.write(SCRIPT_COPY_BREAKPOINT+'\n')
            self.write_block(new_script, self.end_block)

    #############################################################################
    ## Update the script (ie write and copy)

    def set_script_copy_target_dir(self, script_copy_target_dir):
        self.target_dir = script_copy_target_dir

    def set_master_copy_target_dir(self, master_copy_target_dir):
        self._master_target_dir = master_copy_target_dir

    def update_script(self, copy = False, target_filename = None, output_path = None):
        '''
        Docstring
        '''
        ## Status message
        self.logger.debug('Updating worker script; copy option is {}'.format(copy))

        ## Update the original worker script file
        self.write_new_script(self._worker_path)

        if copy:
            ## Get a target filename from either the given filename or path
            if target_filename is not None:
                self.target_file = target_filename
            elif output_path is not None:
                self.target_file = ''.join([os.path.splitext(os.path.basename(output_path))[0], self._PSICT_config.script_copy_postfix, '.py'])
            else:
                raise RuntimeError('The target must be specified through either a filename or a path.')

            ## Generate the full script target path
            self.target_path = os.path.join(self.target_dir, self.target_file)

            ## Create target directory if it does not exist
            if not os.path.exists(self.target_dir):
                os.makedirs(self.target_dir)

            ## Copy worker script to target path
            shutil.copy(self._worker_path, self.target_path)
            # shutil.copy('worker_new.py', self.target_path)

    #############################################################################
    ## Run measurement & do associated admin

    def run_measurement(self, pulse_sequence_name):
        '''
        Docstring.
        '''
        ## Status message
        self.logger.info('Running measurement at master: {}'.format(pulse_sequence_name))

        ## Update pulse sequence name attribute
        self._pulse_sequence_name = pulse_sequence_name

        ## Update parent logger name for worker script
        PSICT_options = self.PSICT_options
        PSICT_options['parent_logger_name'] = self.logger.name
        self.PSICT_options = PSICT_options

        ## Update parameters: stored -> script -> stored
        self.update_parameters()

        ## Execute measurement function
        self.output_path =  self._worker_script.run_pulse_sequence(self._pulse_sequence_name, \
                    self.PSICT_options, self.general_options,  \
                    self.pulse_sequence_options)
        ## Get output filename and dir
        self.output_filename = os.path.splitext(os.path.basename(self.output_path))[0]
        self.output_dir = os.path.dirname(os.path.abspath(self.output_path))
        # ## Log if required
        # if self._logging:
        # 	self._output_logger.add_entry(self.output_filename, self.output_dir, self._pulse_sequence_name)
        ## Copy master script if required
        if not self._iscopied_master:
            self.copy_master(self._master_target_dir)
        ## Update script (with copy)
        self.update_script(copy = True, output_path = self.output_path)
        ## Increment filename in preparation for next measurement
        self.PSICT_options['output_file'] = increment_filename(self.output_filename)
        ## Set parameters
        self.set_parameters(self.PSICT_options, self.general_options, self.pulse_sequence_options)
        ## Update script (incremented filename), with no copy
        self.update_parameters()

        ## Status message
        self.logger.info('Running measurement completed at master.')

    def update_date(self):
        ## Update output dir based on today's date
        self.PSICT_options['output_dir'] = update_labber_dates_dir(self._PSICT_options['output_dir'])

    def copy_master(self, master_dir_target = None):
        '''
        Copy the master script to the script_copy_target_dir
        '''
        ## Use script_copy_target_dir if no alternative is provided
        if master_dir_target is None:
            master_dir_target = self.target_dir
        ## Create target dir if it does not exist
        pathlib.Path(master_dir_target).mkdir(parents = True, exist_ok = True)
        ## Get full path to master file
        master_path_original = os.path.join(self._master_wd, self._master_inv)
        ## Construct filename for target
        master_file_target = ''.join([self.output_filename, '_master.py'])
        ## Construct full path for target
        master_path_target = os.path.join(master_dir_target, master_file_target)
        ## Copy master file
        self._master_path_new = shutil.copy(master_path_original, master_path_target)
        self.logger.log(LogLevels.SPECIAL, 'Master script copied to: {:s}'.format(self._master_path_new))
        ## Set flag
        self._iscopied_master = True

##
