## The PSICT-UIF top-level interface class
##  In the course of normal scripting, this should be the only object
##  the the user directly interfaces with in the external script.

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
        ## delete temporary files here (*before* deleting fileManager object!)
        ##
        ## delete object attributes
        del self.fileManager
        del self.pulseSeqManager
        ## debug message
        if self.verbose >= 4:
            print("Called psictUIFInterface destructor.")
        ##

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## File and path management

    def set_labber_exe_path(self, new_labber_exe_path, *, verbose = 0):
        '''
        Change the stored (system default) Labber executable path to a custom path (passed to the fileManager object).
        '''
        self.fileManager.set_labber_exe_path(new_labber_exe_path, verbose = verbose)


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


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
