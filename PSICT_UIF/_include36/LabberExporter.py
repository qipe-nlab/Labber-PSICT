## PSICT-UIF LabberExporter class
##  Stores and prepares all parameter settings before sending them to the
##  Labber measurement program.

import h5py
import numpy as np

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
        self._iteration_order = [] # list specifying order of iteration quantities
        self._raw_channel_defs = {} # Raw channel definitions for relations
        self._channel_defs = {}      # Processed (final-format) channel definitions for relations
        self._channel_relations = {} # Actual channel relations
        ## Other attributes
        self._hdf5_sl_entry_dtype = None # Stores the dtype of the hdf5 step list entries (this can't be auto-generated for some reason...)
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
    ## Convenience methods

    def get_full_label(self, instrument_name, param_name, pulse_number = 0):
        '''
        Generate the full label of the channel from its components.
        '''
        if pulse_number == 0:
            ## Generic instrument, or SQPG main parameter
            full_label = " - ".join([instrument_name, param_name])
        else:
            ## SQPG pulse-specific parameter
            full_label = "".join([instrument_name, " - ", param_name, " #", str(pulse_number)])
        return full_label

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
        ## status message
        if verbose >= 2:
            print("Setting iteration order...")
        self._iteration_order = iteration_order_list

    ## Pulse-sequence-specific methods

    def process_iteration_order(self, *, verbose = 0):
        '''
        Carry out any processing operations required on the iteration order specification.

        Most importantly, converts the iteration order specifications into full channel names.
        '''
        ## status message
        if verbose >= 3:
            print("Processing iteration order specification...")
        ## Build full-channel names iteration order spec
        new_iteration_order = []
        for iter_item in self._iteration_order:
            instrument_name = iter_item[0]
            if instrument_name == "SQPG" and not iter_item == "main":
                pulse_name = iter_item[1][0]
                param_name = iter_item[1][1]
                ## Get pulse number corresponding to given name
                pulse_number = [pulse["pulse_number"] for pulse in self._pulse_sequence][0]
                ## Construct channel name
                channel_name = "".join([instrument_name, " - ", param_name, " #", str(pulse_number)])
            else:
                param_name = iter_item[1]
                channel_name = " - ".join([instrument_name, param_name])
            ## Populate new iteration order
            new_iteration_order.append(channel_name)
        ## Set as new iteration order
        self.set_iteration_order(new_iteration_order, verbose = verbose-1)
        ## status message
        if verbose >= 3:
            print("Iteration order specification processed.")


    def receive_pulse_sequence(self, exported_pulse_seq, *, verbose = 0):
        '''
        Docstring for receive_pulse_sequence
        '''
        ## debug message
        if verbose >= 1:
            print("LabberExporter receiving pulse sequence...")
        ## Receive pulse sequence
        self._pulse_sequence = exported_pulse_seq
        ## Update iteration order to final format
        self.process_iteration_order(verbose = verbose)
        ## debug message
        if verbose >= 1:
            print("Pulse sequence received.")

    def add_channel_defs(self, channel_def_dict, *, verbose = 0):
        '''
        Store the definitions of the channels which are available for use in relations.

        The stored format will be {<channel key>: <full channel name>}.
        '''
        ## status message
        if verbose >= 2:
            print("Setting channel definitions...")
        for instrument_name, instrument_defs in channel_def_dict.items():
            if instrument_name == "SQPG":
                for pulse_number, pulse_defs in instrument_defs.items():
                    for channel_key, param_name in pulse_defs.items():
                        channel_name = self.get_full_label(instrument_name, param_name, pulse_number)
                        ## Store in self._raw_channel_defs
                        self._raw_channel_defs[channel_key] = channel_name
            else: # generic instrument
                for channel_key, param_name in instrument_defs.items():
                    channel_name = self.get_full_label(instrument_name, param_name)
                    ## Store in self._raw_channel_defs
                    self._raw_channel_defs[channel_key] = channel_name
        ## status message
        if verbose >= 2:
            print("Setting channel definitions completed.")


    def set_channel_relations(self, channel_relations_dict, *, verbose = 0):
        '''
        Store the channel relations.

        The stored format will be {<full channel name>: [<relation string>, [<required key 1>, <required key 2>, ...]], ...}.
        '''
        ## status message
        if verbose >= 2:
            print("Setting generic channel relations...")
        ## Concatenate the instrument and parameter names to create the full channel name, and store the relation under that name
        for instrument_name, instrument_relations in channel_relations_dict.items():
            ## Go through each of the instrument relations
            for param_name, channel_relation in instrument_relations.items():
                channel_name = self.get_full_label(instrument_name, param_name)
                ## Set relation in container
                self._channel_relations[channel_name] = channel_relation
                if verbose >= 3:
                    print("Set channel relation for:", channel_name)

    def receive_pulse_rels(self, pulse_defs, pulse_rels, *, verbose = 0):
        '''
        Docstring
        '''
        ## status message
        if verbose >= 2:
            print("Receiving pulse definitions and relations...")
        ## Add channel definitions
        self.add_channel_defs(pulse_defs)
        ## status message
        if verbose >= 2:
            print("Setting SQPG channel relations...")
        ## Add channel relations
        all_pulse_rels = pulse_rels["SQPG"]
        for pulse_number, pulse_relations in all_pulse_rels.items():
            for param_name, channel_relation in pulse_relations.items():
                ## Construct full channel name
                channel_name = self.get_full_label("SQPG", param_name, pulse_number)
                self._channel_relations[channel_name] = channel_relation
                ## status message
                if verbose >= 3:
                    print("Set channel relation for:", channel_name)
        ## status message
        if verbose >= 2:
            print("Pulse definitions and relations received.")


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

    def swap_items_by_index(self, container, index_1, index_2):
        '''
        Swap two items (specified by index) in the given container.
        '''
        temp = container[index_1]
        container[index_1] = container[index_2]
        container[index_2] = temp

    def sort_iteration_order(self, *, verbose = 0):
        '''
        Docstring
        '''
        ## status message
        if verbose >= 2:
            print("Sorting iteration order...")
        ## Open reference config file and re-order iteration list
        with h5py.File(self.MeasurementObject.sCfgFileIn, 'r+') as config_file:
            for index_counter, channel_name in enumerate(self._iteration_order):
                ## Generate list of channels in the order they currently appear
                current_iter_order = [step_item[0] for step_item in config_file['Step list'].value]
                ## Get index of desired channel name in current order
                channel_index = current_iter_order.index(channel_name)
                ## Swap desired channel with that at index_counter
                self.swap_items_by_index(config_file['Step list'], index_counter, channel_index)
        ## status message
        if verbose >= 2:
            print("Iteration order sorted.")

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
        ## Sort iteration parameters
        self.sort_iteration_order(verbose = verbose)
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

    def process_channel_defs(self, *, verbose = 0):
        '''
        Convert the stored channel definitions to the format required for application to the hdf5 file.

        Note that this cannot be done during calling of the add_channel_defs method, as there is no guarantee that the MeasurementObject has been initialised at that stage.
        '''
        ## status message
        if verbose >= 2:
            print("Processing channel definitions...")
        ## Fetch step list entry dtype (if not already fetched)
        if self._hdf5_sl_entry_dtype is None:
            ## status message
            if verbose >= 3:
                print("Fetching step list entry dtype...")
            with h5py.File(self.MeasurementObject.sCfgFileIn, 'r') as config_file:
                for instrument_key in config_file['Step config']:
                    self._hdf5_sl_entry_dtype = np.dtype(config_file['Step config'][instrument_key]['Relation parameters'].dtype)
                    break # only need to fetch once
        ## Convert each of the stored definitions in self._raw_channel_defs to the appropriate format, and store in self._channel_defs
        for channel_key, channel_name in self._raw_channel_defs.items():
            self._channel_defs[channel_key] = np.array([(channel_key, channel_name, False)], dtype = self._hdf5_sl_entry_dtype)
        if verbose >= 1:
            print("Channel definitions processed.")

    def get_sl_index(self, label_string, *, verbose = 0):
        '''
        Gets the index of the entry matching label_string in the config file's 'Step list'.

        label_string should be a full channel name.
        '''
        ## status message
        if verbose >= 4:
            print("Fetching step list index for", label_string)
        ## Open file and extract existing step list
        with h5py.File(self.MeasurementObject.sCfgFileIn, 'r') as config_file:
            step_list = config_file['Step list'].value
        if verbose >= 5:
            print("Step list extracted.")
        ## Get index of element with matching label string
        step_list_labels = [labels['channel_name'] for labels in step_list]
        index = step_list_labels.index(label_string)
        if verbose >= 5:
            print("Step list index extracted.")
        return index

    def apply_equation_string(self, label_string, equation_string, *, verbose = 0):
        '''
        Apply the equation string for the given label_string specifying a full channel name.

        It is the user's responsibility to ensure that the correct channel keys are provided and referenced in the step config!
        '''
        ## status message
        if verbose >= 3:
            print("Applying equation string \"", equation_string, "\" for ", label_string, sep="")
        ## Get step list index of label string
        step_list_index =self.get_sl_index(label_string)
        ## Modify step list entry
        with h5py.File(self.MeasurementObject.sCfgFileIn, 'r+') as config_file:
            new_entry = config_file['Step list'][step_list_index]
            new_entry['equation'] = equation_string
            new_entry['use_relations'] = True
            new_entry['show_advanced'] = True
            config_file['Step list'][step_list_index] = new_entry
        ## status message
        if verbose >= 3:
            print("Equation string set for", label_string)

    def apply_step_config(self, label_string, required_channel_keys, *, verbose = 0):
        '''
        Apply the step config for a given label_string (describing a full channel name).

        This includes setting up the required_channel_keys from the stored processed channel key definitions.
        '''
        ## status message
        if verbose >= 4:
            print("Applying step config for", label_string)
        ## Build up new step config entry from channel keys
        new_sc_entries = np.concatenate([self._channel_defs[channel_key] for channel_key in required_channel_keys])
        ## Delete old step config entry and replace with new one
        with h5py.File(self.MeasurementObject.sCfgFileIn, 'r+') as config_file:
            try:
                del config_file['Step config'][label_string]['Relation parameters']
            except KeyError:
                pass
            config_file['Step config'][label_string].create_dataset('Relation parameters', data = new_sc_entries)
        ## status message
        if verbose >= 4:
            print("Step config entries applied for", label_string)

    def apply_relation(self, channel_name, channel_relation, *, verbose = 0):
        '''
        Apply a single channel relation to the hdf5 database file.
        '''
        ## status message
        if verbose >= 3:
            print("Applying relation for:", channel_name)
        ## Extract equation and required channel keys
        equation_string = channel_relation[0]
        required_channel_keys = channel_relation[1]
        # Apply equation string
        self.apply_equation_string(channel_name, equation_string, verbose = verbose)
        ## Set appropriate step config entries
        self.apply_step_config(channel_name, required_channel_keys, verbose = verbose)
        ## status message
        if verbose >= 3:
            print("Relation applied for:", channel_name)

    def apply_relations(self, *, verbose = 0):
        '''
        Apply all channel relations by directly editing the reference hdf5 file.
        '''
        ## status message
        if verbose >= 2:
            print("LabberExporter: Applying channel relations...")
        ## Process channel definitions
        self.process_channel_defs(verbose = verbose)
        ## Set relations for each item in the stored relations
        for channel_name, channel_relation in self._channel_relations.items():
            self.apply_relation(channel_name, channel_relation)



    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
