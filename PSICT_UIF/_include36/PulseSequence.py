## Container classes for storing pulse sequence data
##  Subclassed into distinct classes for input (ie specified by user)
##  and output (used to set Labber parameters).

from operator import attrgetter
import warnings
import logging

from PSICT_UIF._include36.Pulse import Pulse
import PSICT_UIF._include36._Pulse_rc as _rc
import PSICT_UIF._include36._LogLevels as LogLevels
from PSICT_UIF._include36._Common import extract_relation_variables

class PulseSeq:
    '''
    Abstract representation of an entire pulse sequence; acts as a container for Pulse objects.

    This class should not be used directly, as it acts as a subclass for the InputPulseSeq and OutputPulseSeq classes.
    '''
    def __init__(self, *, parent_logger_name = None):
        ## Logging
        if parent_logger_name is not None:
            logger_name = '.'.join([parent_logger_name, 'PulseSeq'])
        else:
            logger_name = 'PulseSeq'
        self.logger = logging.getLogger(logger_name)
        ## initialise containers
        self.pulse_list = []  # holds Pulse objects
        self.main_params = {} # holds parameters that are set for the whole sequence
        self.channel_defs = {}
        self.channel_relations = {}
        ## debug message
        self.logger.log(LogLevels.TRACE, 'Instance initialized.')

    def __del__(self):
        ## Status message
        self.logger.log(LogLevels.TRACE, 'Instance deleted.')

    def assign_script_rcmodule(self, rcmodule, rcpath):
        '''
        Assign the passed script rcmodule (already-imported rcfile) to the PulseSeq object.
        '''
        self._script_rc = rcmodule
        self._script_rcpath = rcpath

    ###########################################################################
    ## Sequence main parameter methods

    @property
    def main_params(self):
        return self.__main_params
    @main_params.setter
    def main_params(self, new_dict):
        self.__main_params = new_dict


    ###########################################################################
    ## Pulse list methods

    @property
    def pulse_list(self):
        return self.__pulse_list
    @pulse_list.setter
    def pulse_list(self, new_list):
        self.__pulse_list = new_list

    ## Print list of pure pulse names when accessing pulse_names as attribute
    @property
    def pulse_names(self):
        return [pulse.name for pulse in self.pulse_list]

    ###########################################################################
    ## Pulse transactional methods

    ## Access through subscript operator
    def __getitem__(self, id):
        ## if id is string, attempt to get by name
        if isinstance(id, str):
            id = self.pulse_names.index(id)
        ## else pass (hopefully valid index) directly
        else:
            pass
        return self.pulse_list[id]

    def add_pulse(self, new_pulse):
        '''
        Add a single pulse to the pulse sequence.

        The passed-in pulse specification new_pulse can either be an existing Pulse object, or a dict of parameters with which the new pulse should be created. (A ValueError will be raised if it is neither of the two)

        Note that the pulse name must be unique (relative to the other pulse names already stored in the sequence); a KeyError will be raised if a pulse with the same name already exists.
        '''
        ## Handle new_pulse spec in different cases
        if isinstance(new_pulse, Pulse):
            self.logger.log(LogLevels.TRACE, "New Pulse is already pulse object.")
            pass
        elif isinstance(new_pulse, dict):
            self.logger.log(LogLevels.TRACE, "Creating a new pulse by attribute list")
            new_pulse = Pulse(new_pulse)
        else:
            raise ValueError(" ".join(["Cannot interpret", new_pulse, "as pulse identifier"]))
        ## Check if pulse with matching name already exists
        if new_pulse.name in self.pulse_names:
            raise KeyError(" ".join(["Pulse with name", new_pulse.name, "already exists."]))
        ## Actually add pulse to list
        self.pulse_list.append(new_pulse)

    ###########################################################################
    ## Information & verification

    def print_info(self, *, all = False, main = False, pulses = True, pulse_params = False):
        '''
        Print information on pulse sequence for rapid verification.
        '''
        print("===========================")
        print("Pulse sequence information:")
        ## "all" option
        if all:
            main = True
            pulses = True
            pulse_params = True
        ## Main parameter values
        if main:
            print("Main parameters:")
            print(self.main_params)
        ## Pulse list - will show names
        if pulses:
            print("Pulse list:")
            print(self.pulse_list)
        ## All pulse parameters
        if pulse_params:
            for pulse in self.pulse_list:
                pulse.print_info()
        ##
        print("===========================")


###############################################################################

class InputPulseSeq(PulseSeq):
    '''
    Subclass of PulseSeq, intended specifically for receiving human-input pulse specifications.

    Also contains methods which prepare the pulse parameters for conversion to an output sequence, most notably calculation of an absolute-time specification for every pulse.
    '''
    def __init__(self, *, parent_logger_name = None):
        ## call base class constructor
        super().__init__()
        ## Logging
        if parent_logger_name is not None:
            logger_name = '.'.join([parent_logger_name, 'InputPulseSeq'])
        else:
            logger_name = 'InputPulseSeq'
        self.logger = logging.getLogger(logger_name)
        ## Status message
        self.logger.log(LogLevels.TRACE, 'Instance initialized.')

    def __del__(self):
        ## Status message
        self.logger.log(LogLevels.TRACE, "Instance deleted.")
        ## call base class destructor
        super().__del__()

    ## Global parameters for inverted pulses
    @property
    def inverted_params(self):
        return self.__inverted_params
    @inverted_params.setter
    def inverted_params(self, new_params):
        self.__inverted_params = new_params

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Input-specific main parameter methods

    def export_main_params(self):
        '''
        Carry out all required pre-export operations on the main parameters.
        '''
        if "SQPG" in self._script_rc.parameter_pre_process:
            if "main" in self._script_rc.parameter_pre_process["SQPG"]:
                warnings.warn("SQPG main parameter pre-calculation has not yet been implemented!")
        return self.main_params

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Pulse sequence import

    def set_pulse_seq(self, params_dict):
        '''
        Set the pulse sequence from an input dict (this should be the dict created by the user in the external script).

        Note that a pulse named "main" is treated as specifying the main sequence parameters; all other names will be treated as pulse names.
        '''
        ## Status message
        self.logger.debug("Setting input pulse sequence parameters...")
        ## Set pulse sequence from input dict
        for pulse_name, pulse_params in params_dict.items():
            if pulse_name == "main":        # check for main specification
                self.main_params = pulse_params
                self.logger.log(LogLevels.DEBUG, "Sequence main parameters set.")
            elif pulse_name == "inverted":  # check for global inverted pulse specification
                self.inverted_params = pulse_params
                self.logger.log(LogLevels.DEBUG, "Global inverted pulse parameters set.")
            else:                       # add pulses normally
                ## Status message
                self.logger.log(LogLevels.DEBUG, "Setting parameters for pulse {}".format(pulse_name))
                ## add pulse name to param list
                pulse_params["name"] = pulse_name
                ## create new pulse with given parameters
                self.add_pulse(pulse_params)
                ## debug message
                self.logger.log(LogLevels.TRACE, "Added pulse {} successfully.".format(pulse_name))
        ## debug message
        self.logger.debug("Input pulse sequence parameters set.")

    def set_pulse_parameter(self, pulse_id, param_name, param_value):
        '''
        Set the individual value for a pulse parameter.

        Contrast with 'bulk import' of set_pulse_seq.
        Note that the pulse can, as usual, be specified by either name or index.
        '''
        self[pulse_id][param_name] = param_value
        self.logger.debug("Set pulse {} parameter {} to {}".format(str(pulse_id), param_name, param_value))


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Channel relations

    def add_channel_defs(self, channel_defs_dict):
        '''
        Add channel key definitions (for setting channel relations)
        '''
        ## status message
        self.logger.debug("Adding channel definitions to InputPulseSeq...")
        self.channel_defs = channel_defs_dict

    def add_channel_relations(self, channel_relations_dict):
        '''
        Add channel relations.
        '''
        ## status message
        self.logger.debug("Adding channel relations...")
        ## Extract required variable names if not provided
        for pulse_name, pulse_relations in channel_relations_dict.items():
            for param_name, param_relations in pulse_relations.items():
                ## Check if provided value is string or list
                if isinstance(param_relations, str):
                    self.logger.log(LogLevels.VERBOSE, 'Channel relation variables not provided for SQPG::{}::{}'.format(pulse_name, param_name))
                    self.logger.log(LogLevels.VERBOSE, 'Relation equation string: \'{}\''.format(param_relations))
                    ## Extract variable names and create list
                    variable_names = extract_relation_variables(param_relations)
                    self.logger.log(LogLevels.VERBOSE, 'Variables extracted: {}'.format(variable_names))
                    channel_relations_dict[pulse_name][param_name] = [param_relations, variable_names]
                else:
                    self.logger.log(LogLevels.VERBOSE, 'Channel relation variables provided for SQPG::{}::{}'.format(pulse_name, param_name))
                    ## Variable names are already provided; skip
                    continue
        self.channel_relations = channel_relations_dict

    def get_channel_defs(self):
        '''
        Get channel definitions.
        '''
        ## status message
        self.logger.debug("Getting channel definitions from InputPulseSeq...")
        return self.channel_defs

    def get_channel_relations(self):
        '''
        Get channel relations.
        '''
        ## status message
        self.logger.debug("Getting channel relations from InputPulseSeq...")
        return self.channel_relations

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Pulse sequence sorting

    def pulse_pre_conversion(self):
        '''
        Carry out all required pre-conversion operations on the pulse parameters.

        Most notably, this involves parameter value adjustment (eg converting to ns), as well as working out the timing/ordering of the entire pulse sequence.
        '''
        ## Status message
        self.logger.debug("Carrying out pulse sequence pre-conversion...")

        ###########################################
        #### Setting required pulse parameters ####
        ###########################################

        self.logger.debug("Setting required pulse parameter defaults...")
        ## Set required pulse parameter defaults
        for _default_param, _default_value in _rc.PULSE_PARAM_DEFAULTS.items():
            for pulse in self.pulse_list:
                if not _default_param in pulse.attributes:
                    pulse[_default_param] = _default_value
        self.logger.log(LogLevels.TRACE, "Required pulse parameter defaults set.")

        ##########################################
        #### Setting special pulse parameters ####
        ##########################################

        self.logger.debug("Applying global inverted-pulse parameters... (pre-absolute_time calculation)")
        ## For each pulse that is_inverted, apply the global parameters
        for pulse in self.pulse_list:
            if pulse["is_inverted"]:
                pulse.set_attributes(self.inverted_params)
        self.logger.log(LogLevels.TRACE, "Global inverted-pulse parameters applied. (pre-absolute_time calculation)")

        ##############################################
        ## Converting values based on script-rcfile ##
        ##############################################

        self.logger.log(LogLevels.TRACE, "SQPG values undergoing pre-calculation (based on script-rcfile specification)...")
        ## Fetch the appropriate specifications
        try:
            SQPG_spec = self._script_rc.parameter_pre_process["SQPG"]
        except KeyError:
            self.logger.warning("SQPG pre-calculation spec not found.")
        else:
            try:
                pulse_spec = SQPG_spec["pulse"]
            except KeyError:
                self.logger.warning("SQPG pre-calculation pulse spec not found.")
            else:
                for param_name, param_converter in pulse_spec.items():
                    ## Status message
                    self.logger.log(LogLevels.TRACE, "Carrying out pre-calculation conversion for {}".format(param_name))
                    ## Cycle through each pulse and apply the desired pre-calculations
                    if isinstance(param_converter, dict):
                        for pulse in self.pulse_list:
                            pulse[param_name] = param_converter[pulse[param_name]]
                    ## Leave skeleton for potentially adding different conversion objects
                    else:
                        pass
        ## Status message
        self.logger.log(LogLevels.TRACE, "Pre-calculation completed for SQPG values")

        ####################################
        #### Absolute time calculations ####
        ####################################
        self.logger.debug("Carrying out absolute_time calculations...")

        ## First, all pulses which have their time_reference set as "absolute" automatically have a valid absolute time if it is specified
        self.logger.log(LogLevels.TRACE, "Setting validity of absolute_time for pulses with 'absolute' time_reference...")
        for pulse in self.pulse_list:
            if pulse["time_reference"] == "absolute":
                ## Verify that an absolute_time parameter is actually set (can fall back on time_offset if there is no absolute_time)
                if "absolute_time" in pulse.attributes:
                    pass
                elif "time_offset" in pulse.attributes:
                    pulse["absolute_time"] = pulse["time_offset"]
                else:
                    raise RuntimeError(" ".join(["Pulse", pulse.name, "has no absolute_time or time_offset specified, but time_reference is set as 'absolute'."]))
                ## Set flag
                pulse.valid_abs_time = True
        self.logger.log(LogLevels.TRACE, "Absolute time set for 'absolute' time_reference pulses.")
        # if verbose >= 4:
        #     print("Current pulse state:")
        #     self.print_info(pulse_params = True)
        #     print("Absolute time validity:")
        #     print([pulse.valid_abs_time for pulse in self.pulse_list])

        ## debug message
        self.logger.log(LogLevels.TRACE, "Setting absolute time for pulses with 'previous' and 'relative' time reference...")
        ## Loop through pulses for the next two processes, as there may be odd dependencies
        max_loop_counter = len(self.pulse_list) # at least one pulse should be set each loop
        loop_counter = 0
        ## First, set the value of the pulse_number attribute to None for pulses where it is not already set; this will enable checking for it without errors
        for pulse in self.pulse_list:
            if "pulse_number" in pulse.attributes:
                continue
            else:
                pulse["pulse_number"] = -1
        ## Loop through pulses
        while not all([pulse.valid_abs_time for pulse in self.pulse_list]):
            self.logger.log(LogLevels.TRACE, "Looping through pulse list, iteration {}".format(loop_counter))
            ## check maximum loops - could indicate improper time-ordering dependencies
            if loop_counter >= max_loop_counter:
                raise RuntimeError("Could not calculate pulse timing; please re-check dependencies to ensure calculation is possible!")

            ## Then, any pulses with time_reference set to "previous", which will be set by incrementing upwards through user-specified pulse_number parameters

            ##    Find the maximal user-defined pulse number to serve as an upper limit for iterating the pulse counter
            max_pulse_number = max([pulse["pulse_number"] for pulse in self.pulse_list])
            ##    Finally, iterate upwards through increasing pulse numbers, calculating the absolute times of all pulses with pulse numbers and time_reference = "previous"
            pulse_counter = 0
            previous_pulse = None
            absolute_time = 0.0
            while pulse_counter <= max_pulse_number:
                current_pulse = next((pulse for pulse in self.pulse_list if pulse["pulse_number"] == pulse_counter), None)
                if current_pulse is not None: # ensure that a pulse with this pulse number was returned above
                    if current_pulse["time_reference"] == "previous":
                        ## Check that we are not attempting to specify this for the first pulse (there is no previous pulse!)
                        if previous_pulse is None:
                            raise RuntimeError("Cannot use 'previous' time reference for first numbered pulse")
                        ## Otherwise, calculate absolute time
                        if current_pulse.valid_abs_time:
                            pass
                        else:
                            self.calculate_absolute_time(current_pulse, previous_pulse)
                    else: # the current pulse does not have 'previous' as its time_reference specification - do nothing
                        pass
                    ## If a pulse with this pulse_number exists, always update the previous_pulse reference
                    previous_pulse = current_pulse
                else:  # no pulse with this number exists
                    pass
                ## Update pulse counter
                pulse_counter = pulse_counter + 1

            ## Finally, any pulses which have their reference relative to a named pulse
            for current_pulse in self.pulse_list:
                if current_pulse["time_reference"] == 'relative':
                    ## Ensure that reference pulse is specified by name
                    try:
                        ref_pulse_name = current_pulse["relative_to"]
                    except KeyError:
                        raise RuntimeError(" ".join([str(current_pulse), "has time_reference set as 'relative', but no reference pulse name is specified."]))
                    ## Attempt to fetch ref pulse
                    try:
                        ref_pulse = self[ref_pulse_name]
                    except KeyError:
                        raise RuntimeError(" ".join(["No pulse with name", ref_pulse_name, "exists."]))
                    ## Check if current pulse already has a valid absolute time set
                    if current_pulse.valid_abs_time:
                        # if verbose >= 4:
                        #     print(str(current_pulse), "already has a valid absolute time, skipping...")
                        pass
                    else:
                        # if verbose >= 4:
                        #     print(str(current_pulse), "has no valid absolute time; calculating...")
                        self.calculate_absolute_time(current_pulse, ref_pulse)
                ##
            ## debug message
            # if verbose >= 4:
            #     print("Current pulse state:")
            #     self.print_info(pulse_params = True)
            #     print("Absolute time validity:")
            #     print([pulse.valid_abs_time for pulse in self.pulse_list])
            ## Increment loop counter to prevent infinite loops
            loop_counter = loop_counter + 1

        ## End looping through pulses
        ##    Clean up - remove artificially-added pulse_number specifications
        for pulse in self.pulse_list:
            if pulse["pulse_number"] == -1:
                del pulse["pulse_number"]
        ## Status message
        self.logger.log(LogLevels.TRACE, "Absolute time set for 'previous' and 'relative' reference pulses.")
        ## Absolute times calculations finished
        self.logger.log(LogLevels.TRACE, "Absolute time calculations completed.")

        ####
        ## Status message
        self.logger.debug("Pulse sequence pre-conversion completed.")

    def calculate_absolute_time(self, current_pulse, reference_pulse):
        '''
        Calculate the absolute time of the current_pulse relative to the relative_marker (start or end) of the reference_pulse.

        Note that if the reference pulse does not have a valid absolute time, the function will return nothing; this is intended to be used when looping through the pulse list to brute-force potentially-complex dependencies.
        '''
        ## Assert that the reference pulse already has a valid absolute time calculated; if not, the pulse is skipped, and the loop in pulse_pre_conversion will attempt this again
        if reference_pulse.valid_abs_time:
            ## Check reference point - default to 'end' (as is usual for e2e spec in Labber GUI)
            if "relative_marker" not in current_pulse.attributes:
                current_pulse["relative_marker"] = 'end'
            ## Assume measurement from 'start'
            # if verbose >= 4:
            #     print("Current pulse is:", current_pulse.name)
            #     print("Reference pulse info:")
            #     reference_pulse.print_info()
            #     print(reference_pulse.valid_abs_time)
            new_absolute_time = reference_pulse["absolute_time"] + current_pulse["time_offset"]
            ## Add reference_pulse width if from 'end'
            if current_pulse["relative_marker"] == 'end':
                ## Calculate new absolute time
                new_absolute_time = new_absolute_time + reference_pulse["w"] + reference_pulse["v"]
            ## Set time and flag
            current_pulse["absolute_time"] = new_absolute_time
            current_pulse.valid_abs_time = True
        else:
            return
        ##


    def get_sorted_list(self, sort_attribute = _rc.pulse_sort_attr):
        '''
        Fetch the list of pulses in the sequence, sorted by an attribute (should be absolute_time).

        The output of this method can be passed directly to an OutputPulseSeq.
        '''
        ## Status message
        self.logger.debug("Getting sorted pulse sequence...")
        ## Carry out pre-sort processing
        self.pulse_pre_conversion()
        ## Assert that each pulse in the sequence has the appropriate sort attribute set
        assert all([pulse.valid_abs_time for pulse in self.pulse_list]), "There are pulses which do not have a valid (set or calculated) absolute_time attribute."
        ## debug message
        self.logger.log(LogLevels.TRACE, "Sorting by attribute: {}".format(sort_attribute))
        return sorted(self.pulse_list, key = lambda x: x[sort_attribute])

###############################################################################

###############################################################################

###############################################################################

class OutputPulseSeq(PulseSeq):
    '''
    Subclass of PulseSeq, intended specifically for exporting pulse specifications to Labber.

    Also contains methods which prepare the pulse parameters for export to Labber from a time-ordered list of pulses obtained through an InputPulseSeq -> OutputPulseSeq conversion. Note that this should not be done directly, but instead handled by a PulseSeqManager object.
    '''
    def __init__(self, *, parent_logger_name = None):
        ## call base class constructor
        super().__init__()
        ## Logging
        if parent_logger_name is not None:
            logger_name = '.'.join([parent_logger_name, 'OutputPulseSeq'])
        else:
            logger_name = 'OutputPulseSeq'
        self.logger = logging.getLogger(logger_name)
        ## Flags
        self.is_exportable = False
        ## debug message
        self.logger.log(LogLevels.TRACE, 'Instance initialized.')

    def __del__(self):
        ## Status message
        self.logger.log(LogLevels.TRACE, 'Instance deleted.')
        ## call base class destructor
        super().__del__()

    @property
    def end_pulse(self):
        return max(self.pulse_list, key = attrgetter('end_time'))
    @property
    def total_time(self):
        return self.end_pulse.end_time + self.end_pulse["w"]*(self.main_params["Truncation range"] - 1)/2

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Pulse import methods (post-conversion)

    def set_main_params(self, param_dict):
        '''
        Set the pulse sequence main parameters.
        '''
        ## Status message
        self.logger.debug("Importing main parameters for OutputPulseSeq...")
        ##
        self.main_params = param_dict

    def set_pulse_seq(self, pulse_list):
        '''
        Import data from a (sorted) list of pulses.
        '''
        ## debug message
        self.logger.debug("Setting pulse sequence in OutputPulseSeq...")
        ## Add pulses from list
        for pulse in pulse_list:
            self.add_pulse(pulse)
        # if verbose >= 4:
        #     print("Imported pulse sequence in OutputPulseSeq:")
        #     self.print_info(pulse_params = True)
        ## Post-import processing
        self.pulse_post_conversion()
        ## debug message
        self.logger.log(LogLevels.TRACE, "OutputPulseSeq processing completed.")

    def pulse_post_conversion(self):
        '''
        Post-conversion pulse sequence cleanup.

        This method carries out any modifications to the pulse sequence parameters such that they are ready for export to Labber.
        '''
        ## debug messsage
        self.logger.debug("Carrying out post-conversion processing on output sequence...")
        ## Assign pulse number attributes based on ordering
        for index, pulse in enumerate(self.pulse_list):
            pulse["pulse_number"] = index + 1  # pulse numbering starts at 0
        ## Set number of pulses
        self.main_params["# of pulses"] = len(self.pulse_list)

        ## TODO unit processing on values?

        ###################
        ## Set up timing ##
        ###################
        ## Get first pulse delay from absolute time of first pulse
        self.main_params["First pulse delay"] = self.pulse_list[0]["absolute_time"]
        ## Iterate through pulses, setting previous pulse's spacing based on next pulse's absolute_time
        for current_pulse, next_pulse in zip(self.pulse_list[:-1], self.pulse_list[1:]):
            # if verbose >= 4:
            #     print("Calculating pulse spacing between", current_pulse, "and", next_pulse)
            current_pulse["s"] = next_pulse["absolute_time"] - current_pulse.end_time
            # if verbose >= 4:
            #     print("\tNext pulse absolute time:", next_pulse['absolute_time'])
            #     print("\tCurrent pulse end time:", current_pulse.end_time)
            #     print("\tCurrent pulse spacing:", current_pulse['s'])
        ## Set pulse sequence length (number of points)
        if 'sequence_duration' in self.main_params and 'Sample rate' in self.main_params:
            self.main_params['Number of points'] = int(self.main_params['sequence_duration']*self.main_params['Sample rate'])
        if 'sequence_duration' in self.main_params:
            del self.main_params['sequence_duration']
        ####
        # if verbose >= 4:
        #     print("Pulse parameters after pre-export timing conversions:")
        #     self.print_info(pulse_params = True)

        ####
        ## Convert all physical parameter pulse shortcodes to full names
        self.logger.log(LogLevels.TRACE, "Converting parameter shortcodes...")
        for param_full_name, param_short_name in _rc.FULL_NAMES_PULSES.items():
            self.logger.log(LogLevels.TRACE, "Converting {} into {}...".format(param_short_name, param_full_name))
            for pulse in self.pulse_list:
                try:
                    param_value = pulse[param_short_name]
                except KeyError:
                    continue
                else:
                    del pulse[param_short_name]
                    pulse[param_full_name] = param_value
        self.logger.log(LogLevels.TRACE, "Parameter shortcodes converted.")

        ## set flag
        self.is_exportable = True
        ## debug message
        self.logger.log(LogLevels.TRACE, "Post-conversion processing on output sequence completed.")


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Channel relations

    def process_channel_defs(self, channel_defs_dict):
        '''
        Process channel definitions.
        '''
        self.logger.debug("Processing channel definitions...")
        processed_channel_defs = {}
        ## Convert pulse names to pulse numbers
        for pulse_name, pulse_defs in channel_defs_dict.items():
            if pulse_name == "main":
                processed_channel_defs[0] = pulse_defs
            else:
                pulse_number = self[pulse_name]["pulse_number"]
                processed_channel_defs[pulse_number] = pulse_defs
        ##
        return processed_channel_defs

    def process_channel_relations(self, channel_relations_dict):
        '''
        Process channel relations.
        '''
        ## Status message
        self.logger.debug("Processing channel relations...")
        processed_channel_relations = {}
        ## Convert pulse names to pulse numbers
        for pulse_name, pulse_defs in channel_relations_dict.items():
            if pulse_name == "main":
                processed_channel_relations[0] = pulse_defs
            else:
                pulse_number = self[pulse_name]["pulse_number"]
                processed_channel_relations[pulse_number] = pulse_defs
        return processed_channel_relations

    def add_channel_defs(self, channel_defs_dict):
        '''
        Add channel key definitions (for setting channel relations)
        '''
        ## Status message
        self.logger.debug("Adding channel definitions...")
        self.channel_defs = self.process_channel_defs(channel_defs_dict)

    def add_channel_relations(self, channel_relations_dict):
        '''
        Add channel relations.
        '''
        ## Status message
        self.logger.debug("Adding channel relations...")
        self.channel_relations = self.process_channel_relations(channel_relations_dict)

    def get_channel_defs(self):
        '''
        Get channel definitions.
        '''
        ## status message
        self.logger.debug("Getting channel definitions...")
        return self.channel_defs

    def get_channel_relations(self):
        '''
        Get channel relations.
        '''
        ## status message
        self.logger.debug("Getting channel relations...")
        return self.channel_relations

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Pulse sequence export

    def export(self):
        '''
        Returns the output sequence, ready to be parsed by the LabberExporter and read into the Labber API.
        '''
        ## Check if pulse sequence is ready for export
        if not self.is_exportable:
            raise RuntimeError("Output pulse sequence is not ready for export.")
        ## export pulse sequence
        return self.pulse_list
