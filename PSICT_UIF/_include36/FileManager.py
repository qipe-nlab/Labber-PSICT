## The PSICT-UIF file manager class
##  Handles all file names and paths, including creation and deletion
##  of temporary files.

import platform
import os
import re
import shutil
import sys
import inspect
import pathlib

from Labber import ScriptTools

import PSICT_UIF._include36._FileManager_rc as _rc


class FileManager:
    '''
    A class to store and handle the paths and names of files associated with a PSICT-initialised Labber experiment.

    Includes methods to set (either manually or through defaults in the _FileManager_rc file) the script-specific rcfile and the Labber executable path. In addition, stores and handles the paths and filenames of the template, reference, and output database files; the resource database file is a temporary copy of the template file, where the hdf5 entries are directly modified by the PSICT-UIF package, and is deleted after the script has been run.

    '''

    def __init__(self, *, verbose = 0):
        ## set object log level
        self.verbose = verbose
        ## set values of attributes constant across multiple methods
        self._REF_COPY_POSTFIX = _rc.SCRIPT_COPY_POSTFIX
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
    ## rcfile methods

    def assign_script_rcmodule(self, rcmodule, rcpath):
        '''
        Assign the passed script rcmodule (already-imported rcfile) to the FileManager object.
        '''
        self._script_rc = rcmodule
        self._script_rcpath = rcpath

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
                print("System identified as Windows; default executable path is", _rc.EXE_PATH_WIN)
            _SYSDEF_LABBER_EXE_PATH = _rc.EXE_PATH_WIN
        elif _SYSTEM == "Darwin":
            if verbose >= 3:
                print("System identified as macOS; default executable path is", _rc.EXE_PATH_MAC)
            _SYSDEF_LABBER_EXE_PATH = _rc.EXE_PATH_MAC
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

    def generate_full_path(self, dir_name, file_name, file_extension = _rc.FILE_DATABASE_EXT):
        '''
        Generate the full path to a file of the specified directory, file name, and extension.

        The value of FILE_DATABASE_EXT in the _FileManager_rc file is used as the default extension.
        '''
        return os.path.join(dir_name, "".join([file_name, ".", file_extension]))

    ## Template and reference file methods

    def set_template_file(self, template_dir, template_file, *, verbose = 0):
        '''
        Set the template database file.

        Note that the FileManager will make a temporary copy of this, which will be the "working" reference file, to make direct hdf5 edits, and so the template file will not be modified.
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
        Copies the template file into a temporary reference file, where direct hdf5 edits will be carried out.
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
        Clean up the temporary reference file (ie delete it).
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
        Set the output file for the measurement.

        A check will be carried out to ensure that the output file does not already exist. If it does, the FileManager rc parameters will determine which combination of user input and/or silent default will decide whether or not to attempt a file name incrementation.
         - If allowed, this will attempt to increment the last valid integer string appearing in the file name, eg "myfile_034" -> "myfile_035".
         - If disallowed, or if allowed and unable to parse a sequential integer from the file name, a RuntimeError will be raised.
        Basically, the PSICT-UIF will never overwrite an existing output file.
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
        Return the name of a valid output file (ie not existent through incrementation of the passed-in filename).

        If this cannot be done, will raise a RuntimeError.
        '''
        ## preparation
        flag_increment = False   # set if incrementation attempt is to be attempted
        path_in = self.generate_full_path(dir_in, file_in)
        file_new = file_in
        ## debug message
        if verbose >= 1:
            print("Verifying output file:", path_in)

        ## Check if file already exists
        if not os.path.isfile(path_in):
            ## File does not exist; set new file name as-is
            if verbose >= 2:
                print("The file", path_in, "does not already exist.")
            ## Keep going past incrementation, return as-is
        else:
            ## File already exists
            if verbose >= 1:
                print("The file", path_in, "already exists.")
            ## Check if user permission to increment is necessary
            if _rc.INCREMENT_ASK_USER:
                ## Ask for user input
                user_response = input("Attempt to increment? [Y/n] ")
                if user_response == "" or user_response.lower()[0] == "y":
                    ## User incrementation permitted
                    if verbose >= 3:
                        print("User permitted incrementation.")
                    flag_increment = True
                else:
                    ## User incrementation denied; fall back on auto incrementation default
                    if _rc.INCREMENT_AUTO:
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
                if n_incr_attempts > _rc.INCREMENT_MAX_ATTEMPTS:
                    raise RuntimeError("Maximum number of incrementation attempts reached:", _rc.INCREMENT_MAX_ATTEMPTS)
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
    ## Post-measurement methods

    def post_measurement_copy(self, *, verbose = 0):
        '''
        Docstring
        '''
        ## Check if script copying is enabled in script-rcfile
        if self._script_rc.script_copy_enabled:
            if verbose >= 1:
                print("Copying script and additional files...")
            ## Create target dir if it does not already exist
            if verbose >= 3:
                print("Creating target directory (if it does not exist)...")
            pathlib.Path(self._script_rc.script_copy_target_dir).mkdir(parents = True, exist_ok = True)
            script_target_path = self._script_rc.script_copy_target_dir  # will have custom filename appended if necessary
            target_path = self._script_rc.script_copy_target_dir         # path used for additional files
            ## Set target file names (eg renaming to match output file)
            if verbose >= 3:
                print("Setting new filenames...")
            if self._script_rc.script_copy_matches_output:
                target_file = "".join([self.output_file, self._script_rc.script_copy_postfix, ".", _rc.SCRIPT_COPY_EXTENSION])
                print("The target file name is", target_file)
                ## Append name to script target path
                script_target_path = os.path.join(script_target_path, target_file)
            ## Add additional paths as specified in script-rcfile
            additional_paths = []
            if self._script_rc.script_rc_copy_enabled:
                additional_paths.append(self._script_rcpath)
            ## Copy external script (the one which runs the whole thing)
            script_path_original = os.path.abspath(os.path.basename(inspect.stack()[-1][1]))
            if verbose >= 3:
                print("The original script is at", script_path_original)
            script_path_new = shutil.copy(script_path_original, script_target_path)
            if verbose >= 3:
                print("The script file has been copied to", script_path_new)
            ## Copy additional files as passed to method, eg script-rc
            for add_path in additional_paths:
                add_path_new = shutil.copy(add_path, target_path)
                if verbose >= 3:
                    print("An additional file has been copied to", add_path_new)
        else:
            ## Copying script not enabled
            if verbose >= 1:
                print("Script copying has been disabled in the script-rcfile.")
        ##

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
