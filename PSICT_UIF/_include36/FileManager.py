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
    Stores and handles the paths and names of files associated with a PSICT-initialised Labber experiment.

    Includes methods to set (either manually or through defaults in the _FileManager_rc file) the script-specific rcfile and the Labber executable path. In addition, stores and handles the paths and filenames of the template, reference, and output database files. The resource database file is a temporary copy of the template file, where the hdf5 entries are directly modified by the PSICT-UIF package, and is deleted after the script has been run.
    '''

    def __init__(self, *, verbose = 1):
        ## Set object log level
        self.verbose = verbose
        ## Set values of attributes constant across multiple methods
        self._REF_COPY_POSTFIX = _rc.REF_COPY_POSTFIX
        ## Set Labber exe path to system default - can be overwritten by user in external script later
        self.setdef_labber_exe_path(verbose = self.verbose)
        ## Status message
        if self.verbose >= 4:
            print("Called FileManager constructor.")

    def __del__(self):
        ## Status message
        if self.verbose >= 4:
            print("Calling FileManager destructor.")
        ## Delete reference file (temporary copy of template file)
        self.clean_reference_file(verbose = self.verbose)
        ## Status message
        if self.verbose >= 4:
            print("FileManager destructor finished.")

    def set_original_wd(self, original_wd, script_inv):
        '''
        Store the original working directory (original_wd) and sys.argv[0] script invocation (script_inv).

        These are necessary for copying scripts etc. correctly in full generality.
        '''
        self._original_wd = original_wd
        self._script_inv = script_inv

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Config/rcfile methods

    def set_script_copy_target_dir(self, script_copy_target_dir):
        '''
        Assign the target directory to which the script will be copied.
        '''
        self._script_copy_target_dir = os.path.normpath(script_copy_target_dir)

    def assign_script_rcmodule(self, rcmodule, rcpath):
        '''
        Assign the passed script rcmodule (already-imported rcfile) to the FileManager object.
        '''
        self._script_rc = rcmodule
        self._script_rcpath = rcpath

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Labber executable methods

    def set_labber_exe_path(self, new_labber_exe_path, *, verbose = 1):
        '''
        Set the Labber executable path stored in the FileManager object.

        Note that the path will only be applied immediately before the measurement is performed; validity checks are not carried out!
        '''
        ## Normalize path
        new_labber_exe_path = os.path.normpath(new_labber_exe_path)
        ## Status message
        if verbose >= 2:
            print("New Labber executable path:", new_labber_exe_path)
        ## Change attribute
        self.labber_exe_path = new_labber_exe_path
        ## Status message
        if verbose >= 2:
            print("New Labber executable path set.")

    def setdef_labber_exe_path(self, *, verbose = 1):
        '''
        Set the Labber executable path as the system default (os-sensitive).

        Currently supports Windows and Darwin (macOS); other operating systems will raise a RuntimeError.
        '''
        ## Status message
        if verbose >= 2:
            print("Setting Labber executable path spec to system default...")
        ## Check os
        _SYSTEM = platform.system()
        if _SYSTEM == "Windows":  # Windows
            if verbose >= 3:
                print("System identified as Windows; default executable path is", _rc.EXE_PATH_WIN)
            _SYSDEF_LABBER_EXE_PATH = _rc.EXE_PATH_WIN
        elif _SYSTEM == "Darwin": # macOS
            if verbose >= 3:
                print("System identified as macOS; default executable path is", _rc.EXE_PATH_MAC)
            _SYSDEF_LABBER_EXE_PATH = _rc.EXE_PATH_MAC
        else:                     # Other OSes are currently not supported
            raise RuntimeError("System could not be identified, or is not supported.\nplatform.system() returned:", _SYSTEM)
        ## Change path stored in FileManager attributes
        self.set_labber_exe_path(_SYSDEF_LABBER_EXE_PATH, verbose = verbose)
        ## Status message
        if verbose >= 2:
            print("Labber executable path spec set to system default.")

    def apply_labber_exe_path(self, *, verbose = 1):
        '''
        Apply the Labber executable path stored in the FileManager object attributes to ScriptTools, ie "set" externally.

        NB: This method should not be used explicitly in the external script; it will be called as part of measurement pre-processing anyway.
        '''
        ## Status message
        if verbose >= 2:
            print("Applying Labber executable path...")
        ## Set ScriptTools path
        ScriptTools.setExePath(self.labber_exe_path)
        ## Status message
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

    def set_template_file(self, template_dir, template_file, *, verbose = 1):
        '''
        Set the template database file.

        This template file will never be modified by PSICT. Where it is necessary to edit the hdf5 files directly (eg setting channel relations), such edits will be applied to the temporary copy (the "reference file").
        '''
        ## Status message
        if verbose >= 1:
            print("Setting template file...")
        ## Set attributes
        self.template_dir = os.path.expanduser(os.path.normpath(template_dir))
        self.template_file = template_file
        self.template_path = self.generate_full_path(self.template_dir, self.template_file)
        ## Status message
        if verbose >= 1:
            print("Template file set as:", self.template_path)
        ## Copy template file to create reference file
        self.copy_reference_file(verbose = verbose)

    def copy_reference_file(self, *, verbose = 1):
        '''
        Copies the template file into a temporary reference file.

        The temporary reference file will have all direct hdf5 edits applied to it, and the measurement will be run from it as well.
        '''
        ## Status message
        if verbose >= 3:
            print("Copying reference file...")
        ## Set reference file target names
        try:
            self.reference_dir = self.template_dir
            self.reference_file = "".join([self.template_file, self._REF_COPY_POSTFIX])
        except AttributeError:
            raise RuntimeError("The template directory and/or filename have not been specified.")
        self.reference_path = self.generate_full_path(self.reference_dir, self.reference_file)
        ## Copy file
        shutil.copy(self.template_path, self.reference_path)
        ## Status message
        if verbose >= 3:
            print("Reference file copied successfully:", self.reference_path)


    def clean_reference_file(self, *, verbose = 1):
        '''
        Clean up the temporary reference file (ie delete it).
        '''
        ## Status message
        if verbose >= 3:
            print("Deleting temporary copy of reference file...")
        ## Delete temporary copy of reference file
        try:
            os.remove(self.reference_path)
        except (AttributeError, FileNotFoundError):
            pass
        else:
            ## Status message
            if verbose >= 3:
                print("Deleted reference file", self.reference_path)


    ## Output file methods

    def set_output_file(self, output_dir, output_file, *, verbose = 1):
        '''
        Set the output file for the measurement.

        A check will be carried out to ensure that the output file does not already exist. If it does, the FileManager rc parameters will determine which combination of user input and/or silent default will decide whether or not to attempt a file name incrementation.
         - If allowed, this will attempt to increment the last valid integer string appearing in the file name, eg "myfile_034" -> "myfile_035".
         - If disallowed, or if allowed and unable to parse a sequential integer from the file name, a RuntimeError will be raised.
        Basically, the PSICT-UIF will never overwrite an existing output file.
        '''
        ## Status message
        if verbose >= 2:
            print("Setting output file...")
        ## Set output dir (will not change)
        self.output_dir = os.path.abspath(os.path.normpath(output_dir))
        ## Create output dir if it does not exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        ## Get valid output filename, checking for existence, incrementing if nececssary, etc
        valid_output_file = self.get_valid_output_file(self.output_dir, output_file, verbose = verbose)
        ## Set attributes
        self.output_file = valid_output_file
        self.output_path = self.generate_full_path(self.output_dir, self.output_file)
        ## Status message
        if verbose == 1:
            print("Output file:", self.output_file)
        elif verbose >= 1:
            print("Output file set as:", self.output_path)


    def get_valid_output_file(self, dir_in, file_in, *, verbose = 1):
        '''
        Return the name of a valid output file.

        If the specified file does not already exist, it will be returned as-is. If the file already exists, incrementation of the file name (see the FileManager.increment_filename method) will be attempted. If this cannot be done, a RuntimeError will be raised.
        '''
        ## preparation
        flag_increment = False   # set if incrementation attempt is to be attempted
        path_in = self.generate_full_path(dir_in, file_in)
        file_new = file_in
        ## Status message
        if verbose >= 2:
            print("Verifying output file:", path_in)

        ## Check if file already exists
        if not os.path.isfile(path_in):
            ## File does not exist; set new file name as-is
            if verbose >= 2:
                print("The file", path_in, "does not already exist.")
            ## Keep going past incrementation, return as-is
        else:
            ## File already exists
            if verbose >= 2:
                print("The file", path_in, "already exists.")
            ## Check if user permission to increment is necessary
            if self._script_rc.outfile_iter_automatic:
                ## Check if incrementation is set to be automatic
                if verbose >= 2:
                    print("Automatic incrementation enabled.")
                flag_increment = True
            elif self._script_rc.outfile_iter_user_check:
                ## Ask for user input
                user_response = input("Attempt to increment? [Y/n] ")
                if user_response == "" or user_response.lower()[0] == "y":
                    ## User incrementation permitted
                    if verbose >= 3:
                        print("User permitted incrementation.")
                    flag_increment = True
            else:
                ## Incrementation to not be attempted; raise error as program execution cannot continue
                raise RuntimeError("Could not get valid output file: filename incrementation denied.")

        ## Attempt to increment filename if required
        if flag_increment:
            if verbose >= 2:
                print("Attempting to increment file name...")
            n_incr_attempts = 0   # log number of attempts to prevent loop with no exit condition
            path_new = self.generate_full_path(dir_in, file_new)
            while os.path.isfile(path_new):
                if verbose >= 2:
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
        ## Status message
        if verbose >= 2:
            print("The file", path_new, "is a valid output file.")
        return file_new

    def increment_filename(self, fname_in):
        '''
        Attempt to increment a filename by increasing a sequential id integer at the end of the filename string by 1, and returning the new filename.
        '''
        ## Split the file name into a head and sequential id
        fname_split = re.split(r'(\d+$)', fname_in)    # split by int searching from back
        if len(fname_split) < 2:                         # could not split properly
            raise RuntimeError("Could not identify sequential ID in filename:", fname_in)
        fname_head = fname_split[0]
        fname_id = fname_split[1]
        ## Increment the id
        new_id = self.increment_string(fname_id)
        ## Put path back together
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

    def set_slave_status(self, is_slave, *, verbose = 1):
        '''
        Set whether or not the script is running as a slave (ie not a standalone).

        Affects whether or not the integrated script copying methods are invoked.
        '''
        self._is_slave = is_slave
        if verbose >= 2:
            print('Slave status set to:', self._is_slave)

    def pre_measurement_copy(self, *, verbose = 1):
        '''
        Copies files associated with the measurement to a target folder for reproducability/storage.

        Which files are copied, and if any special rules such as renaming to match the measurement file name are applied, are determined
        by the flags and parameters in the config file (previously, the script-rcfile).
        '''
        ## Check if script copying is enabled in script-rcfile
        if self._script_rc.script_copy_enabled:
            if self._is_slave:
                if verbose >= 2:
                    print('Script copying through the PSICT-UIF is disabled when the script is run as a slave.')
            else: # Script copying is enabled and the script is running as a standalone
                if verbose >= 2:
                    print("Copying script and additional files...")
                ## Check if target directory has been specified
                try:
                    assert self._script_copy_target_dir
                except AssertionError:
                    raise RuntimeError('The script copy target directory has not been specified.')
                ## Create target dir if it does not already exist
                if verbose >= 3:
                    print("Creating target directory (if it does not exist)...")
                pathlib.Path(self._script_copy_target_dir).mkdir(parents = True, exist_ok = True)
                script_target_dir = self._script_copy_target_dir  # will have custom filename appended if necessary
                ## Set target file names (eg renaming to match output file)
                if verbose >= 3:
                    print("Setting new filenames...")
                target_file = "".join([self.output_file, self._script_rc.script_copy_postfix, ".", _rc.SCRIPT_COPY_EXTENSION])
                if verbose >= 2:
                    print("The target file name is", target_file)
                ## Append name to script target path
                script_target_path = os.path.abspath(os.path.join(script_target_dir, target_file))
                ## Copy external script (the one which runs the whole thing)
                script_path_original = os.path.join(self._original_wd, self._script_inv)
                if verbose >= 3:
                    print("The original script is at", script_path_original)
                script_path_new = shutil.copy(script_path_original, script_target_path)
                if verbose >= 3:
                    print("The script file has been copied to", script_path_new)
        else:
            ## Copying script not enabled
            if verbose >= 2:
                print("Script copying has been disabled in the PSICT config file.")
        ##

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
