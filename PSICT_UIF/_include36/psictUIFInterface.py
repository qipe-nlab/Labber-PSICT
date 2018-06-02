## The PSICT-UIF top-level interface class
##  In the course of normal scripting, this should be the only object
##  the the user directly interfaces with in the external script.

import os
import importlib.util

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
        if verbose >= 2:
            print("Reading from script rcfile:", self.script_rcpath)
        ## import script rcfile as module, and assign as FileManager attribute
        script_rc_spec = importlib.util.spec_from_file_location("", self.script_rcpath)
        self._script_rc = importlib.util.module_from_spec(script_rc_spec)
        script_rc_spec.loader.exec_module(self._script_rc)
        if verbose >= 2:
            print("Script rcfile imported.")

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

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Pulse sequence operations

    def set_pulse_seq_params(self, *, verbose = 0):
        '''
        Set input parameters for the pulse sequence.

        These are the human-input parameters which will later be converted to a Labber-readable pulse sequence by the PulseSeqManager object.
        '''
        self.pulseSeqManager.set_input_pulse_seq(verbose = verbose)


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Measurement

    def perform_measurement(self, *, verbose = 0):
        '''
        Calls Labber to perform the measurement.

        Note that a final few pre-processing actions are taken before Labber is actually called.
        '''
        ## debug message
        if verbose >= 2:
            print("Carrying out measurement pre-processing...")
        ##### measurement pre-processing
        ## set ScriptTools executable path
        self.fileManager.apply_labber_exe_path(verbose = verbose)
        ## convert stored input pulse sequence to output pulse sequence
        self.pulseSeqManager.convert_seq(verbose = verbose)
        ####
        ## debug message
        if verbose >= 2:
            print("Measurement pre-processing completed.")
        if verbose >= 1:
            print("Calling Labber to perform measurement...")
        ## Call Labber to perform measurement
        if self.MeasurementObject is not None:
            self.MeasurementObject.performMeasurement()
        else:
            ## Error: MeasurementObject not set!
            ## TODO Change this to an error once everything else is implemented.
            print("MeasurementObject is not set.")
        ## debug message
        if verbose >= 1:
            print("Measurement completed.")
        if verbose >= 1:
            print("Carrying out post-measurement operations...")
        ## Copy script and associated files to target directory (set in script rcfile)
        if self._script_rc.script_copy_enabled:
            self.fileManager.post_measurement_copy(self._script_rc.script_copy_target_dir, verbose = verbose)
        ## debug message
        if verbose >= 1:
            print("Post-measurement operations completed.")


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
