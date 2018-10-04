## The PSICT-UIF top-level interface class
##  In the course of normal scripting, this should be the only object
##  the the user directly interfaces with in the external script.

import os
import sys
import importlib.util
from pathlib import Path

from PSICT_UIF._include36.FileManager import FileManager
from PSICT_UIF._include36.PulseSeqManager import PulseSeqManager
from PSICT_UIF._include36.LabberExporter import LabberExporter

class psictUIFInterface:
    '''
    The main PSICT pulse-sequence generator class

    This class handles all interfaces with the Labber reference files and Labber measurements, so that (in principle) everything can be controlled from a self-contained external script. This includes control over input and output database/reference files, creation of the pulse sequence, and control over parameters for the Single-Qubit Pulse Generator (SQPG) as well as any other instruments on the Labber instrument server in all of point-value, iteration, and inter-channel relation modes.

    The Labber ScriptTools MeasurementObject instance can be accessed directly in the external script once both input and output files have been set for the psictUIFInterface object by accessing the "MeasurementObject" attribute.

    All settings that are liable to change between experiments or even potentially across individual scripts are stored in the so-called "script-rcfile", which must be specified through the load_script_rcfile method.
    '''

    def __init__(self, *, is_slave = False, verbose = 1):
        ## NB declare all attributes explicitly for __del__ to work correctly
        ## Set object logging level
        self.verbose = verbose
        ## Save original working directory from which external script was invoked from
        self._original_wd = os.getcwd()
        self._script_inv = sys.argv[0]
        ## Add constituent objects
        self.fileManager = FileManager(verbose = self.verbose)
        self.pulseSeqManager = PulseSeqManager(verbose = self.verbose)
        self.labberExporter = LabberExporter(verbose = self.verbose)
        ## Add attributes for constituent objects
        self.fileManager.set_original_wd(self._original_wd, self._script_inv)
        ## Set slave status as standalone script by default
        self.set_slave_status(is_slave, verbose = self.verbose)
        ## Status message
        if self.verbose >= 4:
            print("Called psictUIFInterface constructor.")
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
        if self.verbose >= 4:
            print("Called psictUIFInterface destructor.")
        ##

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## File and path management

    def set_slave_status(self, is_slave, *, verbose = 1):
        '''
        Passes slave status to the FileManager object.
        '''
        self.fileManager.set_slave_status(is_slave, verbose = verbose)

    def load_script_rcfile(self, script_rcpath, *, verbose = 1):
        '''
        DEPRECATED. Set the script-rc file, imported as a module.

        If script_rc_copy_enabled is set to True in the script-rcfile, this file (the script-rcfile) will be copied alongside the external script. More options (such as matching the output file name) are available through the script-rcfile variables.
        '''
        raise DeprecationWarning('The script-rcfile is deprecated as of version 1.0.7.1')

    def load_config_file(self, config_path, *, verbose = 0):
        '''
        Load the PSICT config file from the specified path.

        The config_path provided must be an absolute path.
        Prior to version 1.0.7, these configuration settings were stored in the script rc-file.
        '''
        ## Status message
        if verbose > 2:
            print('Loading config file from path:', config_path)
        ## Set config path
        self.script_rcpath = os.path.normpath(config_path)
        ## Import config file as module - preserve old names from rc-file
        config_spec = importlib.util.spec_from_file_location("", self.script_rcpath)
        self._script_rc = importlib.util.module_from_spec(config_spec)
        config_spec.loader.exec_module(self._script_rc)
        ## Assign to delegates
        self.fileManager.assign_script_rcmodule(self._script_rc, self.script_rcpath)
        self.pulseSeqManager.assign_script_rcmodule(self._script_rc, self.script_rcpath)
        ## Status message
        if verbose >= 3:
            print('Config file loaded and assigned to delegates.')

    def set_labber_exe_path(self, new_labber_exe_path, *, verbose = 0):
        '''
        Change the stored (system default) Labber executable path to a custom path.

        Wraps the FileManager.set_labber_exe_path method.
        '''
        self.fileManager.set_labber_exe_path(new_labber_exe_path, verbose = verbose)

    def set_template_file(self, template_dir, template_file, *, verbose = 1):
        '''
        Set the template hdf5 file.

        The "template" file is so named to differentiate it from the "reference" file, which can be modified by PSICT. The template file is guaranteed to be unmodified.

        Wraps the FileManager.set_template_file method.
        '''
        self.fileManager.set_template_file(template_dir, template_file, verbose = verbose)

    def set_output_file(self, output_dir, output_file, *, verbose = 1):
        '''
        Set the output hdf5 file.

        Wraps the FileManager.set_output_file method.
        '''
        self.fileManager.set_output_file(output_dir, output_file, verbose = verbose)

    def set_script_copy_target_dir(self, script_copy_target_dir, *, verbose = 0):
        '''
        Sets the target directory to which the script will be copied.

        NB At present, this should be specified as an absolute path.
        Prior to version 1.0.7.1, this was specified in the script-rcfile.
        '''
        self.fileManager.set_script_copy_target_dir(script_copy_target_dir)

    def pre_measurement_copy(self, *, verbose = 1):
        '''
        Copy all specified files (eg external script, script-rcfile) for reproducability.

        Wraps the FileManager.post_measurement_copy method (the copy used to be carried out after the measurement; however, this interfered with editing of external scripts while the measurement was running).
        '''
        self.fileManager.post_measurement_copy(verbose = verbose)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Labber MeasurementObject methods

    def init_MeasurementObject(self, *, auto_init = False, verbose = 1):
        '''
        Explicitly initialise the Labber MeasurementObject, so that it can be interacted with directly in the external script.

        If this is not called, the MeasurementObject will be initialised during pre-measurement processing.
        '''
        ## Ensure that the appropriate paths are set
        assert self.fileManager.reference_path
        assert self.fileManager.output_path
        ## Initialise MeasurementObject
        self.labberExporter.init_MeasurementObject(self.fileManager.reference_path, self.fileManager.output_path, auto_init = auto_init, verbose = verbose)


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Instrument parameter setting methods

    def set_point_values(self, point_values_dict, *, verbose = 1):
        '''
        Set instrument parameters as point (single) values.
        '''
        ## Status message
        if verbose >= 1:
            print("Adding point values for instrument parameters...")
        ## Iterate through instrument specifications in the input dict, and divert the SQPG spec to the PulseSeqManager.
        for instrument_name, instrument_params in point_values_dict.items():
            if instrument_name == "SQPG":
                self.pulseSeqManager.set_input_pulse_seq(instrument_params, verbose = verbose)
            else:
                self.labberExporter.add_point_value_spec(instrument_name, instrument_params, verbose = verbose)
        ## Status message
        if verbose >= 1:
            print("Instrument parameter point values added.")

    def set_iteration_values(self, iteration_values_dict, iteration_order_list, *, verbose = 1):
        '''
        Set instrument parameters as (independent) iteration values.

        Iteration values are set as custom IterationSpec objects. They live within the same structure as the point values, and so overwrite any point values that were previously specified using the set_point_values method. As there is no simple way to implement general relationships amongst variables, all inter-pulse calculations carried out using IterationSpec objects will always take the maximal values in the iteration range.
        '''
        ## Status message
        if verbose >= 2:
            print("Adding iteration values for instrument parameters...")
        ## Iterate through instrument specifications in the input dict, and divert the SQPG spec to the PulseSeqManager
        for instrument_name, instrument_params in iteration_values_dict.items():
            if instrument_name == "SQPG":
                self.pulseSeqManager.set_iteration_spec(instrument_params, verbose = verbose)
            else:
                self.labberExporter.add_iteration_spec(instrument_name, instrument_params, verbose = verbose)
        ## Set iteration order
        self.labberExporter.set_iteration_order(iteration_order_list)
        ## Status message
        if verbose >= 2:
            print("Instrument parameter iteration values added.")

    def set_channel_relations(self, channel_defs_dict, channel_relations_dict, *, verbose = 1):
        '''
        Set the channel relations.

        Pulse names should be used to specify pulse parameters. In addition, the pulse parameters should be specified using their full names and *not* their shortcodes! (This may be fixed in future versions).

        channel_defs_dict specifies the available channels, and their algebraic symbols used in the channel relation strings. channel_relations_dict specifies the actual relations.
        '''
        ## Status message
        if verbose >= 1:
            print("Adding channel relations...")
        ## Peel off SQPG specifications
        if "SQPG" in channel_defs_dict:
            SQPG_defs = channel_defs_dict["SQPG"]
            del channel_defs_dict["SQPG"]
            ## Set definitions
            self.pulseSeqManager.add_channel_defs(SQPG_defs, verbose = verbose)
        if "SQPG" in channel_relations_dict:
            SQPG_relations = channel_relations_dict["SQPG"]
            del channel_relations_dict["SQPG"]
            ## Set relations
            self.pulseSeqManager.add_channel_relations(SQPG_relations, verbose = verbose)
        ## Set channel definitions for generic instruments
        self.labberExporter.add_channel_defs(channel_defs_dict, verbose = verbose)
        ## Set channel relations for generic instruments
        self.labberExporter.set_channel_relations(channel_relations_dict, verbose = verbose)
        ## Status message
        if verbose >= 1:
            print("Channel relations added.")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Measurement

    def perform_measurement(self, *, dry_run = False, verbose = 1):
        '''
        Calls Labber to perform the measurement.

        Note that a final few pre-processing actions are taken before Labber is actually called:
        - The last-set user-specified Labber executable path is applied to the system
        - The Labber MeasurementObject is initialised (if this has not already occurred explicitly)
        - The pulse sequence is processed
        - All stored parameter values are actually applied to the Labber reference database file
        - Specified files (eg external script, script-rcfile) are copied to their target destinations

        There are currently no post-measurement operations (beyond changing the working directory back to the original one, which is probably redundant anyway...)
        '''
        ## Status message
        if verbose >= 2:
            print("Carrying out measurement pre-processing...")
        ##### Measurement pre-processing
        ## Set ScriptTools executable path
        self.fileManager.apply_labber_exe_path(verbose = verbose)
        ## Initialise Labber MeasurementObject if not already done
        self.init_MeasurementObject(auto_init = True, verbose = verbose)
        ## Convert stored input pulse sequence to output pulse sequence
        self.pulseSeqManager.convert_seq(verbose = verbose)
        ## Transfer output pulse sequence and main SQPG params to LabberExporter
        self.labberExporter.add_point_value_spec("SQPG", self.pulseSeqManager.get_main_params(verbose = verbose), verbose = verbose-1)
        self.labberExporter.receive_pulse_sequence(self.pulseSeqManager.export_output(verbose = verbose))
        ## Transfer pulse sequence relations to LabberExporter
        self.labberExporter.receive_pulse_rels(*self.pulseSeqManager.export_relations(verbose = verbose), verbose = verbose)
        ## Apply all parameters stored in LabberExporter
        self.labberExporter.apply_all(verbose = verbose)
        ## Copy script - carried out before measurement to allow editing the script file while the measurement is running in Labber
        self.pre_measurement_copy(verbose = verbose)
        ## Status message
        if verbose >= 2:
            print("Measurement pre-processing completed.")
        #### End measurement pre-processing
        ## Status message
        if verbose >= 1:
            print("Calling Labber to perform measurement...")
        ## Call Labber to perform measurement
        if self.MeasurementObject is not None:
            if dry_run:  # allows debugging w/o a Labber license
                if verbose >= 1:
                    print("Measurement dry run; skipping actual measurement...")
            else:        # actually perform measurement
                self.MeasurementObject.performMeasurement()
        else:
            raise RuntimeError("MeasurementObject has not been set!")
        ## Status message
        if verbose >= 1:
            print("Measurement completed.")
        # #### Post-measurement operations - commented out as a placeholder
        # if verbose >= 2:
        #     print("Carrying out post-measurement operations...")
        # ## Status message
        # if verbose >= 2:
        #     print("Post-measurement operations completed.")
        ## Change working directory back to original - this is here so Dany will be happy (it also exists in the destructor, but that is not run until ipython exits!)
        os.chdir(self._original_wd)
        ## Final status message - this indicates the user can continue with other things!
        if verbose >= 1:
            print("Labber-PSICT execution finished.")


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
