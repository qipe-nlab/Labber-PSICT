## The PSICT-UIF top-level interface class
##  In the course of normal scripting, this should be the only object
##  the the user directly interfaces with in the external script.

from PSICT_UIF._include36.FileManager import FileManager

class psictUIFInterface:
    '''
    Docstring for psictUIFInterface.
    '''

    def __init__(self, *, verbose = 0):
        self.verbose = verbose
        ## Add constituent objects
        ## NB declare all attributes explicitly for __del__ to work correctly
        self.fileManager = FileManager(verbose = self.verbose)
        if self.verbose >= 4:
            print("Called psictUIFInterface constructor.")

    def __del__(self):
        ## delete temporary files here (*before* deleting fileManager object!)
        del self.fileManager
        if self.verbose >= 4:
            print("Called psictUIFInterface destructor.")
