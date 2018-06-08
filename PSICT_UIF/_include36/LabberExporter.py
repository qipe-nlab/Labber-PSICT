## PSICT-UIF LabberExporter class
##  Stores and prepares all parameter settings before sending them to the
##  Labber measurement program.

class LabberExporter:
    '''
    Docstring for LabberExporter class.
    '''

    def __init__(self, *, verbose = 0):
        ## set object log level
        self.verbose = verbose
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
        if verbose >= 1:
            print("Importing point value specifications for", instrument_name)


    ## Pulse-sequence-specific mathods
    def receive_pulse_sequence(self, exported_pulse_seq, *, verbose = 0):
        '''
        Docstring for receive_pulse_sequence
        '''
        ## debug message
        if verbose >= 1:
            print("LabberExporter receiving pulse sequence...")
        ## TODO
        ## debug message
        if verbose >= 1:
            print("Pulse sequence received.")
