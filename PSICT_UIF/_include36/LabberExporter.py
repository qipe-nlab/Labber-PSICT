## PSICT-UIF LabberExporter class
##  Stores and prepares all parameter settings before sending them to the
##  Labber measurement program.

import h5py
import numpy as np
import logging

from Labber import ScriptTools
import Labber

import PSICT_UIF._include36._Pulse_rc as _Pulse_rc
from PSICT_UIF._include36.ParameterSpec import IterationSpec
import PSICT_UIF._include36._LogLevels as LogLevels
from PSICT_UIF._include36._Common import extract_relation_variables

class LabberExporter:
    '''
    Stores and prepares all parameter settings before applying them to the measurement.

    The LabberExporter uses both the Labber ScriptTools API as well as direct editing of the reference hdf5 database file to accomplish this.

    Parameters should in general be passed to the LabberExporter in their "final form", ie with no further calculations to be carried out (note that the LabberExporter class does implement several methods to expand channel names in full etc.).
    '''

    def __init__(self, *, parent_logger_name = None):
        ## Logging
        if parent_logger_name is not None:
            logger_name = '.'.join([parent_logger_name, 'LabberExporter'])
        else:
            logger_name = 'LabberExporter'
        self.logger = logging.getLogger(logger_name)
        ## Labber MeasurementObject - will be set later
        self.MeasurementObject = None
        ## Set server name to 'localhost' as default
        self.set_server_name('localhost')
        ## Parameter containers
        self._api_values = {}     # parameter values which will be set through the Labber API
        self._client_values = {}  # parameter values which will be set through the InstrumentClient interface
        self._instr_config_values = {} # parameter values which will be set through direct editing of the hdf5 file Instrument Config attributes
        self._hardware_names = {} # 'hardware' names of instruments (ie full driver names)
        self._pulse_sequence = {} # parameter values specific to the pulse sequence (not including main SQPG parameters)
        self._iteration_order = [] # list specifying order of iteration quantities
        self._raw_channel_defs = {} # Raw channel definitions for relations
        self._channel_defs = {}      # Processed (final-format) channel definitions for relations
        self._channel_relations = {} # Actual channel relations
        ## Other attributes
        self._hdf5_sl_entry_dtype = None # Stores the dtype of the hdf5 step list entries (this can't be auto-generated for some reason...)
        ## Status message
        self.logger.log(LogLevels.TRACE, "Instance initialized.")

    def __del__(self):
        ## Delete objects here
        ## Status message
        self.logger.log(LogLevels.TRACE, "Instance deleted.")


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Misc methods

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

    def add_point_value_spec(self, instrument_name, instrument_params):
        '''
        Add point-value specifications, specified per-instrument.

        TODO: show sample dict structure here
        '''
        ## Status message
        self.logger.debug("Adding parameter specifications for {}...".format(instrument_name))
        ## Import parameters
        self._api_values[instrument_name] = instrument_params

    def set_server_name(self, server_name):
        '''
        Set the name/address of the InstrumentServer

        Used when connecting via the Labber InstrumentClient.
        '''
        self._InstrumentServer = server_name
        self.logger.log(LogLevels.VERBOSE, 'InstrumentServer set to: {}'.format(server_name))

    def add_client_value_spec(self, instrument_name, instrument_params, hardware_name):
        '''
        Add specifications that are to be set via the Labber InstrumentClient API.
        '''
        ## Status message
        self.logger.debug('Importing InstrumentClient specifications for: {}'.format(instrument_name))
        ## Import parameter values
        self._client_values[instrument_name] = instrument_params
        self._hardware_names[instrument_name] = hardware_name

    def add_instr_config_spec(self, instrument_name, instrument_params, hardware_name):
        '''
        Add specifications to be set via Instrument Config attributes in the reference HDF5 file.
        '''
        ## Status message
        self.logger.debug('Importing Instrument Config specifications for: {}'.format(instrument_name))
        ## Import parameter values
        self._instr_config_values[instrument_name] = instrument_params
        self._hardware_names[instrument_name] = hardware_name

    def add_iteration_spec(self, instrument_name, instrument_params):
        '''
        Add iteration specifications, specified per-instrument.

        TODO: show sample dict structure here
        '''
        ## Status message
        self.logger.debug("Importing iteration specifications for: {}".format(instrument_name))
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
            self.logger.debug("Set {} - {} to {}".format(instrument_name, \
                                                    param_name, iter_obj))

    def set_iteration_order(self, iteration_order_list):
        '''
        Set the order of iteration for iteration variables.

        If this is not specified, Labber will default to using the order in which they appear on the LHS in the measurement editor.
        '''
        ## Status message
        self.logger.debug("Setting iteration order...")
        self._iteration_order = iteration_order_list

    ## Pulse-sequence-specific methods

    def process_iteration_order(self):
        '''
        Carry out any processing operations required on the iteration order specification.

        Most importantly, converts the iteration order specifications into full channel names.
        '''
        ## status message
        self.logger.debug("Processing iteration order specification...")
        ## Build full-channel names iteration order spec
        new_iteration_order = []
        for iter_item in self._iteration_order:
            instrument_name = iter_item[0]
            if instrument_name == "SQPG" and iter_item[0] == "main":
                param_name = iter_item[1][1]
                ## Construct channel name
                channel_name = " - ".join([instrument_name, param_name])
            elif instrument_name == "SQPG":
                pulse_name = iter_item[1][0]
                param_name = iter_item[1][1]
                ## Get pulse number corresponding to given name
                pulse_number = [pulse["pulse_number"] for pulse in self._pulse_sequence if pulse.name == pulse_name][0]
                ## Construct channel name
                channel_name = "".join([instrument_name, " - ", param_name, " #", str(pulse_number)])
            else:
                param_name = iter_item[1]
                channel_name = " - ".join([instrument_name, param_name])
            ## Populate new iteration order
            new_iteration_order.append(channel_name)
        ## Set as new iteration order
        self.set_iteration_order(new_iteration_order)
        ## status message
        self.logger.debug("Iteration order specification processed.")


    def receive_pulse_sequence(self, exported_pulse_seq):
        '''
        Receive an exported pulse sequence (from a PulseSequence object) and store it.
        '''
        ## debug message
        self.logger.debug("LabberExporter receiving pulse sequence...")
        ## Receive pulse sequence
        self._pulse_sequence = exported_pulse_seq
        ## Update iteration order to final format
        self.process_iteration_order()
        ## debug message
        self.logger.debug("Pulse sequence received.")

    def add_channel_defs(self, channel_def_dict):
        '''
        Store the definitions of the channels which are available for use in relations.

        The stored format will be {<channel key>: <full channel name>}.
        '''
        ## status message
        self.logger.debug("Setting channel definitions...")
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
        self.logger.debug("Setting channel definitions completed.")


    def set_channel_relations(self, channel_relations_dict):
        '''
        Store the channel relations.

        The stored format will be {<full channel name>: [<relation string>, [<required key 1>, <required key 2>, ...]], ...}.
        '''
        ## status message
        self.logger.debug("Setting generic channel relations...")
        ## Concatenate the instrument and parameter names to create the full channel name, and store the relation under that name
        for instrument_name, instrument_relations in channel_relations_dict.items():
            ## Go through each of the instrument relations
            for param_name, channel_relation in instrument_relations.items():
                channel_name = self.get_full_label(instrument_name, param_name)
                ## Extract required variable names if not provided
                if isinstance(channel_relation, str):
                    self.logger.log(LogLevels.VERBOSE, 'Channel relation variables not provided for {}::{}'.format(instrument_name, param_name))
                    self.logger.log(LogLevels.VERBOSE, 'Relation equation string: \'{}\''.format(channel_relation))
                    variable_names = extract_relation_variables(channel_relation)
                    self.logger.log(LogLevels.VERBOSE, 'Variables extracted: {}'.format(variable_names))
                    channel_relation = [channel_relation, variable_names]
                else:
                    self.logger.log(LogLevels.VERBOSE, 'Channel relation variables provided for {}::{}'.format(instrument_name, param_name))
                ## Set relation in container
                self._channel_relations[channel_name] = channel_relation
                self.logger.debug("Set channel relation for: {}".format(channel_name))

    def receive_pulse_rels(self, pulse_defs, pulse_rels):
        '''
        Receive pulse relations (from a PulseSequence object) and store them.
        '''
        ## status message
        self.logger.debug("Receiving pulse definitions and relations...")
        ## Add channel definitions
        self.add_channel_defs(pulse_defs)
        ## status message
        self.logger.debug("Setting SQPG channel relations...")
        ## Add channel relations
        all_pulse_rels = pulse_rels["SQPG"]
        for pulse_number, pulse_relations in all_pulse_rels.items():
            for param_name, channel_relation in pulse_relations.items():
                ## Construct full channel name
                channel_name = self.get_full_label("SQPG", param_name, pulse_number)
                self._channel_relations[channel_name] = channel_relation
                ## status message
                self.logger.debug("Set channel relation for: {}".format(channel_name))
        ## status message
        self.logger.debug("Pulse definitions and relations received.")


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Labber MeasurementObject methods

    def init_MeasurementObject(self, reference_path, output_path, *, auto_init = False):
        '''
        Initialise a Labber MeasurementObject instance.

        For more information on the MeasurementObject, see the Labber API docs.
        '''
        ## debug message
        self.logger.log(LogLevels.VERBOSE, "Initialising MeasurementObject...")
        ## Check that the MeasurementObject has not already been initialised
        if self.MeasurementObject is not None:
            if not auto_init:
                ## This method has been called manually
                # warnings.warn("Labber MeasurementObject has already been initialised!", RuntimeWarning)
                self.logger.warning('Labber MeasurementObject has already been initialised!')
            return
        else:
            ## Initialise MeasurementObject
            self.MeasurementObject = ScriptTools.MeasurementObject(\
                                        reference_path,
                                        output_path)
            ## debug message
            self.logger.debug("MeasurementObject initialised.")


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Application of instrument parameter specifications

    def apply_all(self):
        '''
        Apply all stored parameters to the reference file, either through the Labber API or direct editing.
        '''
        ## Status message
        self.logger.log(LogLevels.VERBOSE, "Applying all instrument parameters from LabberExporter...")
        ## Apply different parameter sets
        self.apply_api_values()
        self.apply_client_values()
        self.apply_instr_config_values()
        self.apply_relations()
        ## debug message
        self.logger.log(LogLevels.VERBOSE, "Instrument parameters applied.")

    def swap_items_by_index(self, container, index_1, index_2):
        '''
        Swap two items (specified by index) in the given container.
        '''
        temp = container[index_1]
        container[index_1] = container[index_2]
        container[index_2] = temp

    def sort_iteration_order(self):
        '''
        Re-order the iteration items list in the reference hdf5 file, based on the specified iteration order.
        '''
        ## Status message
        self.logger.debug("Sorting iteration order...")
        ## Open reference config file and re-order iteration list
        with h5py.File(self.MeasurementObject.sCfgFileIn, 'r+') as config_file:
            for index_counter, channel_name in enumerate(self._iteration_order):
                ## Generate list of channels in the order they currently appear
                current_iter_order = [step_item[0] for step_item in config_file['Step list'][()]]
                ## Get index of desired channel name in current order
                channel_index = current_iter_order.index(channel_name)
                ## Swap desired channel with that at index_counter
                self.swap_items_by_index(config_file['Step list'], index_counter, channel_index)
        ## status message
        self.logger.debug("Iteration order sorted.")

    def apply_api_values(self):
        '''
        Apply all stored point values (including for SQPG) through the Labber API.
        '''
        ## Status message
        self.logger.log(LogLevels.VERBOSE, "Applying parameter point values...")
        ## Apply all non-pulse parameters (including main SQPG parameters)
        for instrument_name, instrument_params in self._api_values.items():
            for param_name, param_value in instrument_params.items():
                target_string = " - ".join([instrument_name, param_name])
                self.update_api_value(target_string, param_value)
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
                    self.update_api_value(target_string, param_value)
        ## Sort iteration parameters
        self.sort_iteration_order()
        ## Status message
        self.logger.debug('Parameter point values applied.')

    def update_api_value(self, target_string, param_value):
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
            ## Status message
            self.logger.log(LogLevels.SPECIAL, \
                    "Instrument value updated: \'{}\' to {}".format(target_string, param_value))
        else: # the parameter is a single value, either string or numeric
            self.MeasurementObject.updateValue(target_string, param_value, 'SINGLE')
            ## Status message
            self.logger.log(LogLevels.VERBOSE, \
                    "Instrument value updated: \'{}\' to {}".format(target_string, param_value))
        ## Status message
        self.logger.debug('Labber API values applied.')

    def apply_client_values(self):
        '''
        Apply all stored values that are marked for application through the InstrumentClient interface
        '''
        ## Status message
        self.logger.log(LogLevels.VERBOSE, 'Applying InstrumentClient values...')
        ## Open server connection
        self.logger.debug('Opening connection to Labber InstrumentServer...')
        try:
            ServerClient = Labber.connectToServer(self._InstrumentServer)
        except:
            self.logger.error('Could not connect to server; skipping...')
            ## Could not connect to server; do not attempt further client value application
            return
        else:
            pass
        ## Iterate through instruments, opening InstrumentClient instance
        for instrument_name, hardware_name in self._hardware_names.items():
            ## Connect to instrument
            self.logger.debug('Connecting to instrument {} ({})'.format(instrument_name, hardware_name))
            ## Treat strings and lists/arrays differently (weird Labber quirk)
            array_params = {}
            string_params = {}
            for param_name, param_value in self._client_values[instrument_name].items():
                if isinstance(param_value, str):
                    self.logger.log(LogLevels.TRACE, '{} is a string: {}'.format(param_name, param_value))
                    string_params[param_name] = param_value
                elif isinstance(param_value, list) or isinstance(param_value, np.ndarray):
                    self.logger.log(LogLevels.TRACE, '{} is a list/array: {}'.format(param_name, param_value))
                    array_params[param_name] = param_value
            ## Open InstrumentClient
            instClient = ServerClient.connectToInstrument(hardware_name, {'name': instrument_name})
            ## Iterate over arrays/lists
            for param_name, param_value in array_params.items():
                ## Set parameter value
                instClient.setValue(param_name, param_value)
                ## Status message
                self.logger.debug('Set value: {} to {} ({})'.format(param_name, \
                                                    param_value, type(param_value)))
            ## Apply string values
            instClient.setInstrConfig(string_params)
            ## Print status messages
            for param_name in string_params.keys():
                self.logger.debug('Set value: {} to {}'.format(param_name, \
                                            instClient.getValue(param_name)))
            ## Close connection to instrument
            instClient.disconnectFromInstr()
            ##
            self.logger.debug('Disconnected from instrument: {}'.format(instrument_name))
        ## Close server connection
        ServerClient.close()
        self.logger.debug('Labber InstrumentServer connection closed.')
        ## Status message
        self.logger.debug('InstrumentClient values applied.')

    def apply_instr_config_values(self):
        '''
        Apply all stored values through direct editing of the Instrument Config attributes in the reference hdf5 file.
        '''
        ## Status message
        self.logger.log(LogLevels.VERBOSE, 'Applying Instrument Config values...')
        ## Iterate over instruments
        for instrument_name in self._instr_config_values.keys():
            self.logger.debug('Applying Instrument Config values for {}'.format(instrument_name))
            instrument_params = self._instr_config_values[instrument_name]
            hardware_name = self._hardware_names[instrument_name]
            full_instrument_string = hardware_name+' - , '+instrument_name+' at '+self._InstrumentServer
            ## Open file and set values
            with h5py.File(self.MeasurementObject.sCfgFileIn, 'r+') as config_file:
                ## Iterate over each instrument parameter
                for param_name, param_value in instrument_params.items():
                    self.logger.debug('Setting value: {} to {}'.format(param_name, param_value))
                    config_file['Instrument config'][full_instrument_string].attrs[param_name] = param_value
        ## Status message
        self.logger.debug('Instrument Config values applied.')

    def process_channel_defs(self):
        '''
        Convert the stored channel definitions to the format required for application to the hdf5 file.

        Note that this cannot be done during calling of the add_channel_defs method, as there is no guarantee that the MeasurementObject has been initialised at that stage.
        '''
        ## status message
        self.logger.debug("Processing channel definitions...")
        ## Fetch step list entry dtype (if not already fetched)
        if self._hdf5_sl_entry_dtype is None:
            ## status message
            self.logger.debug("Fetching step list entry dtype...")
            with h5py.File(self.MeasurementObject.sCfgFileIn, 'r') as config_file:
                for instrument_key in config_file['Step config']:
                    self._hdf5_sl_entry_dtype = np.dtype(config_file['Step config'][instrument_key]['Relation parameters'].dtype)
                    break # only need to fetch once
        ## Convert each of the stored definitions in self._raw_channel_defs to the appropriate format, and store in self._channel_defs
        for channel_key, channel_name in self._raw_channel_defs.items():
            self._channel_defs[channel_key] = np.array([(channel_key, channel_name, False)], dtype = self._hdf5_sl_entry_dtype)
        self.logger.debug("Channel definitions processed.")

    def get_sl_index(self, label_string):
        '''
        Gets the index of the entry matching label_string in the config file's 'Step list'.

        label_string should be a full channel name.
        '''
        ## status message
        self.logger.debug("Fetching step list index for {}...".format(label_string))
        ## Open file and extract existing step list
        with h5py.File(self.MeasurementObject.sCfgFileIn, 'r') as config_file:
            step_list = config_file['Step list'][()]
        self.logger.debug("Step list extracted.")
        ## Get index of element with matching label string
        step_list_labels = [labels['channel_name'] for labels in step_list]
        index = step_list_labels.index(label_string)
        self.logger.debug("Step list index extracted.")
        return index

    def apply_equation_string(self, label_string, equation_string):
        '''
        Apply the equation string for the given label_string specifying a full channel name.

        It is the user's responsibility to ensure that the correct channel keys are provided and referenced in the step config!
        '''
        ## status message
        self.logger.log(LogLevels.VERBOSE, "Applying equation string \'{}\' for {}".format(equation_string, label_string))
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
        self.logger.debug("Equation string set for {}".format(label_string))

    def apply_step_config(self, label_string, required_channel_keys):
        '''
        Apply the step config for a given label_string (describing a full channel name).

        This includes setting up the required_channel_keys from the stored processed channel key definitions.
        '''
        ## status message
        self.logger.debug("Applying step config for {}".format(label_string))
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
        self.logger.debug("Step config entries applied for {}".format(label_string))

    def apply_relation(self, channel_name, channel_relation):
        '''
        Apply a single channel relation to the hdf5 database file.
        '''
        ## status message
        self.logger.debug("Applying relation for: {}".format(channel_name))
        ## Extract equation and required channel keys
        equation_string = channel_relation[0]
        required_channel_keys = channel_relation[1]
        # Apply equation string
        self.apply_equation_string(channel_name, equation_string)
        ## Set appropriate step config entries
        self.apply_step_config(channel_name, required_channel_keys)
        ## status message
        self.logger.debug("Relation applied for: {}".format(channel_name))

    def apply_relations(self):
        '''
        Apply all channel relations by directly editing the reference hdf5 file.
        '''
        ## Status message
        self.logger.log(LogLevels.VERBOSE, "Applying channel relations...")
        ## Process channel definitions
        self.process_channel_defs()
        ## Set relations for each item in the stored relations
        for channel_name, channel_relation in self._channel_relations.items():
            self.apply_relation(channel_name, channel_relation)



    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
