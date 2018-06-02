## The PSICT-UIF file manager class
##  Handles all file names and paths, including creation and deletion
##  of temporary files.

import platform
import os
import re
import shutil

from Labber import ScriptTools

from PSICT_UIF._include36._FileManager_rc import (_FILEMGR_LABBER_EXE_PATH_MAC_DEFAULT, \
                                                  _FILEMGR_LABBER_EXE_PATH_WIN_DEFAULT, \
                                                  _FILEMGR_DEFAULTS_FILE_EXTENSION, \
                                                  _FILEMGR_DEFAULTS_COPY_POSTFIX, \
                                                  _FILEMGR_DEFAULTS_USER_INCREMENT, \
                                                  _FILEMGR_DEFAULTS_AUTO_INCREMENT, \
                                                  _FILEMGR_DEFAULTS_MAX_INCREMENTATION_ATTEMPTS, \
                                                 )


class FileManager:
    '''
    Docstring for FileManager.
    '''

    def __init__(self, *, verbose = 0):
        ## set object log level
        self.verbose = verbose
        ## set values of attributes constant across multiple methods
        self._REF_COPY_POSTFIX = _FILEMGR_DEFAULTS_COPY_POSTFIX
        ## set Labber exe path to system default
        self.setdef_labber_exe_path(verbose = self.verbose)
        ## debug message
        if self.verbose >= 4:
            print("Called FileManager constructor.")

    def __del__(self):
        ## debug message
        if self.verbose >= 4:
            print("Calling FileManager destructor.")
        ## Delete reference file (temporary copy of template file)
        self.clean_reference_file(verbose = self.verbose)
        ## debug message
        if self.verbose >= 4:
            print("FileManager destructor finished.")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Labber executable methods

    def set_labber_exe_path(self, new_labber_exe_path, *, verbose = 0):
        '''
        Set the Labber executable path stored in the FileManager object.

        Note that the path will only be applied immediately before the measurement is performed; validity checks are not carried out!
        '''
        ## normalize path
        new_labber_exe_path = os.path.normpath(new_labber_exe_path)
        ## debug message
        if verbose >= 2:
            print("New Labber executable path:", new_labber_exe_path)
        ## change attribute
        self.labber_exe_path = new_labber_exe_path
        ## debug message
        if verbose >= 2:
            print("New Labber executable path set.")

    def setdef_labber_exe_path(self, *, verbose = 0):
        '''
        Set the Labber executable path as the system default (os-sensitive).

        Currently supports Windows and Darwin (macOS); other operating systems will raise a RuntimeError.
        '''
        ## debug message
        if verbose >= 2:
            print("Setting Labber executable path spec to system default...")
        ## check os
        _SYSTEM = platform.system()
        if _SYSTEM == "Windows":
            if verbose >= 3:
                print("System identified as Windows; default executable path is", _FILEMGR_LABBER_EXE_PATH_WIN_DEFAULT)
            _SYSDEF_LABBER_EXE_PATH = _FILEMGR_LABBER_EXE_PATH_WIN_DEFAULT
        elif _SYSTEM == "Darwin":
            if verbose >= 3:
                print("System identified as macOS; default executable path is", _FILEMGR_LABBER_EXE_PATH_MAC_DEFAULT)
            _SYSDEF_LABBER_EXE_PATH = _FILEMGR_LABBER_EXE_PATH_MAC_DEFAULT
        else:
            raise RuntimeError("System could not be identified, or is not supported.\nplatform.system() returned:", _SYSTEM)
        ## change path stored in FileManager attributes
        self.set_labber_exe_path(_SYSDEF_LABBER_EXE_PATH, verbose = verbose)
        ## debug message
        if verbose >= 2:
            print("Labber executable path spec set to system default.")

    def apply_labber_exe_path(self, *, verbose = 0):
        '''
        Apply the Labber executable path stored in the FileManager object attributes to ScriptTools, ie "set" externally.

        NB: This method should not be used explicitly in the external script; it will be called as part of measurement pre-processing anyway.
        '''
        ## debug message
        if verbose >= 2:
            print("Applying Labber executable path...")
        ## set ScriptTools path
        ScriptTools.setExePath(self.labber_exe_path)
        ## debug message
        if verbose >= 2:
            print("Labber executable path applied.")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Database file methods

    def generate_full_path(self, dir_name, file_name, file_extension = _FILEMGR_DEFAULTS_FILE_EXTENSION):
        '''
        Generate the full path to a file of the specified directory, file name, and extension.

        The value of _FILEMGR_DEFAULTS_FILE_EXTENSION in the _FileManager_rc file is used as the default extension.
        '''
        return os.path.join(dir_name, "".join([file_name, ".", file_extension]))

    ## Template and reference file methods

    def set_template_file(self, template_dir, template_file, *, verbose = 0):
        '''
        Docstring for set_template_file.
        '''
        ## debug message
        if verbose >= 2:
            print("Setting template file...")
        ## Set attributes
        self.template_dir = os.path.expanduser(os.path.normpath(template_dir))
        self.template_file = template_file
        self.template_path = self.generate_full_path(self.template_dir, self.template_file)
        ## debug message
        if verbose >= 1:
            print("Template file set as:", self.template_path)
        ## Copy template file to create reference file
        self.copy_reference_file(verbose = verbose)


    def copy_reference_file(self, *, verbose = 0):
        '''
        Docstring for copy_reference_file
        '''
        ## debug message
        if verbose >= 3:
            print("Copying reference file...")
        ## Set names
        try:
            self.reference_dir = self.template_dir
            self.reference_file = "".join([self.template_file, self._REF_COPY_POSTFIX])
        except AttributeError:
            raise RuntimeError("The template directory and/or filename have not been specified.")
        self.reference_path = self.generate_full_path(self.reference_dir, self.reference_file)
        ## Copy file
        shutil.copy(self.template_path, self.reference_path)
        ## debug message
        if verbose >= 3:
            print("Reference file copied successfully:", self.reference_path)


    def clean_reference_file(self, *, verbose = 0):
        '''
        Docstring for clean_reference_file.
        '''
        ## debug message
        if verbose >= 3:
            print("Deleting temporary copy of reference file...")
        ## Delete temporary copy of reference file
        try:
            os.remove(self.reference_path)
        except (AttributeError, FileNotFoundError):
            pass
        else:
            ## debug message
            if verbose >= 3:
                print("Deleted reference file", self.reference_path)


    ## Output file methods

    def set_output_file(self, output_dir, output_file, *, verbose = 0):
        '''
        Docstring for set_output_file.
        '''
        ## debug message
        if verbose >= 2:
            print("Setting output file...")
        ## Set output dir (will not change)
        self.output_dir = os.path.expanduser(os.path.normpath(output_dir))
        ## Get valid output filename, checking for existence, incrementing if nececssary, etc
        valid_output_file = self.get_valid_output_file(self.output_dir, output_file, verbose = verbose)
        ## Set attributes
        self.output_file = valid_output_file
        self.output_path = self.generate_full_path(self.output_dir, self.output_file)
        ## debug message
        if verbose >= 1:
            print("Output file set as:", self.output_path)


    def get_valid_output_file(self, dir_in, file_in, *, verbose = 0):
        '''
        Docstring for get_valid_output_file.
        '''
        ## preparation
        flag_increment = False   # set if incrementation attempt is to be attempted
        path_in = self.generate_full_path(dir_in, file_in)
        ## debug message
        if verbose >= 1:
            print("Verifying file:", path_in)

        ## Check if file already exists
        if not os.path.isfile(path_in):
            ## File does not exist; set new file name as-is
            if verbose >= 2:
                print("The file", path_in, "does not already exist.")
            file_new = file_in
        else:
            ## File already exists
            if verbose >= 1:
                print("The file", path_in, "already exists.")
            ## Check if user permission to increment is necessary
            if _FILEMGR_DEFAULTS_USER_INCREMENT:
                ## Ask for user input
                user_response = input("Attempt to increment? [Y/n] ")
                if user_response == "" or user_response.lower()[0] == "y":
                    ## User incrementation permitted
                    if verbose >= 3:
                        print("User permitted incrementation.")
                        flag_increment = True
                else:
                    ## User incrementation denied; fall back on auto incrementation default
                    if _FILEMGR_DEFAULTS_AUTO_INCREMENT:
                        ## Automatic incrementation enabled
                        if verbose >= 2:
                            print("Automatic incrementation enabled.")
                        flag_increment = True
                    else:
                        ## Incrementation to not be attempted; raise error as program execution cannot continue
                        raise RuntimeError("Could not get valid output file: filename incrementation denied.")

        ## Attempt to increment filename if required
        if flag_increment:
            if verbose >= 1:
                print("Attempting to increment file name...")
            n_incr_attempts = 0   # log number of attempts to prevent loop with no exit condition
            file_new = file_in    # update trial file name
            path_new = self.generate_full_path(dir_in, file_new)
            while os.path.isfile(path_new):
                if verbose >= 1:
                    print("File", path_new, "exists; incrementing...")
                ## increment filename
                file_new = self.increment_filename(file_new)
                ## update other values
                path_new = self.generate_full_path(dir_in, file_new)
                n_incr_attempts = n_incr_attempts + 1
                ## check if max number of attempts exceeded
                if n_incr_attempts > _FILEMGR_DEFAULTS_MAX_INCREMENTATION_ATTEMPTS:
                    raise RuntimeError("Maximum number of incrementation attempts reached:", _FILEMGR_DEFAULTS_MAX_INCREMENTATION_ATTEMPTS)
            ##

        ## Return new file name (can be unchanged)
        path_new = self.generate_full_path(dir_in, file_new)
        if verbose >= 2:
            print("The file", path_new, "is a valid output file.")
        return file_new

    def increment_filename(self, fname_in):
        '''
        Attempt to increment a filename by increasing a sequential id integer at the end of the filename string by 1, and returning the new filename.
        '''
        ## split the file name into a head and sequential id
        fname_split = re.split(r'(\d+$)', fname_in)    # split by int searching from back
        if len(fname_split) < 2:                         # could not split properly
            raise RuntimeError("Could not identify sequential ID in filename:", fname_in)
        fname_head = fname_split[0]
        fname_id = fname_split[1]

        ## increment the id
        new_id = self.increment_string(fname_id)

        ## put path back together
        new_fname = "".join([fname_head, new_id])

        return new_fname

    def increment_string(self, str_in):
        '''
        Increment a string, preserving leading zeros.

        eg "00567" -> "00568"
        '''
        return str(int(str_in)+1).zfill(len(str_in))


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
