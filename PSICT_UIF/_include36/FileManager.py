## The PSICT-UIF file manager class
##  Handles all file names and paths, including creation and deletion
##  of temporary files.

import platform
import os

from Labber import ScriptTools

from PSICT_UIF._include36._FileManager_rc import (_FILEMGR_LABBER_EXE_PATH_MAC_DEFAULT, \
                                                  _FILEMGR_LABBER_EXE_PATH_WIN_DEFAULT, \
                                                  _FILEMGR_DEFAULTS_FILE_EXTENSION, \
                                                  _FILEMGR_DEFAULTS_COPY_POSTFIX, \
                                                 )


class FileManager:
    '''
    Docstring for FileManager.
    '''

    def __init__(self, *, verbose = 0):
        ## set object log level
        self.verbose = verbose
        ## set Labber exe path to system default
        self.setdef_labber_exe_path(verbose = self.verbose)
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

    def set_template_file(self, template_dir, template_file, *, verbose = 0):
        '''
        Docstring for set_template_file.
        '''
        ## debug message
        if verbose >= 2:
            print("Setting template file...")
        ## Set attributes
        self.template_dir = os.path.normpath(template_dir)
        self.template_file = template_file
        self.template_path = self.generate_full_path(self.template_dir, self.template_file)
        ## Copy template file to create reference file
        #### TODO
        ## debug message
        if verbose >= 1:
            print("Template file set as:", self.template_path)

    def set_output_file(self, output_dir, output_file, *, verbose = 0):
        '''
        Docstring for set_output_file.
        '''
        ## debug message
        if verbose >= 2:
            print("Setting output file...")
        ## Set attributes
        self.output_dir = os.path.normpath(output_dir)
        self.output_file = output_file
        self.output_path = self.generate_full_path(self.output_dir, self.output_file)
        ## debug message
        if verbose >= 1:
            print("Output file set as:", self.output_path)


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
