## The PSICT-UIF top-level interface class
##  In the course of normal scripting, this should be the only object
##  the the user directly interfaces with in the external script.

import os
import importlib.util
from pathlib import Path
import warnings

from Labber import ScriptTools

from PSICT_UIF._include36.FileManager import FileManager
from PSICT_UIF._include36.PulseSeqManager import PulseSeqManager

class psictUIFInterface:
    '''
    Docstring for psictUIFInterface.
    '''

    def __init__(self, *, verbose = 0):
        ## NB declare all attributes explicitly for __del__ to work correctly
        ## set logging level
        self.verbose = verbose
        ## change working directory to the enclosing folder of this script
        if verbose >= 4:
            print("Changing working directory...")
        os.chdir(Path(__file__).parents[2]) # trim to enclosing folder of PSICT_UIF
        if verbose >= 4:
            print("New working directory is", os.getcwd())
        ## Add constituent objects
        self.fileManager = FileManager(verbose = self.verbose)
        self.pulseSeqManager = PulseSeqManager(verbose = self.verbose)
        self.MeasurementObject = None # will be initialized later once file paths are known
        ## debug message
        if self.verbose >= 4:
            print("Called psictUIFInterface constructor.")
        ##

    def __del__(self):
        ## delete object attributes
        del self.fileManager      # FileManager destructor deletes temp files
        del self.pulseSeqManager
        ## debug message
        if self.verbose >= 4:
            print("Called psictUIFInterface destructor.")
        ##

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## File and path management

    def load_script_rcfile(self, script_rcpath, *, verbose = 0):
        '''
        Set the script-rc file, imported as a module.
        '''
        ## normalize path
        self.script_rcpath = os.path.abspath(os.path.expanduser(os.path.normpath(script_rcpath)))
        ## debug message
        if verbose >= 1:
            print("Reading from script rcfile:", self.script_rcpath)
        ## import script rcfile as module
        script_rc_spec = importlib.util.spec_from_file_location("", self.script_rcpath)
        self._script_rc = importlib.util.module_from_spec(script_rc_spec)
        script_rc_spec.loader.exec_module(self._script_rc)
        if verbose >= 2:
            print("Script rcfile imported.")
        ## assign script rcfile to FileManager
        self.fileManager.assign_script_rcmodule(self._script_rc, self.script_rcpath)

    def set_labber_exe_path(self, new_labber_exe_path, *, verbose = 0):
        '''
        Change the stored (system default) Labber executable path to a custom path (passed to the FileManager object).
        '''
        self.fileManager.set_labber_exe_path(new_labber_exe_path, verbose = verbose)

    def set_template_file(self, template_dir, template_file, *, verbose = 0):
        '''
        Set the template hdf5 file (passed to the FileManager object).
        '''
        self.fileManager.set_template_file(template_dir, template_file, verbose = verbose)

    def set_output_file(self, output_dir, output_file, *, verbose = 0):
        '''
        Set the output hdf5 file (passed to the FileManager object).
        '''
        self.fileManager.set_output_file(output_dir, output_file, verbose = verbose)

    def post_measurement_copy(self, *, verbose = 0):
        '''
        Wraps the FileManager.post_measurement_copy method with some additional pre-copy admin.

        This is specifically deciding on what, where, and whether or not to rename, based on the script rcfile.
        '''
        self.fileManager.post_measurement_copy(verbose = verbose)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Labber MeasurementObject methods

    def init_MeasurementObject(self, *, auto_init = False, verbose = 0):
        '''
        Explicitly initialise the Labber MeasurementObject, so that it can be interacted with directly in the external script.

        If this is not called, the MeasurementObject will be initialised during pre-measurement processing.
        '''
        ## debug message
        if verbose >= 1:
            print("Initialising MeasurementObject...")
        ## Check that the MeasurementObject has not already been initialised
        if self.MeasurementObject is not None:
            if not auto_init:
                ## This method has been called manually
                warnings.warn("Labber MeasurementObject has already been initialised!", RuntimeWarning)
                # RuntimeWarning("Labber MeasurementObject has already been initialised!")
            return
        else:
            ## Ensure reference and output files are set properly
            assert self.fileManager.reference_path
            assert self.fileManager.output_path
            ## Initialise MeasurementObject
            self.MeasurementObject = ScriptTools.MeasurementObject(\
                                        self.fileManager.reference_path,
                                        self.fileManager.output_path)
            ## debug message
            if verbose >= 1:
                print("MeasurementObject initialised.")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Instrument parameter setting methods

    def set_point_values(self, point_values_dict, *, verbose = 0):
        '''
        Set instrument parameters as point (single) values.
        '''
        ## debug message
        if verbose >= 1:
            print("Setting point values for instrument parameters...")
        ## Extract pulse sequence for SQPG instrument
        try:
            pulse_seq_dict = point_values_dict["SQPG"]
        except KeyError:
            raise RuntimeWarning("There were no point-value specifications for the pulse sequence!")
        else:
            self.pulseSeqManager.set_input_pulse_seq(pulse_seq_dict, verbose = verbose)
        ## TODO generic other instrument parameter setting here
        ## debug message
        if verbose >= 1:
            print("Set instrument parameters as point values.")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Measurement

    def perform_measurement(self, *, dry_run = False, verbose = 0):
        '''
        Calls Labber to perform the measurement.

        Note that a final few pre-processing actions are taken before Labber is actually called.
        '''
        ## debug message
        if verbose >= 1:
            print("Carrying out measurement pre-processing...")
        ##### measurement pre-processing
        ## set ScriptTools executable path
        self.fileManager.apply_labber_exe_path(verbose = verbose)
        ## Initialise Labber MeasurementObject if not already done
        self.init_MeasurementObject(auto_init = True, verbose = verbose)
        ## convert stored input pulse sequence to output pulse sequence
        self.pulseSeqManager.convert_seq(verbose = verbose)
        ####
        ## debug message
        if verbose >= 1:
            print("Measurement pre-processing completed.")
        if verbose >= 1:
            print("Calling Labber to perform measurement...")
        ## Call Labber to perform measurement
        if self.MeasurementObject is not None:
            if dry_run:  # check what would have been done
                if verbose >= 1:
                    print("Measurement dry run; skipping actual measurement...")
            else:        # actually perform measurement
                self.MeasurementObject.performMeasurement()
        else:
            ## Error: MeasurementObject not set!
            ## TODO Change this to an error once everything else is implemented.
            print("MeasurementObject is not set.")
        ## debug message
        if verbose >= 1:
            print("Measurement completed.")
        #### Post-measurement operations
        if verbose >= 1:
            print("Carrying out post-measurement operations...")
        ## Copy files (script, rcfile, etc) for reproducability
        self.post_measurement_copy(verbose = verbose)
        ## debug message
        if verbose >= 1:
            print("Post-measurement operations completed.")


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
