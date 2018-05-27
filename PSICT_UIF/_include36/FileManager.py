## The PSICT-UIF file manager class
##  Handles all file names and paths, including creation and deletion
##  of temporary files.

from Labber import ScriptTools

class FileManager:
    '''
    Docstring for FileManager.
    '''

    def __init__(self, *, verbose = 0):
        ## set log level
        self.verbose = verbose
        ## flags
        self.is_labber_exe_default = True
        ## debug message
        if self.verbose >= 4:
            print("Called FileManager constructor.")

    def __del__(self):
        if self.verbose >= 4:
            print("Called FileManager destructor.")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Labber executable methods

    def set_labber_exe_path(self, new_labber_exe_path, *, verbose = 0):
        '''
        Set the Labber executable path manually.

        The is_labber_exe_default flag tracks if this method has been called; if it is True at the time of calling the measurement method from the psictUIFInterface, the os-sensitive default will be used.
        '''
        if verbose >= 2:
            print("Setting Labber executable path to:", new_labber_exe_path)
        ScriptTools.setExePath(new_labber_exe_path)
        self.is_labber_exe_default = False
        if verbose >= 2:
            print("Labber executable path set.")


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
