## Container classes for storing pulse sequence data
##  Subclassed into distinct classes for input (ie specified by user)
##  and output (used to set Labber parameters).

from PSICT_UIF._include36.Pulse import Pulse
import PSICT_UIF._include36._Pulse_rc as _rc

class PulseSeq:
    '''
    Abstract representation of an entire pulse sequence; acts as a container for Pulse objects.

    This class should not be used directly, as it acts as a subclass for the InputPulseSeq and OutputPulseSeq classes.
    '''
    def __init__(self, *, verbose = 0):
        ## set logging level
        self.verbose = verbose
        ## initialise containers
        self.pulse_list = []  # holds Pulse objects
        self.main_params = {} # holds parameters that are set for the whole sequence
        ## debug message
        if self.verbose >= 4:
            print("Called PulseSeq constructor.")

    def __del__(self):
        ## debug message
        if self.verbose >= 4:
            print("Called PulseSeq destructor.")

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

    def add_pulse(self, new_pulse, *, verbose = 0):
        '''
        Add a single pulse to the pulse sequence.

        The passed-in pulse specification new_pulse can either be an existing Pulse object, or a dict of parameters with which the new pulse should be created. (A ValueError will be raised if it is neither of the two)

        Note that the pulse name must be unique (relative to the other pulse names already stored in the sequence); a KeyError will be raised if a pulse with the same name already exists.
        '''
        ## Handle new_pulse spec in different cases
        if isinstance(new_pulse, Pulse):
            if verbose >= 4:
                print("New Pulse is already pulse object.")
            pass
        elif isinstance(new_pulse, dict):
            if verbose >= 4:
                print("Creating a new pulse by attribute list")
            new_pulse = Pulse(new_pulse, verbose = verbose)
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
    def __init__(self, *, verbose = 0):
        ## call base class constructor
        super().__init__(verbose = verbose)
        ## debug message
        if self.verbose >= 4:
            print("Called InputPulseSeq constructor.")

    def __del__(self):
        ## debug message
        if self.verbose >= 4:
            print("Called InputPulseSeq destructor.")
        ## call base class destructor
        super().__del__()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Input-specific main parameter methods

    def export_main_params(self, *, verbose = 0):
        '''
        Carry out all required pre-export operations on the main parameters.
        '''
        return self.main_params

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Pulse sequence import

    def set_pulse_seq(self, params_dict, * , verbose = 0):
        '''
        Set the pulse sequence from an input dict (this should be the dict created by the user in the external script).

        Note that a pulse named "main" is treated as specifying the main sequence parameters; all other names will be treated as pulse names.
        '''
        ## debug message
        if verbose >= 1:
            print("Setting input pulse sequence parameters...")
        ## Set pulse sequence from input dict
        for pulse_name, pulse_params in params_dict.items():
            if pulse_name == "main":    # check for main specification
                if verbose >= 2:
                    print("Setting sequence main parameters...")
                self.main_params = pulse_params
                if verbose >= 2:
                    print("Sequence main parameters set.")
            else:                       # add pulses normally
                ## debug message
                if verbose >= 2:
                    print("Setting parameters for pulse", pulse_name)
                ## add pulse name to param list
                pulse_params["name"] = pulse_name
                ## create new pulse with given parameters
                self.add_pulse(pulse_params, verbose = verbose)
                ## debug message
                if verbose >= 2:
                    print("Added pulse", pulse_name, "successfully.")
        ## debug message
        if verbose >= 1:
            print("Input pulse sequence parameters set.")


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Pulse sequence sorting

    def pulse_pre_conversion(self, *, verbose = 0):
        '''
        Carry out all required pre-conversion operations on the pulse parameters.

        Most notably, this involves parameter value adjustment (eg converting to ns), as well as working out the timing/ordering of the entire pulse sequence.
        '''
        ## TODO Implement all the stuff mentioned in the docstring!
        ## debug message
        if verbose >= 2:
            print("Carrying out pulse sequence pre-conversion...")

        if verbose >= 3:
            print("Setting required pulse parameter defaults...")
        ## Set required pulse parameter defaults
        for _default_param, _default_value in _rc.PULSE_PARAM_DEFAULTS.items():
            for pulse in self.pulse_list:
                if not _default_param in pulse.attributes:
                    pulse[_default_param] = _default_value
        if verbose >= 3:
            print("Required pulse parameter defaults set.")

        ####################################
        #### Absolute time calculations ####
        ####################################
        if verbose >= 3:
            print("Carrying out absolute_time calculations...")

        ## First, all pulses which have their time_reference set as "absolute" automatically have a valid absolute time if it is specified
        if verbose >= 3:
            print("Setting validity of absolute_time for pulses with 'absolute' time_reference...")
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
        if verbose >= 3:
            print("Absolute time set for 'absolute' time_reference pulses.")
        if verbose >= 4:
            print("Current pulse state:")
            self.print_info(pulse_params = True)
            print("Absolute time validity:")
            print([pulse.valid_abs_time for pulse in self.pulse_list])

        ## debug message
        if verbose >= 3:
            print("Setting absolute time for pulses with 'previous' and 'relative' time reference...")
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
            if verbose >= 3:
                print("Looping through pulse list, iteration", loop_counter)
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
                            self.calculate_absolute_time(current_pulse, previous_pulse, verbose = verbose)
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
                        if verbose >= 4:
                            print(str(current_pulse), "already has a valid absolute time, skipping...")
                    else:
                        if verbose >= 4:
                            print(str(current_pulse), "has no valid absolute time; calculating...")
                        self.calculate_absolute_time(current_pulse, ref_pulse, verbose = verbose)
                ##
            ## debug message
            if verbose >= 4:
                print("Current pulse state:")
                self.print_info(pulse_params = True)
                print("Absolute time validity:")
                print([pulse.valid_abs_time for pulse in self.pulse_list])
            ## Increment loop counter to prevent infinite loops
            loop_counter = loop_counter + 1

        ## End looping through pulses
        ##    Clean up - remove artificially-added pulse_number specifications
        for pulse in self.pulse_list:
            if pulse["pulse_number"] == -1:
                del pulse["pulse_number"]
        ## debug message
        if verbose >= 3:
            print("Absolute time set for 'previous' and 'relative' reference pulses.")

        ####
        ## debug message
        if verbose >= 2:
            print("Pulse sequence pre-conversion completed.")

    def calculate_absolute_time(self, current_pulse, reference_pulse, *, verbose = 0):
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
            if verbose >= 4:
                print("Current pulse is:", current_pulse.name)
                print("Reference pulse info:")
                reference_pulse.print_info()
                print(reference_pulse.valid_abs_time)
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


    def get_sorted_list(self, sort_attribute = _rc.pulse_sort_attr, *, verbose = 0):
        '''
        Fetch the list of pulses in the sequence, sorted by an attribute (should be absolute_time).

        The output of this method can be passed directly to an OutputPulseSeq.
        '''
        ## debug message
        if verbose >= 2:
            print("Getting sorted pulse sequence...")
        ## Carry out pre-sort processing
        self.pulse_pre_conversion(verbose = verbose)
        ## Assert that each pulse in the sequence has the appropriate sort attribute set
        assert all([pulse.valid_abs_time for pulse in self.pulse_list]), "There are pulses which do not have a valid (set or calculated) absolute_time attribute."
        ## debug message
        if verbose >= 4:
            print("Sorting by attribute:", sort_attribute)
        return sorted(self.pulse_list, key = lambda x: x[sort_attribute])


###############################################################################

class OutputPulseSeq(PulseSeq):
    '''
    Subclass of PulseSeq, intended specifically for exporting pulse specifications to Labber.

    Also contains methods which prepare the pulse parameters for export to Labber from a time-ordered list of pulses obtained through an InputPulseSeq -> OutputPulseSeq conversion. Note that this should not be done directly, but instead handled by a PulseSeqManager object.
    '''
    def __init__(self, *, verbose = 0):
        ## call base class constructor
        super().__init__(verbose = verbose)
        ## debug message
        if self.verbose >= 4:
            print("Called OutputPulseSeq constructor.")

    def __del__(self):
        ## debug message
        if self.verbose >= 4:
            print("Called OutputPulseSeq destructor.")
        ## call base class destructor
        super().__del__()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Pulse import methods (post-conversion)

    def set_main_params(self, param_dict, *, verbose = 0):
        '''
        Set the pulse sequence main parameters.
        '''
        ## debug message
        if verbose >= 3:
            print("Importing main parameters for OutputPulseSeq...")
        ##
        self.main_params = param_dict
        ## debug message
        if verbose >= 3:
            print("OutputPulseSeq main parameter import completed.")

    def set_pulse_seq(self, pulse_list, *, verbose = 0):
        '''
        Import data from a (sorted) list of pulses.
        '''
        ## debug message
        if verbose >= 3:
            print("Setting pulse sequence in OutputPulseSeq...")
        ## Add pulses from list
        for pulse in pulse_list:
            self.add_pulse(pulse, verbose = verbose)
        ## Post-import processing
        self.pulse_post_conversion(verbose = verbose)
        ## debug message
        if verbose >= 3:
            print("OutputPulseSeq processing completed.")

    def pulse_post_conversion(self, *, verbose = 0):
        '''
        Post-conversion pulse sequence cleanup.

        This method carries out any modifications to the pulse sequence parameters such that they are ready for export to Labber.
        '''
        ## debug messsage
        if verbose >= 3:
            print("Carrying out post-conversion processing on output sequence...")
        ## Assign pulse number attributes based on ordering
        for index, pulse in enumerate(self.pulse_list):
            pulse["pulse_number"] = index + 1  # pulse numbering starts at 0
        ## debug message
        if verbose >= 3:
            print("Post-conversion processing on output sequence completed.")
