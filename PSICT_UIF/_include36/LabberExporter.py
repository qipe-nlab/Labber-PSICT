## PSICT-UIF LabberExporter class
##  Stores and prepares all parameter settings before sending them to the
##  Labber measurement program.

from Labber import ScriptTools

import PSICT_UIF._include36._Pulse_rc as _Pulse_rc
from PSICT_UIF._include36.ParameterSpec import IterationSpec

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
        self._api_values = {}     # parameter values which will be set through the Labber API
        self._pulse_sequence = {} # parameter values specific to the pulse sequence (not including main SQPG parameters)
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
        self._api_values[instrument_name] = instrument_params

    def add_iteration_spec(self, instrument_name, instrument_params, *, verbose = 0):
        '''
        Docstring.
        '''
        ## debug message
        if verbose >= 1:
            print("Importing iteration specifications for:", instrument_name)
        ## Ensure instrument entry exists
        if not instrument_name in self._api_values:
            self._api_values[instrument_name] = {}
        ## Import parameters
        for param_name, iter_list in instrument_params.items():
            iter_obj = IterationSpec({"start_value": iter_list[0],
                                      "stop_value": iter_list[1],
                                      "n_pts": iter_list[2],
                                    })
            self._api_values[instrument_name][param_name] = iter_obj

    def set_iteration_order(self, iteration_order_list, *, verbose = 0):
        '''
        Docstring
        '''
        self._iteration_order = iteration_order_list

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
        self.apply_api_values(verbose = verbose)
        self.apply_relations(verbose = verbose)
        ## debug message
        if verbose >= 1:
            print("Instrument parameters applied.")

    def apply_api_values(self, *, verbose = 0):
        '''
        Apply all stored point values (including for SQPG) through the Labber API.
        '''
        ## debug message
        if verbose >= 2:
            print("LabberExporter: Applying parameter point values...")
        ## Apply all non-pulse parameters (including main SQPG parameters)
        for instrument_name, instrument_params in self._api_values.items():
            for param_name, param_value in instrument_params.items():
                target_string = " - ".join([instrument_name, param_name])
                self.update_api_value(target_string, param_value, verbose = verbose)
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
                    self.update_api_value(target_string, param_value, verbose = verbose)
        ## Status message
        if verbose >= 2:
            print("LabberExporter: Parameter point values applied")

    def update_api_value(self, target_string, param_value, *, verbose = 0):
        '''
        Update the value of an instrument parameter through the Labber API

        The specific parameter should be specified in full by the target_string. The type of the param_value will determine what is set: single -> single, IterationSpec -> iteration.
        '''
        ## Check type of param value
        if isinstance(param_value, IterationSpec):
            ## param_value is an IterationSpec object
            self.MeasurementObject.updateValue(target_string, param_value.start_value, 'START')
            self.MeasurementObject.updateValue(target_string, param_value.stop_value, 'STOP')
            self.MeasurementObject.updateValue(target_string, param_value.n_pts, 'N_PTS')
        else: # the parameter is a single value, either string or numeric
            self.MeasurementObject.updateValue(target_string, param_value, 'SINGLE')
        ## status message
        if verbose >= 2:
            print("Instrument value updated: \"", target_string, "\" to ", param_value, sep="")


    def apply_relations(self, *, verbose = 0):
        '''
        Apply all channel relations by directly editing the reference hdf5 file.
        '''
        if verbose >= 2:
            print("LabberExporter: Applying channel relations...")



    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
