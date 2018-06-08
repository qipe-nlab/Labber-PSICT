## PSICT-UIF LabberExporter class
##  Stores and prepares all parameter settings before sending them to the
##  Labber measurement program.

from Labber import ScriptTools

import PSICT_UIF._include36._Pulse_rc as _Pulse_rc

class LabberExporter:
    '''
    Docstring for LabberExporter class.
    '''

    def __init__(self, *, verbose = 0):
        ## set object log level
        self.verbose = verbose
        ## Labber MeasurementObject - will be set later
        self.MeasurementObject = None
        ## Parameter containers
        self._point_values = {}
        self._pulse_sequence = {}
        ## debug message
        if verbose >= 4:
            print("LabberExporter constructor called.")

    def __del__(self):
        ## debug message
        if self.verbose >= 4:
            print("Calling LabberExporter destructor.")
        ## delete objects here...
        ## debug message
        if self.verbose >= 4:
            print("LabberExporter destructor finished.")


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Import instrument parameter specifications

    def add_point_value_spec(self, instrument_name, instrument_params, *, verbose = 0):
        '''
        Docstring.
        '''
        ## debug message
        if verbose >= 1:
            print("Importing point value specifications for", instrument_name)
        ## Import parameters
        self._point_values[instrument_name] = instrument_params


    ## Pulse-sequence-specific mathods
    def receive_pulse_sequence(self, exported_pulse_seq, *, verbose = 0):
        '''
        Docstring for receive_pulse_sequence
        '''
        ## debug message
        if verbose >= 1:
            print("LabberExporter receiving pulse sequence...")
        ## Receive pulse sequence
        self._pulse_sequence = exported_pulse_seq
        ## debug message
        if verbose >= 1:
            print("Pulse sequence received.")


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Labber MeasurementObject methods

    def init_MeasurementObject(self, reference_path, output_path, *, auto_init = False, verbose = 0):
        '''
        Docstring
        '''
        ## debug message
        if verbose >= 1:
            print("Initialising MeasurementObject...")
        ## Check that the MeasurementObject has not already been initialised
        if self.MeasurementObject is not None:
            if not auto_init:
                ## This method has been called manually
                warnings.warn("Labber MeasurementObject has already been initialised!", RuntimeWarning)
            return
        else:
            ## Initialise MeasurementObject
            self.MeasurementObject = ScriptTools.MeasurementObject(\
                                        reference_path,
                                        output_path)
            ## debug message
            if verbose >= 1:
                print("MeasurementObject initialised.")


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Application of instrument parameter specifications

    def apply_all(self, *, verbose = 0):
        '''
        Apply all stored parameters to the reference file, either through the Labber API or direct editing.
        '''
        ## debug message
        if verbose >= 1:
            print("Applying all instrument parameters from LabberExporter...")
        ## Apply different parameter sets
        self.apply_point_values(verbose = verbose)
        self.apply_iteration_values(verbose = verbose)
        self.apply_relations(verbose = verbose)
        ## debug message
        if verbose >= 1:
            print("Instrument parameters applied.")

    def apply_point_values(self, *, verbose = 0):
        '''
        Apply all stored point values (including for SQPG) through the Labber API.
        '''
        ## debug message
        if verbose >= 2:
            print("LabberExporter: Applying parameter point values...")
        ## Apply all non-pulse parameters (including main SQPG parameters)
        for instrument_name, instrument_params in self._point_values.items():
            for param_name, param_value in instrument_params.items():
                target_string = " - ".join([instrument_name, param_name])
                self.MeasurementObject.updateValue(\
                                        target_string, param_value, 'SINGLE')
                if verbose >= 4:
                    print("Point value updated: \"", target_string, "\" to ", param_value, sep="")
        ## Apply pulse parameters for SQPG
        for pulse in self._pulse_sequence:
            pulse_number = pulse.attributes["pulse_number"]
            for param_name in _Pulse_rc.FULL_NAMES_PULSES:
                try:
                    param_value = pulse.attributes[param_name]
                except KeyError:
                    continue
                else:
                    target_string = "".join([
                                            "SQPG - ", param_name, " #", str(pulse_number)])
                    self.MeasurementObject.updateValue(\
                                            target_string, param_value, 'SINGLE')
                    if verbose >= 4:
                        print("Point value updated: \"", target_string, "\" to ", param_value, sep="")
        ## debug message
        if verbose >= 2:
            print("LabberExporter: Parameter point values applied")

    def apply_iteration_values(self, *, verbose = 0):
        '''
        Apply all stored iteration values through the Labber API.
        '''
        if verbose >= 2:
            print("LabberExporter: Applying parameter iteration values...")

    def apply_relations(self, *, verbose = 0):
        '''
        Apply all channel relations by directly editing the reference hdf5 file.
        '''
        if verbose >= 2:
            print("LabberExporter: Applying channel relations...")



    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
