## The PSICT-UIF top-level interface class
##  In the course of normal scripting, this should be the only object
##  the the user directly interfaces with in the external script.

import os
import sys
import importlib.util
from pathlib import Path
import logging
from datetime import datetime

from PSICT_UIF._include36.FileManager import FileManager
from PSICT_UIF._include36.PulseSeqManager import PulseSeqManager
from PSICT_UIF._include36.LabberExporter import LabberExporter
import PSICT_UIF._include36._LogLevels as LogLevels

class psictUIFInterface:
    '''
    The main PSICT pulse-sequence generator class

    This class handles all interfaces with the Labber reference files and Labber measurements, so that (in principle) everything can be controlled from a self-contained external script. This includes control over input and output database/reference files, creation of the pulse sequence, and control over parameters for the Single-Qubit Pulse Generator (SQPG) as well as any other instruments on the Labber instrument server in all of point-value, iteration, and inter-channel relation modes.

    The Labber ScriptTools MeasurementObject instance can be accessed directly in the external script once both input and output files have been set for the psictUIFInterface object by accessing the "MeasurementObject" attribute.

    Some settings and attributes which may change with time are stored in the PSICT_config.py file. This must be loaded into the PSICT interface object using the load_config_file method. Prior to version 1.0.7.1, these parameters were stored in the script-rcfile.

    Since version 1.0.7.2, it is possible to specify the is_worker parameter on initialisation. This indicates to the PSICT interface that it is running as part of a more complex automation procedure, but more generally that the 'measurement' script invoking the PSICT interface directly is *not* the main script being executed. The intention is to alter some of the default behaviours of the PSICT interface object that are no longer appropriate in this context. At present, this setting effectively turns off the script copying mechanism (as it does not play well when what is executed as __main__ is not the 'measurement' script mentioned previously), which shifts the burden of copying the script onto the 'master' automation/controller script. As the default of the worker setting is False, this is fully backwards-compatible with scripts from previous versions.
    '''

    def __init__(self, config_path, *, is_worker = False, parent_logger_name = None):
        ## NB declare all attributes explicitly for __del__ to work correctly
        ## Load config (log after logger initialized)
        self.load_config_file(config_path)
        ## Logging
        self.init_logging(parent_logger_name)
        ## Log config loading for debugging
        self.logger.log(LogLevels.VERBOSE, 'Config file loaded from path: {}'.format(self.script_rcpath))
        ## Save original working directory from which external script was invoked from
        self._original_wd = os.getcwd()
        self._script_inv = sys.argv[0]
        ## Add attributes
        self.is_SQPG_used = False
        ## Add constituent objects
        self.fileManager = FileManager(parent_logger_name = self.logger.name)
        self.pulseSeqManager = PulseSeqManager(parent_logger_name = self.logger.name)
        self.labberExporter = LabberExporter(parent_logger_name = self.logger.name)
        ## Add attributes for constituent objects
        self.fileManager.set_original_wd(self._original_wd, self._script_inv)
        ## Assign config to delegates
        self.assign_config_to_delegates()
        ## Set worker status as standalone script by default
        self.set_worker_status(is_worker)
        ## Status message
        self.logger.log(LogLevels.TRACE, 'psictUIFInterface instance initialized.')
        ##

    ## Direct access to MeasurementObject as attribute
    @property
    def MeasurementObject(self):
        return self.labberExporter.MeasurementObject

    def __del__(self):
        ## Delete object attributes
        del self.fileManager      # FileManager destructor deletes temp files
        del self.pulseSeqManager
        ## Change working directory back to original
        os.chdir(self._original_wd)
        ## Status message
        self.logger.log(LogLevels.TRACE, 'psictUIFInterface instance deleted.')
        ##

    ##########################################################################
    ## Logging

    def init_logging(self, parent_logger_name = None):
        '''
        Initialize logging for the psictUIFInterface.
        '''
        ## Add extra logging levels
        logging.addLevelName(LogLevels.ALL, 'ALL')
        logging.addLevelName(LogLevels.TRACE, 'TRACE')
        logging.addLevelName(LogLevels.VERBOSE, 'VERBOSE')
        logging.addLevelName(LogLevels.SPECIAL, 'SPECIAL')
        ## Init logger
        if parent_logger_name is not None:
            logger_name = '.'.join([parent_logger_name, 'psictUIFInterface'])
        else:
            logger_name = 'psictUIFInterface'
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(LogLevels.ALL) # Log all possible events
        ## Add handlers if there are none already added
        if len(self.logger.handlers) == 0:
            ## Console stream handler
            if self._script_rc.logging_config['console_log_enabled']:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(self._script_rc.logging_config['console_log_level'])
                console_fmt = logging.Formatter(self._script_rc.logging_config['console_fmt'], \
                                                datefmt = self._script_rc.logging_config['console_datefmt'])
                console_handler.setFormatter(console_fmt)
                ## Add handler to logger
                self.logger.addHandler(console_handler)
            ## File handler
            if self._script_rc.logging_config['file_log_enabled']:
                log_dir = self._script_rc.logging_config['log_dir']
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                log_file = self._script_rc.logging_config['log_file'].format(datetime.now())+'.log'
                log_path = os.path.join(log_dir, log_file)
                file_handler = logging.FileHandler(log_path)
                file_handler.setLevel(self._script_rc.logging_config['file_log_level'])
                file_fmt = logging.Formatter(self._script_rc.logging_config['file_fmt'], \
                                                datefmt = self._script_rc.logging_config['file_datefmt'])
                file_handler.setFormatter(file_fmt)
                ## Add handler to logger
                self.logger.addHandler(file_handler)
        ## Add NullHandler if no other handlers are configured
        if len(self.logger.handlers) == 0:
            self.logger.addHandler(logging.NullHandler())
        ## Status message
        self.logger.debug('Logging initialization complete.')

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## File and path management

    def set_worker_status(self, is_worker):
        '''
        Passes worker status to the FileManager object.
        '''
        self.fileManager.set_worker_status(is_worker)

    def load_config_file(self, config_path):
        '''
        Load the PSICT config file from the specified path.

        Prior to version 1.1.3.1, this method needed to be invoked explicitly in the external script.
        This is now changed in order to enable logging config to be imported from the config file,
        and log as much of the psictUIFInterface object creation as possible. Logging of the config
        file load process is now confirmed post-fact.

        The config_path provided should be an absolute path (behaviour is not guaranteed if it is relative).
        Prior to version 1.0.7.1, these configuration settings were stored in the script rc-file.
        '''
        ## Set config path
        self.script_rcpath = os.path.normpath(config_path)
        ## Import config file as module - preserve old names from rc-file
        config_spec = importlib.util.spec_from_file_location("", self.script_rcpath)
        self._script_rc = importlib.util.module_from_spec(config_spec)
        config_spec.loader.exec_module(self._script_rc)

    def assign_config_to_delegates(self):
        '''
        Assign the config path/module to the FileManager and PulseSeqManager objects

        Prior to version 1.1.3.1, this was done implicitly in the load_config_file method.
        '''
        self.fileManager.assign_script_rcmodule(self._script_rc, self.script_rcpath)
        self.pulseSeqManager.assign_script_rcmodule(self._script_rc, self.script_rcpath)
        self.logger.debug('Config path/module assigned to delegates.')

    def set_labber_exe_path(self, new_labber_exe_path):
        '''
        Change the stored (system default) Labber executable path to a custom path.

        Wraps the FileManager.set_labber_exe_path method.
        '''
        self.fileManager.set_labber_exe_path(new_labber_exe_path)

    def set_template_file(self, template_dir, template_file):
        '''
        Set the template hdf5 file.

        The "template" file is so named to differentiate it from the "reference" file, which can be modified by PSICT. The template file is guaranteed to be unmodified.

        Wraps the FileManager.set_template_file method.
        '''
        self.fileManager.set_template_file(template_dir, template_file)

    def set_output_file(self, output_dir, output_file):
        '''
        Set the output hdf5 file.

        Wraps the FileManager.set_output_file method.
        '''
        self.fileManager.set_output_file(output_dir, output_file)

    def set_script_copy_target_dir(self, script_copy_target_dir):
        '''
        Sets the target directory to which the script will be copied.

        Prior to version 1.0.7.1, this was specified in the script-rcfile.
        '''
        self.fileManager.set_script_copy_target_dir(script_copy_target_dir)

    def pre_measurement_copy(self):
        '''
        Copy all specified files (eg external script, script-rcfile) for reproducability.

        Wraps the FileManager.pre_measurement_copy method (the copy used to be carried out after the measurement; however, this interfered with editing of external scripts while the measurement was running).
        '''
        self.fileManager.pre_measurement_copy()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Labber MeasurementObject methods

    def init_MeasurementObject(self, *, auto_init = False):
        '''
        Explicitly initialise the Labber MeasurementObject, so that it can be interacted with directly in the external script.

        If this is not called, the MeasurementObject will be initialised during pre-measurement processing.
        '''
        ## Ensure that the appropriate paths are set
        self.logger.debug('Asserting reference and output paths exist...')
        assert self.fileManager.reference_path
        assert self.fileManager.output_path
        ## Initialise MeasurementObject
        self.labberExporter.init_MeasurementObject(self.fileManager.reference_path, self.fileManager.output_path, auto_init = auto_init)


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Instrument parameter setting methods

    def set_point_values(self, point_values_dict):
        '''
        Set instrument parameters as point (single) values.
        '''
        ## Status message
        self.logger.log(LogLevels.VERBOSE, 'Adding point values for instrument parameters...')
        ## Iterate through instrument specifications in the input dict, and divert the SQPG spec to the PulseSeqManager.
        for instrument_name, instrument_params in point_values_dict.items():
            if instrument_name == "SQPG":
                self.is_SQPG_used = True
                self.pulseSeqManager.set_input_pulse_seq(instrument_params)
            else:
                self.labberExporter.add_point_value_spec(instrument_name, instrument_params)
        ## Status message
        self.logger.debug("Instrument parameter point values added.")

    def set_api_client_values(self, api_client_values_dict, hardware_names, server_name = 'localhost'):
        '''
        Set values through the Labber API InstrumentClient object.

        In principle, this can be used for all point values, but is only strictly necessary for setting values as lists/arrays (presently, this is possible neither through the direct scripting API nor by direct HDF5 editing).
        '''
        ## Status message
        self.logger.debug('Adding API client values for instrument parameters...')
        ## Set server name in LabberExporter
        self.labberExporter.set_server_name(server_name)
        ## Iterate through instrument specifications, and pass to the LabberExporter
        for instrument_name in api_client_values_dict.keys():
            instrument_params = api_client_values_dict[instrument_name]
            hardware_name = hardware_names[instrument_name]
            self.labberExporter.add_client_value_spec(instrument_name, \
                                        instrument_params, hardware_name)
        ## Status message
        self.logger.debug('Instrument parameter API client values added.')

    def set_instr_config_values(self, instr_config_values_dict, hardware_names, server_name = 'localhost'):
        '''
        Set values by directly editing the reference hdf5 file's 'Instrument config' attributes.

        Note that this requires the 'hardware name' of the instrument (ie the full name of the driver), as well as the server name ('localhost' by default).
        '''
        ## Status message
        self.logger.debug('Adding HDF5 InstrumentConfig values for instrument parameters...')
        ## Set server name in LabberExporter
        self.labberExporter.set_server_name(server_name)
        ## Iterate through instruments and pass to LabberExporter
        for instrument_name in instr_config_values_dict.keys():
            instrument_params = instr_config_values_dict[instrument_name]
            hardware_name = hardware_names[instrument_name]
            self.labberExporter.add_instr_config_spec(instrument_name, instrument_params, \
                        hardware_name)
        ## Status message
        self.logger.debug('Instrument parameter HDF5 InstrumentConfig values added.')


    def set_iteration_values(self, iteration_values_dict, iteration_order_list):
        '''
        Set instrument parameters as (independent) iteration values.

        Iteration values are set as custom IterationSpec objects. They live within the same structure as the point values, and so overwrite any point values that were previously specified using the set_point_values method. As there is no simple way to implement general relationships amongst variables, all inter-pulse calculations carried out using IterationSpec objects will always take the maximal values in the iteration range.
        '''
        ## Status message
        self.logger.log(LogLevels.VERBOSE, "Adding iteration values for instrument parameters...")
        ## Iterate through instrument specifications in the input dict, and divert the SQPG spec to the PulseSeqManager
        for instrument_name, instrument_params in iteration_values_dict.items():
            if instrument_name == "SQPG":
                self.is_SQPG_used = True
                self.pulseSeqManager.set_iteration_spec(instrument_params)
            else:
                self.labberExporter.add_iteration_spec(instrument_name, instrument_params)
        ## Set iteration order
        self.labberExporter.set_iteration_order(iteration_order_list)
        ## Status message
        self.logger.debug("Instrument parameter iteration values added.")

    def set_channel_relations(self, channel_defs_dict, channel_relations_dict):
        '''
        Set the channel relations.

        Pulse names should be used to specify pulse parameters. In addition, the pulse parameters should be specified using their full names and *not* their shortcodes! (This may be changed/fixed in future versions).

        channel_defs_dict specifies the available channels, and their algebraic symbols used in the channel relation strings. channel_relations_dict specifies the actual relations.
        '''
        ## Status message
        self.logger.log(LogLevels.VERBOSE, "Adding channel relations...")
        ## Peel off SQPG specifications
        if "SQPG" in channel_defs_dict:
            self.is_SQPG_used = True
            SQPG_defs = channel_defs_dict["SQPG"]
            del channel_defs_dict["SQPG"]
            ## Set definitions
            self.pulseSeqManager.add_channel_defs(SQPG_defs)
        if "SQPG" in channel_relations_dict:
            self.is_SQPG_used = True
            SQPG_relations = channel_relations_dict["SQPG"]
            del channel_relations_dict["SQPG"]
            ## Set relations
            self.pulseSeqManager.add_channel_relations(SQPG_relations)
        ## Set channel definitions for generic instruments
        self.labberExporter.add_channel_defs(channel_defs_dict)
        ## Set channel relations for generic instruments
        self.labberExporter.set_channel_relations(channel_relations_dict)
        ## Status message
        self.logger.debug("Channel relations added.")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Measurement

    def perform_measurement(self, *, dry_run = False):
        '''
        Calls Labber to perform the measurement.

        Note that a final few pre-processing actions are taken before Labber is actually called:
        - The last-set user-specified Labber executable path is applied to the system
        - The Labber MeasurementObject is initialised (if this has not already occurred explicitly)
        - The pulse sequence is processed
        - All stored parameter values are actually applied to the Labber reference database file
        - When not in worker mode, the measurement script is copied to its target destination

        Following the pre-processing, Labber is called to carry out the measurement using the Labber MeasurementObject's performMeasurement() method.

        There are currently no post-measurement operations (beyond changing the working directory back to the original one, which is probably redundant anyway...)
        '''
        ## Status message
        self.logger.log(LogLevels.VERBOSE, "Carrying out measurement pre-processing...")
        ##### Measurement pre-processing
        ## Set ScriptTools executable path
        self.fileManager.apply_labber_exe_path()
        ## Initialise Labber MeasurementObject if not already done
        self.init_MeasurementObject(auto_init = True)
        ## Check if SPQG is being used
        if self.is_SQPG_used:
            ## Convert stored input pulse sequence to output pulse sequence
            self.pulseSeqManager.convert_seq()
            ## Transfer output pulse sequence and main SQPG params to LabberExporter
            self.labberExporter.add_point_value_spec("SQPG", self.pulseSeqManager.get_main_params())
            self.labberExporter.receive_pulse_sequence(self.pulseSeqManager.export_output())
            ## Transfer pulse sequence relations to LabberExporter
            self.labberExporter.receive_pulse_rels(*self.pulseSeqManager.export_relations())
        else:
            self.labberExporter.process_iteration_order()
        ## Apply all parameters stored in LabberExporter
        self.labberExporter.apply_all()
        ## Copy script - carried out before measurement to allow editing the script file while the measurement is running in Labber
        self.pre_measurement_copy()
        ## Status message
        self.logger.debug("Measurement pre-processing completed.")
        #### End measurement pre-processing
        ## Status message
        self.logger.log(LogLevels.SPECIAL, "Calling Labber to perform measurement...")
        ## Call Labber to perform measurement
        if self.MeasurementObject is not None:
            if dry_run:  # allows debugging w/o a Labber license
                self.logger.warning("Measurement dry run; skipping actual measurement...")
            else:        # actually perform measurement
                self.MeasurementObject.performMeasurement()
        else:
            raise RuntimeError("MeasurementObject has not been set!")
        ## Status message
        self.logger.log(LogLevels.SPECIAL, "Measurement completed.")
        ## Change working directory back to original - this is here so Dany will be happy (it also exists in the destructor, but that is not run until ipython exits!)
        os.chdir(self._original_wd)
        ## Final status message - this indicates the user can continue with other things!
        self.logger.info("Labber-PSICT execution finished.")


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
