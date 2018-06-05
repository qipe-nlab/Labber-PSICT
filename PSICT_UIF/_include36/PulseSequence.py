## Container classes for storing pulse sequence data
##  Subclassed into distinct classes for input (ie specified by user)
##  and output (used to set Labber parameters).

from PSICT_UIF._include36.Pulse import Pulse

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
        elif isinstance(new_pulse, Pulse):
            if verbose >= 3:
                print("New Pulse is already pulse object.")
            pass
        else:
            raise ValueError(" ".join(["Cannot interpret", new_pulse, "as pulse identifier"]))
        ## check if pulse with matching name already exists
        if new_pulse.name in self.pulse_names:
            raise KeyError(" ".join(["Pulse with name", new_pulse.name, "already exists."]))
        # TODO new_pulse.set_attributes(pulse_attributes)
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
