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
import logging

from Labber import ScriptTools

import PSICT_UIF._include36._FileManager_rc as _rc
import PSICT_UIF._include36._LogLevels as LogLevels

class FileManager:
    '''
    Stores and handles the paths and names of files associated with a PSICT-initialised Labber experiment.

    Includes methods to set (either manually or through defaults in the _FileManager_rc file) the script-specific rcfile and the Labber executable path. In addition, stores and handles the paths and filenames of the template, reference, and output database files. The resource database file is a temporary copy of the template file, where the hdf5 entries are directly modified by the PSICT-UIF package, and is deleted after the script has been run.
    '''

    def __init__(self, *, parent_logger_name = None):
        ## Logging
        if parent_logger_name is not None:
            logger_name = '.'.join([parent_logger_name, 'FileManager'])
        else:
            logger_name = 'FileManager'
        self.logger = logging.getLogger(logger_name)
        ## Set values of attributes constant across multiple methods
        self._REF_COPY_POSTFIX = _rc.REF_COPY_POSTFIX
        ## Set Labber exe path to system default - can be overwritten by user in external script later
        self.setdef_labber_exe_path()
        ## Status message
        self.logger.debug('FileManager instance initialized.')

    def __del__(self):
        ## Delete reference file (temporary copy of template file)
        self.clean_reference_file()
        ## Status message
        self.logger.debug('FileManager instance deleted.')

    def set_original_wd(self, original_wd, script_inv):
        '''
        Store the original working directory (original_wd) and sys.argv[0] script invocation (script_inv).

        These are necessary for copying scripts etc. correctly in full generality.
        '''
        self.logger.debug('Setting original wd and script inv...')
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
        self.logger.debug('Script rcmodule and rcpath assigned to FileManager instance.')

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Labber executable methods

    def set_labber_exe_path(self, new_labber_exe_path):
        '''
        Set the Labber executable path stored in the FileManager object.

        Note that the path will only be applied immediately before the measurement is performed; validity checks are not carried out!
        '''
        ## Normalize path
        new_labber_exe_path = os.path.normpath(new_labber_exe_path)
        ## Status message
        self.logger.debug("Setting new Labber executable path: {}".format(new_labber_exe_path))
        ## Change attribute
        self.labber_exe_path = new_labber_exe_path

    def setdef_labber_exe_path(self):
        '''
        Set the Labber executable path as the system default (os-sensitive).

        Currently supports Windows and Darwin (macOS); other operating systems will raise a RuntimeError.
        '''
        ## Status message
        self.logger.debug("Setting Labber executable path spec to system default...")
        ## Check os
        _SYSTEM = platform.system()
        if _SYSTEM == "Windows":  # Windows
            self.logger.debug("System identified as Windows; "+\
                              "default executable path is {}".format(_rc.EXE_PATH_WIN))
            _SYSDEF_LABBER_EXE_PATH = _rc.EXE_PATH_WIN
        elif _SYSTEM == "Darwin": # macOS
            self.logger.debug("System identified as macOS; "\
                             +"default executable path is".format(_rc.EXE_PATH_MAC))
            _SYSDEF_LABBER_EXE_PATH = _rc.EXE_PATH_MAC
        else:                     # Other OSes are currently not supported
            raise RuntimeError("System could not be identified, or is not supported.\nplatform.system() returned: {}".format(_SYSTEM))
        ## Change path stored in FileManager attributes
        self.set_labber_exe_path(_SYSDEF_LABBER_EXE_PATH)
        ## Status message
        self.logger.debug("Labber executable path spec set to system default.")

    def apply_labber_exe_path(self):
        '''
        Apply the Labber executable path stored in the FileManager object attributes to ScriptTools, ie "set" externally.

        NB: This method should not be used explicitly in the external script; it will be called as part of measurement pre-processing anyway.
        '''
        self.logger.debug("Setting Labber executable path through ScriptTools...")
        ## Set ScriptTools path
        ScriptTools.setExePath(self.labber_exe_path)
        ## Status message
        self.logger.debug("Labber executable path set through ScriptTools.")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    ## Database file methods

    def generate_full_path(self, dir_name, file_name, file_extension = _rc.FILE_DATABASE_EXT):
        '''
        Generate the full path to a file of the specified directory, file name, and extension.

        The value of FILE_DATABASE_EXT in the _FileManager_rc file is used as the default extension.
        '''
        return os.path.join(dir_name, "".join([file_name, ".", file_extension]))

    ## Template and reference file methods

    def set_template_file(self, template_dir, template_file):
        '''
        Set the template database file.

        This template file will never be modified by PSICT. Where it is necessary to edit the hdf5 files directly (eg setting channel relations), such edits will be applied to the temporary copy (the "reference file").
        '''
        self.logger.debug("Setting template file...")
        ## Set attributes
        self.template_dir = os.path.expanduser(os.path.normpath(template_dir))
        self.template_file = template_file
        self.template_path = self.generate_full_path(self.template_dir, self.template_file)
        ## Status message
        self.logger.info("Template file set as: {}".format(self.template_path))
        ## Copy template file to create reference file
        self.copy_reference_file()
        self.logger.debug('Template file copied to temporary reference file.')

    def copy_reference_file(self):
        '''
        Copies the template file into a temporary reference file.

        The temporary reference file will have all direct hdf5 edits applied to it, and the measurement will be run from it as well.
        '''
        self.logger.debug("Copying reference file...")
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
        self.logger.debug("Reference file copied successfully: {}".format(self.reference_path))


    def clean_reference_file(self):
        '''
        Clean up the temporary reference file (ie delete it).
        '''
        self.logger.debug("Deleting temporary reference file...")
        ## Delete temporary copy of reference file
        try:
            os.remove(self.reference_path)
        except (AttributeError, FileNotFoundError):
            ## Log but do nothing
            self.logger.warning('Reference file {} not found!'.format(self.reference_path))
            pass
        else:
            self.logger.debug("Deleted reference file {}".format(self.reference_path))


    ## Output file methods

    def set_output_file(self, output_dir, output_file):
        '''
        Set the output file for the measurement.

        A check will be carried out to ensure that the output file does not already exist. If it does, the FileManager rc parameters will determine which combination of user input and/or silent default will decide whether or not to attempt a file name incrementation.
         - If allowed, this will attempt to increment the last valid integer string appearing in the file name, eg "myfile_034" -> "myfile_035".
         - If disallowed, or if allowed and unable to parse a sequential integer from the file name, a RuntimeError will be raised.
        Basically, the PSICT-UIF will never overwrite an existing output file.
        '''
        self.logger.debug("Setting output file...")
        ## Set output dir (will not change)
        self.output_dir = os.path.abspath(os.path.normpath(output_dir))
        ## Create output dir if it does not exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        ## Get valid output filename, checking for existence, incrementing if nececssary, etc
        valid_output_file = self.get_valid_output_file(self.output_dir, output_file)
        ## Set attributes
        self.output_file = valid_output_file
        self.output_path = self.generate_full_path(self.output_dir, self.output_file)
        ## Status message
        self.logger.log(LogLevels.SPECIAL, "Output file: {}".format(self.output_file))
        self.logger.debug("Full output path: {}".format(self.output_path))


    def get_valid_output_file(self, dir_in, file_in):
        '''
        Return the name of a valid output file.

        If the specified file does not already exist, it will be returned as-is. If the file already exists, incrementation of the file name (see the FileManager.increment_filename method) will be attempted. If this cannot be done, a RuntimeError will be raised.
        '''
        ## preparation
        flag_increment = False   # set if incrementation attempt is to be attempted
        path_in = self.generate_full_path(dir_in, file_in)
        file_new = file_in
        ## Status message
        self.logger.debug("Verifying output file: {}".format(path_in))

        ## Check if file already exists
        if not os.path.isfile(path_in):
            ## File does not exist; set new file name as-is
            self.logger.debug("The file {} does not already exist.".format(path_in))
            ## Keep going past incrementation, return as-is
        else:
            ## File already exists
            self.logger.debug("The file {} already exists.".format(path_in))
            ## Check if user permission to increment is necessary
            if self._script_rc.outfile_iter_automatic:
                ## Check if incrementation is set to be automatic
                self.logger.debug("Automatic incrementation enabled.")
                flag_increment = True
            elif self._script_rc.outfile_iter_user_check:
                ## Ask for user input
                user_response = input("Attempt to increment? [Y/n] ")
                if user_response == "" or user_response.lower()[0] == "y":
                    ## User incrementation permitted
                    self.logger.info("User permitted incrementation.")
                    flag_increment = True
            else:
                ## Incrementation to not be attempted; raise error as program execution cannot continue
                raise RuntimeError("Could not get valid output file: filename incrementation denied.")

        ## Attempt to increment filename if required
        if flag_increment:
            self.logger.debug("Attempting to increment file name...")
            n_incr_attempts = 0   # log number of attempts to prevent loop with no exit condition
            path_new = self.generate_full_path(dir_in, file_new)
            while os.path.isfile(path_new):
                self.logger.debug("File {} exists; incrementing...".format(path_new))
                ## increment filename
                file_new = self.increment_filename(file_new)
                ## update other values
                path_new = self.generate_full_path(dir_in, file_new)
                n_incr_attempts = n_incr_attempts + 1
                ## check if max number of attempts exceeded
                if n_incr_attempts > _rc.INCREMENT_MAX_ATTEMPTS:
                    raise RuntimeError("Maximum number of incrementation attempts reached: {}"\
                                        .format(_rc.INCREMENT_MAX_ATTEMPTS))
            ##

        ## Return new file name (can be unchanged)
        path_new = self.generate_full_path(dir_in, file_new)
        ## Status message
        self.logger.debug("The file {} is a valid output file.".format(path_new))
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

    def set_slave_status(self, is_slave):
        '''
        Set whether or not the script is running as a slave (ie not a standalone).

        Affects whether or not the integrated script copying methods are invoked.
        '''
        self._is_slave = is_slave
        self.logger.debug('Slave status set to: {}'.format(self._is_slave))

    def pre_measurement_copy(self):
        '''
        Copies files associated with the measurement to a target folder for reproducability/storage.

        Which files are copied, and if any special rules such as renaming to match the measurement file name are applied, are determined
        by the flags and parameters in the config file (previously, the script-rcfile).
        '''
        ## Check if script copying is enabled in script-rcfile
        if self._script_rc.script_copy_enabled:
            if self._is_slave:
                self.logger.debug('Script copying through the PSICT-UIF is disabled when the script is run as a slave.')
            else: # Script copying is enabled and the script is running as a standalone
                self.logger.debug("Copying script and additional files...")
                ## Check if target directory has been specified
                try:
                    assert self._script_copy_target_dir
                except AssertionError:
                    raise RuntimeError('The script copy target directory has not been specified.')
                ## Create target dir if it does not already exist
                self.logger.debug("Creating target directory (if it does not exist)...")
                pathlib.Path(self._script_copy_target_dir).mkdir(parents = True, exist_ok = True)
                script_target_dir = self._script_copy_target_dir  # will have custom filename appended if necessary
                ## Set target file names (eg renaming to match output file)
                self.logger.debug("Setting new filenames...")
                target_file = "".join([self.output_file, self._script_rc.script_copy_postfix, ".", _rc.SCRIPT_COPY_EXTENSION])
                self.logger.debug("Target file name is: {}".format(target_file))
                ## Append name to script target path
                script_target_path = os.path.abspath(os.path.join(script_target_dir, target_file))
                ## Copy external script (the one which runs the whole thing)
                script_path_original = os.path.join(self._original_wd, self._script_inv)
                self.logger.debug("Original script is: {}".format(script_path_original))
                script_path_new = shutil.copy(script_path_original, script_target_path)
                self.logger.debug("Script file copied to: {}".format(script_path_new))
        else:
            ## Copying script not enabled
            self.logger.warning("Script copying has been disabled in the PSICT config file.")
        ##

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
