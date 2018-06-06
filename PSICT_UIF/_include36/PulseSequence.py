## Container classes for storing pulse sequence data
##  Subclassed into distinct classes for input (ie specified by user)
##  and output (used to set Labber parameters).

from PSICT_UIF._include36.Pulse import Pulse
import PSICT_UIF._include36._Pulse_rc as _rc

class PulseSeq:
    '''
    Docstring for PulseSeq.
    '''
    def __init__(self, *, verbose = 0):
        ## set logging level
        self.verbose = verbose
        ## initialise containers
        self.pulse_list = []
        self.main_params = {}
        ## debug message
        if self.verbose >= 4:
            print("Called PulseSeq constructor.")

    def __del__(self):
        ## debug message
        if self.verbose >= 4:
            print("Called PulseSeq destructor.")

    ###########################################################################
    ## Main (overall) parameter methods
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

    ## print list of pure pulse names when accessing pulse_names as attribute
    @property
    def pulse_names(self):
        return [pulse.name for pulse in self.pulse_list]

    ###########################################################################
    ## Pulse transactional methods

    ## access through subscript operator
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
        Docstring for add_pulse.
        '''
        ## handle new_pulse spec in different cases
        if isinstance(new_pulse, Pulse):
            if verbose >= 3:
                print("New Pulse is already pulse object.")
            pass
        elif isinstance(new_pulse, dict):
            if verbose >= 3:
                print("Creating a new pulse by attribute list")
            new_pulse = Pulse(new_pulse)
        else:
            raise ValueError(" ".join(["Cannot interpret", new_pulse, "as pulse identifier"]))
        ## check if pulse with matching name already exists
        if new_pulse.name in self.pulse_names:
            raise KeyError(" ".join(["Pulse with name", new_pulse.name, "already exists."]))
        self.pulse_list.append(new_pulse)


###############################################################################

class InputPulseSeq(PulseSeq):
    '''
    Docstring for InputPulseSeq.
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
    ## Pulse sequence import

    def set_pulse_seq(self, params_dict, * , verbose = 0):
        '''
        Docstring.
        '''
        ## debug message
        if verbose >= 1:
            print("Setting input pulse sequence parameters...")
        ## Set pulse sequence from input dict
        for pulse_name, pulse_params in params_dict.items():
            ## Check for main specification
            if pulse_name == "main":
                if verbose >= 2:
                    print("Setting sequence main parameters...")
                self.main_params = pulse_params
                if verbose >= 2:
                    print("Sequence main parameters set.")
            else:  ## add pulses normally
                ## debug message
                if verbose >= 2:
                    print("Setting parameters for pulse", pulse_name)
                ## add pulse name to param list
                pulse_params["name"] = pulse_name
                ## create new pulse with given parameters
                self.add_pulse(pulse_params)
                ## debug message
                if verbose >= 2:
                    print("Added pulse", pulse_name, "successfully.")
        ## debug message
        if verbose >= 1:
            print("Input pulse sequence parameters set.")

    # def set_main_params(self, main_params_dict, *, verbose = 0):
    #     '''
    #     Docstring.
    #     '''
    #     ## debug message
    #     if verbose >= 3:
    #         print("Setting main params for InputPulseSeq...")
    #     ##
    #     self.main_params = main_params_dict
    #     ## debug message
    #     if verbose >= 3:
    #         print("InputPulseSeq main params set.")
    #
    # def set_seq_params(self, param_dict, *, verbose = 0):
    #     '''
    #     Docstring
    #     '''
    #     for pulse_name, pulse_params in param_dict.items():
    #         ## debug message
    #         if verbose >= 2:
    #             print("Setting parameters for pulse", pulse_name)
    #         ## add pulse name to param list
    #         pulse_params["name"] = pulse_name
    #         ## create new pulse with given parameters
    #         self.add_pulse(pulse_params)
    #         ## debug message
    #         if verbose >= 2:
    #             print("Added pulse", pulse_name, "successfully.")

    def pulse_pre_conversion(self, *, verbose = 0):
        '''
        Operations that need to be carried out on the pulses before they are sorted into time-order and converted to the output sequence.
        '''
        pass

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Pulse sequence sorting

    def get_sorted_list(self, sort_attribute = _rc.pulse_sort_attr, *, verbose = 0):
        '''
        Docstring.
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
    Docstring for OutputPulseSeq.
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
        Docstring.
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
        Import data from a list of pulses (in order)
        '''
        ## debug message
        if verbose >= 3:
            print("Setting pulse sequence in OutputPulseSeq...")
        ## Add pulses from list
        for pulse in pulse_list:
            self.add_pulse(pulse)
        ## Post-import processing
        self.pulse_post_conversion(verbose = verbose)
        ## debug message
        if verbose >= 3:
            print("OutputPulseSeq processing completed.")

    def pulse_post_conversion(self, *, verbose = 0):
        '''
        Post-conversion pulse sequence cleanup.
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
