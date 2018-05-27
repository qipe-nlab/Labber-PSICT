## Container classes for storing pulse sequence data
##  Subclassed into distinct classes for input (ie specified by user)
##  and output (used to set Labber parameters).

class PulseSeq:
    '''
    Docstring for PulseSeq.
    '''
    def __init__(self, *, verbose = 0):
        self.verbose = verbose
        ## debug message
        if self.verbose >= 4:
            print("Called PulseSeq constructor.")

    def __del__(self):
        ## debug message
        if self.verbose >= 4:
            print("Called PulseSeq destructor.")


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
