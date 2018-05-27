## The PSICT-UIF file manager class
##  Handles all file names and paths, including creation and deletion
##  of temporary files.

class FileManager:
    '''
    Docstring for FileManager.
    '''

    def __init__(self, *, verbose = 0):
        self.verbose = verbose
        if self.verbose >= 4:
            print("Called FileManager constructor.")

    def __del__(self):
        if self.verbose >= 4:
            print("Called FileManager destructor.")
