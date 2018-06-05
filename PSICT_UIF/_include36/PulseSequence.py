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
        ## debug message
        if self.verbose >= 4:
            print("Called PulseSeq constructor.")

    def __del__(self):
        ## debug message
        if self.verbose >= 4:
            print("Called PulseSeq destructor.")

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

    def add_pulse(self, new_pulse, pulse_attributes = {}, *, verbose = 0):
        '''
        Docstring for add_pulse.
        '''
        ## if pulse is a string, create a new Pulse
        if isinstance(new_pulse, str):
            if verbose >= 3:
                print("Creating a new pulse by name:", new_pulse)
            new_pulse = Pulse(new_pulse)
            new_pulse.set_attributes(pulse_attributes, verbose = verbose)
        elif isinstance(new_pulse, Pulse):
            if verbose >= 3:
                print("New Pulse is already pulse object.")
            pass
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
    ## Pulse sequence sorting

    def get_sorted_list(self, sort_attribute = _rc.pulse_sort_attr, *, verbose = 0):
        '''
        Docstring.
        '''
        ## debug message
        if verbose >= 2:
            print("Getting sorted pulse sequence...")
        # assert that each pulse in the sequence has the appropriate sort attribute set
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
