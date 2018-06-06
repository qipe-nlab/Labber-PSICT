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
        pass

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
        try:
            sort_times = [pulse[sort_attribute] for pulse in self.pulse_list]
        except KeyError:
            raise RuntimeError(" ".join(["There are pulses for which the", sort_attribute, "attribute has not been set."]))
        ## return pulse list sorted by sort attribute
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
