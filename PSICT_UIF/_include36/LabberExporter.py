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
        self.apply_point_values(verbose = verbose)
        self.apply_iteration_values(verbose = verbose)
        self.apply_relations(verbose = verbose)
        ## debug message
        if verbose >= 1:
            print("Instrument parameters applied.")

    def apply_point_values(self, *, verbose = 0):
        '''
        Apply all stored point values (including for SQPG) through the Labber API.
        '''
        if verbose >= 2:
            print("LabberExporter: Applying parameter point values...")

    def apply_iteration_values(self, *, verbose = 0):
        '''
        Apply all stored iteration values through the Labber API.
        '''
        if verbose >= 2:
            print("LabberExporter: Applying parameter iteration values...")

    def apply_relations(self, *, verbose = 0):
        '''
        Apply all channel relations by directly editing the reference hdf5 file.
        '''
        if verbose >= 2:
            print("LabberExporter: Applying channel relations...")



    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
