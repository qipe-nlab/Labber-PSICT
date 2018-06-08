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
