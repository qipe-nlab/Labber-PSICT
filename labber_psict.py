### String input parser for Labber pulse sequences
## Author:         Sam Wolski
## Date created:  2018/04/13

import os               # for checking if output file exists in InputStrParser.set_MeasurementObject
import sys              # for sys.exit
import re               # for filename parsing for sequential incrementation
import h5py             # for direct editing of hdf5 files to modify iteration parameter order
import numpy as np      # for working directly with h5py datasets
import shutil           # for manipulating copies of the input reference config file

###############################################################################
## Labber-PSICT general information
PSICT_VERSION = "0.1.0 (alpha)"
print("Labber-PSICT version is", PSICT_VERSION)

###############################################################################

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
## Configs for admissible parameter input values.

params_main_config = {
        "sr":     float,  # sample rate
        # "npts":   float,  # number of points - calculated from dead, sr, and pulse sequence
        "dead":   float,  # Dead time (relaxation of qubit after pulse sequence) in ns
        "delay":  float,  # first pulse delay in ns
        "trim":   int,    # Trim waveform to sequence (bool)
        "nout":   int,    # number of outputs
        "np":     int,    # number of pulses
        "ptype":  str,    # pulse type
        "tr":     int,    # truncation range
        "saz":    int,    # start at zero (bool)
        "e2e":    int,    # edge-to-edge pulses (bool)
        "epos":   int,    # edge position
        "SSB":    int,    # use SSB mixing (bool)
        "DRAG":   int,    # use DRAG (bool)
        ## these are 'main' parameters, but they are set per-pulse in post-processing:
        "IQ":     float,  # I/Q ratio
        "dphi":   float,  # Phase diff.
        ## IF/Control frequency specification
        # "cf":     float,  # Control frequency in MHz
        # "if":     float,  # IF frequency (to be modulated by Mod. freq) in MHz
    }

params_pulse_config = {
        "a":      float,  # Amplitude
        "w":      float,  # Width in ns
        "v":      float,  # Plateau in ns
        "s":      float,  # Spacing in ns
        "p":      float,  # Phase
        "f":      float,  # Mod. frequency (offset from IF frequency) in MHz
        "o":      str,    # Output
        "cf":     float,  # Control frequency in MHz
        "if":     float,  # IF frequency (to be modulated by Mod. freq) in MHz
    }

## dict for shortcode conversion
shortcodes = {
    ## main
    "sr":       "Sample rate",
    "npts":     "Number of points",
    "delay":    "First pulse delay",
    "trim":     "Trim waveform to sequence",
    "nout":     "Number of outputs",
    "np":       "# of pulses",
    "ptype":    "Pulse type",
    "tr":       "Truncation range",
    "saz":      "Start at zero",
    "e2e":      "Edge-to-edge pulses",
    "epos":     "Edge position",
    "SSB":      "Use SSB mixing",
    "DRAG":     "Use DRAG",
    ## additional
    "dead":     "Dead time",
    "cf":       "Control frequency",
    "if":       "IF frequency",
    ## pulse
    "a":        "Amplitude",
    "w":        "Width",
    "v":        "Plateau",
    "s":        "Spacing",
    "p":        "Phase",
    "f":        "Mod. frequency",
    "o":        "Output",
    ## main applied to pulses
    "IQ":       "Ratio I/Q",
    "dphi":     "Phase diff.",
}

## lists of shortcodes for sorting tests
add_shortcodes = ["dead"]
pulseapp_shortcodes = ["IQ", "dphi"]

## expansion of full parameter label from disparate input
def get_full_label(instrument_name, param_name, pulse_number = 0):
    '''
    Expand to the full parameter name from the instrument name, parameter name, and optional pulse number (for SQPG input).

    Passing the instrument name as "SQPG" or and empty string or None will default to the SQPG instrument.

    If the instrument is the SQPG, the parameter shortcode can be passed instead of the name. As usual, pulse_number = 0 denotes a main config parameter.
    '''
    ## convert SQPG names to appropriate string
    if instrument_name in [None, "", "SQPG"]:
        # print("-> Instrument is SQPG.")
        instrument_name = "Single-Qubit Pulse Generator"
    ## expand param shortcode if instrument is SQPG
    if (instrument_name == "Single-Qubit Pulse Generator") and (param_name in shortcodes):
        # print("Param name", param_name, "is in shortcodes.")
        param_name = shortcodes[param_name]
    ## concatenate string together based on pulse number
    if pulse_number == 0:
        label_string = "".join([instrument_name, " - ", param_name])
    else:
        label_string = "".join([instrument_name, " - ", param_name, " #", str(pulse_number)])
    return label_string

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

###############################################################################
## Conversions for nonstandard input types
##  eg To specify a channel name instead of the expected value (int), conversion
##  rules must be specified here.
##  NB Boolean values are converted using if ... else during post-processing

## main config
convert_nout = {1: 0, 2: 1, 3: 2, 4: 3}
convert_ptype = {"gauss": 0, "square": 1, "ramp": 2}
MAX_PULSES = 8         # maximum number of pulses supported by driver

## pulse config
convert_out = {"Readout": 0, "QubitControl": 1, "MagnonControl": 2, "Trigger": 3}
##      ## NB pulse output names cannot contain underscores (_) or spaces


###############################################################################


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
## post-processing functionality
def post_process_params_values(parserObj, in_main = [], in_pulses = [], verbose = False):
    '''
    Defines post-processing operations to be carried out on the raw input value of the specified parameter(s); these are carried out on the specified input parameters when the function is called.

    Dependencies are calculated based on stored values within the parserObj (InputStrParser instance). parserObj values are modified in-place; the function also returns the post-processed values of any parameters passed in (but _not_ their potential dependents!) such that this function can be used with iteration variables.

    Currently, any dependencies must be set explicitly in the InputStrParser parserObj (and are not read from the reference file). A warning or error will be raised (don't know which just yet...), and so this may cause undefined behaviour.

    Twofold main purpose:
        - Converts more descriptive strings (eg for output channel name)
            into integer switch values
        - Calculates parameters based on specified dependencies
            (eg pulse spacing as a function of pulse width)

    - out_main variable names (ie output) must match the variable names on the
        instrument as these will be passed directly to the Labber API
        updateValue methods.
    - Pulses should be referred to by their actual number (starting at 1, not 0).
    - This function should be called any time parameters are updated, eg setting iteration variables after main variables have already been set.
    '''
    if verbose: print("Beginning post-processing...")
    ## output dicts
    # out_main = {}
    # out_pulse = {}
    # out_add = {}     # additional parameters not passed directly to labber

    ## main values
    if "sr" in in_main:
        parserObj.main_values_out[shortcodes["sr"]] = in_main["sr"]
    # parserObj.main_values_out["Number of points"] = in_main["npts"]
    if "delay" in in_main:
        parserObj.main_values_out[shortcodes["delay"]] = in_main["delay"]*1e-9   # ns
    if "trim" in in_main:
        parserObj.main_values_out[shortcodes["trim"]] = 0 if in_main["trim"] == 0 else 1
    if "nout" in in_main:
        parserObj.main_values_out[shortcodes["nout"]] = convert_nout[in_main["nout"]]
    if "np" in in_main:
        parserObj.main_values_out[shortcodes["np"]] = in_main["np"] if in_main["np"] <= MAX_PULSES else MAX_PULSES
    if "ptype" in in_main:
        parserObj.main_values_out[shortcodes["ptype"]] = convert_ptype[in_main["ptype"]]
    if "tr" in in_main:
        parserObj.main_values_out[shortcodes["tr"]] = in_main["tr"]
    if "saz" in in_main:
        parserObj.main_values_out[shortcodes["saz"]] = 0 if in_main["saz"] == 0 else 1
    if "e2e" in in_main:
        parserObj.main_values_out[shortcodes["e2e"]] = 0 if in_main["e2e"] == 0 else 1
    if "epos" in in_main:
        parserObj.main_values_out[shortcodes["epos"]] = in_main["epos"]
    if "SSB" in in_main:
        parserObj.main_values_out[shortcodes["SSB"]] = 0 if in_main["SSB"] == 0 else 1
    if "DRAG" in in_main:
        parserObj.main_values_out[shortcodes["DRAG"]] = 0 if in_main["DRAG"] == 0 else 1
    ## additional data - not passed directly
    if "dead" in in_main:
        parserObj.add_values_out[shortcodes["dead"]] = in_main["dead"]*1e-9   # ns
    ## status print
    # if verbose:
        # print("(main) Sample rate:", parserObj.main_values_out["Sample rate"])
        # # print("(main) Number of points:", parserObj.main_values_out["Number of points"])
        # print("(main) First pulse delay:", parserObj.main_values_out["First pulse delay"])

    ## pulse values
    # npulses = len(in_pulse)
    # if verbose: print("(pulse) Number of pulses:", npulses)
    for pulse_num in in_pulses:
        # print(pulse_num)
        in_pulse = in_pulses[pulse_num]    # unpacks number, dict from list of lists

        # print(parserObj.pulse_values_out)
        ## init sub-dict for each pulse if nonexistent
        if not pulse_num in parserObj.pulse_values_out:
            parserObj.pulse_values_out[pulse_num] = {}

        if "a" in in_pulse:
            parserObj.pulse_values_out[pulse_num][shortcodes["a"]] = in_pulse["a"]
        if "w" in in_pulse:
            parserObj.pulse_values_out[pulse_num][shortcodes["w"]] = in_pulse["w"]*1e-9  # ns
        if "v" in in_pulse:
            parserObj.pulse_values_out[pulse_num][shortcodes["v"]] = in_pulse["v"]*1e-9  # ns
        if "s" in in_pulse:
            parserObj.pulse_values_out[pulse_num][shortcodes["s"]] = in_pulse["s"]*1e-9  # ns
        if "p" in in_pulse:
            parserObj.pulse_values_out[pulse_num][shortcodes["p"]] = in_pulse["p"]
        ## modulation frequency calculations: potential sideband switching
        if "cf" in in_pulse:
            parserObj.pulse_values_out[pulse_num][shortcodes["cf"]] = in_pulse["cf"]*1e6        # MHz
        if "if" in in_pulse:
            parserObj.pulse_values_out[pulse_num][shortcodes["if"]] = in_pulse["if"]*1e6             # MHz
        if "cf" in in_pulse and "if" in in_pulse:
            parserObj.pulse_values_out[pulse_num]["LO frequency"] = parserObj.pulse_values_out[pulse_num][shortcodes["cf"]] - parserObj.pulse_values_out[pulse_num][shortcodes["if"]]
        ## same sign => same sideband
        if "f" in in_pulse:
            freq_offset = in_pulse["f"]*1e6      # MHz
            if parserObj.pulse_values_out[pulse_num][shortcodes["if"]]*(parserObj.pulse_values_out[pulse_num]["IF frequency"] + freq_offset) >= 0:
                parserObj.pulse_values_out[pulse_num][shortcodes["f"]] = abs(parserObj.pulse_values_out[pulse_num]["IF frequency"] + freq_offset)
            ## sideband switching
            else:
                print("*** WARNING: Specified frequency offset induces a sideband switch for pulse ", pulse_num, "; defaulting to 0.", sep = "")
                parserObj.pulse_values_out[pulse_num][shortcodes["f"]] = abs(parserObj.pulse_values_out[pulse_num]["IF frequency"])
        ##
        if "o" in in_pulse:
            parserObj.pulse_values_out[pulse_num][shortcodes["o"]] = convert_out[in_pulse["o"]]
        ## overall parameters applied to pulses individually
        if "IQ" in in_main:
            parserObj.pulse_values_out[pulse_num][shortcodes["IQ"]] = in_main["IQ"]
        if "dphi" in in_main:
            parserObj.pulse_values_out[pulse_num][shortcodes["dphi"]] = in_main["dphi"]

        ## status print
        if verbose:
            print("(pulse)", pulse_num, "Amplitude:", parserObj.pulse_values_out[pulse_num]["Amplitude"])
            print("(pulse)", pulse_num, "Width:", parserObj.pulse_values_out[pulse_num]["Width"])
            print("(pulse)", pulse_num, "Plateau:", parserObj.pulse_values_out[pulse_num]["Plateau"])
            print("(pulse)", pulse_num, "Mod. Frequency:", parserObj.pulse_values_out[pulse_num]["Mod. frequency"])

    ##

    # # # # # # # # # # # # # # # # #
    ## Additional calculations

    ## Number of points from pulse sequence, dead time, and sample rate
    ##   Calculation depends on whether or not pulses are e2e
    if parserObj.main_values_out[shortcodes["e2e"]]:
        total_time = parserObj.main_values_out[shortcodes["delay"]] + sum([parserObj.pulse_values_out[xx][shortcodes["w"]] + \
                parserObj.pulse_values_out[xx][shortcodes["v"]] + parserObj.pulse_values_out[xx][shortcodes["s"]] for xx in range(1, parserObj.npulses+1)]) \
                + parserObj.add_values_out[shortcodes["dead"]]
    else:
        total_time = parserObj.main_values_out[shortcodes["delay"]] + sum([parserObj.pulse_values_out[xx][shortcodes["s"]] for xx in range(1, parserObj.npulses+1)]) + parserObj.add_values_out[shortcodes["dead"]]
    if verbose: print("Total time for pulse sequence (incl dead time):", str(total_time), "ns")
    parserObj.main_values_out["Number of points"] = int(parserObj.main_values_out[shortcodes["sr"]]*total_time)
    if verbose: print("Calculated number of points:", str(parserObj.main_values_out["Number of points"]))

    # # # # # # # # # # # # # # # # #


    ## complete debug printing
    if verbose:
        print("Main parameters:")
        print(parserObj.main_values_out)
        print("Pulse parameters:")
        print(parserObj.pulse_values_out)

    ## completion status message
    if verbose: print("Post-processing completed.")

    ## get return values corresponding to input params
    ## main - contains add
    out_main = {}
    for param_code in in_main:
        ## param is part of additional params
        if param_code in add_shortcodes:
            out_main[shortcodes[param_code]] = parserObj.add_values_out[shortcodes[param_code]]
        ## param is main but set for each pulse
        elif param_code in pulseapp_shortcodes:
            continue
        ## param is ordinary main param
        else:
            out_main[shortcodes[param_code]] = parserObj.main_values_out[shortcodes[param_code]]

    ## pulse
    out_pulse = {}
    # print(in_pulses)
    for pulse_num in in_pulses:
        in_pulse_data = in_pulses[pulse_num]
        pulse_dict = {}
        for param_code in in_pulse_data:
            pulse_dict[shortcodes[param_code]] = parserObj.pulse_values_out[pulse_num][shortcodes[param_code]]
        out_pulse[pulse_num] = pulse_dict

    ## output
    return out_main, out_pulse

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

###############################################################################

## output filepath-related constants and functions

REFERENCE_COPY_POSTFIX = "__copy"     # file name postfix used for denoting copy of template reference file
CONFIG_FILE_EXTENSION = "hdf5"        # file extension used for database files

def full_path(file_path, file_name, file_extension = CONFIG_FILE_EXTENSION):
    '''
    Generate a full path from a given file path, file name, and file extension.
    '''
    return os.path.join(file_path, "".join([file_name, ".", file_extension]))

def get_valid_out_fname(path_in, fname_in, user_input = True, default_attempt_increment = False, MAX_INCREMENT_ATTEMPTS = 1000, verbose = False):
    '''
    Get a "valid" output filepath (ie a log file that does not exist) based on the input filepath path_in. Returns None if a valid filepath cannot be obtained.

    First, the file extension is checked. As Labber will automatically append ".hdf5" if an otherwise-invalid extension is given, this would cause potential data appending if the input filename extension is not kosher. To rectify this, the extension file_ext (default ".hdf5") replaces the given extension if they are not already equal. (This is done before checking if the path points to an existing file)

    If path_in does not point to an existing file, the path is valid and so is returned as-is.

    If path_in points to an existing file,
        - setting the user_input flag will allow the user to decide whether or not to attempt to increment the filename, and
        - setting the default_attempt_increment flag will (if user_input is False) result in alwayus attempting to increment the filename.

    If possible, the filename increment is carried out using increment_filename(), and this is done repeatedly (up to MAX_INCREMENT_ATTEMPTS) until the filename is valid (the specified file does not exist) or the incrementing procedure fails for some reason.

    TODO: implement with proper exception handling at some stage.
    '''
    flag_increment = False       # set through args or input if incrementation attempt is desired
    file_in = full_path(path_in, fname_in)
    if verbose: print("Verifying file:", file_in)
    ## Check if file already exists
    if not os.path.isfile(file_in):
        ## file does not exist; set new fname to input fname as-is
        fname_new = fname_in
    else:
        ## file already exists
        if verbose: print("The file", file_in, "already exists.")
        if user_input:
            ## ask for user input about attempting increment
            print("The file", file_in, "already exists; attempt to increment?")
            user_response = input("[Y/n] ")
            if user_response == "" or user_response.lower()[0] == "y":
                ##
                if verbose: print("User permitted incrementation.")
                flag_increment = True
            else:
                ## user denied incrementation attempt; return None.
                print("User denied incrementation.")
                return None
        else:
            ## no user input - check for default incrementation attempt
            if default_attempt_increment:
                ## attempt incrementation by default
                print("Incrementing by default.")
                flag_increment = True
            else:
                ## do not attempt to increment; return None.
                return None
    ## attempt to increment the filename
    if flag_increment:
        if verbose: print("Attempting to increment file name...")
        n_attempts = 0
        fname_new = fname_in
        file_new = full_path(path_in, fname_new)
        while os.path.isfile(file_new):
            print("File", file_new, "exists; incrementing...")   # always prints; could be removed?
            try:
                ## TODO implement with proper exception handling
                fname_new = increment_filename(fname_new)
            except:
                ## could not increment path!
                if verbose: print("Could not increment filename", fname_new)
                return None
            finally:
                file_new = full_path(path_in, fname_new)
                n_attempts = n_attempts + 1
            if n_attempts > MAX_INCREMENT_ATTEMPTS:
                ## failure by number of attempts
                print("ERROR: number of attempts to increment is more than", MAX_INCREMENT_ATTEMPTS)
                return None

    ## return new path (can be same as old path)
    print("Output file set as:", file_new)
    return fname_new


def increment_filename(fname_in):
    '''
    Attempt to increment a filename by increasing a sequential id integer at the end of the filename string by 1, and returning the new filename.

    TODO: Implement with proper exception handling at some stage.
    '''
    ## split the file name into a head and sequential id
    fname_split = re.split(r'(\d+$)', fname_in)    # split by int searching from back
    if len(fname_split) < 2:                         # could not split properly - TODO exception handling...
        print("ERROR: Could not split filename according to sequential id!")
        return                                            # return none for error
    fname_head = fname_split[0]
    fname_id = fname_split[1]

    ## increment the id
    new_id = increment_string(fname_id)

    ## put path back together
    new_fname = "".join([fname_head, new_id])

    return new_fname

def increment_string(str_in):
    '''
    Increment a string, preserving leading zerosself.

    eg "00567" -> "00568"
    '''
    return str(int(str_in)+1).zfill(len(str_in))


##################

class FileManager:

    def __init__(self, reference_template_dir, reference_template_fname, output_dir, output_fname):
        ## parse input spec
        self.template_dir = reference_template_dir
        self.template_fname = reference_template_fname
        self.output_dir = output_dir
        self.output_fname = output_fname
        ## create full file path for template reference config file
        self.template_file = full_path(self.template_dir, self.template_fname)
        ## get valid output file and create full path
        self.output_fname = get_valid_out_fname(self.output_dir, self.output_fname)
        self.output_file = full_path(self.output_dir, self.output_fname)
        ## copy template file to reference copy (this will be used to eg set relations between parameters)
        self.reference_dir = self.template_dir
        self.reference_fname = None
        self.reference_file = None
        self.copy_reference_file()
        ## end

    def copy_reference_file(self, fname_postfix = REFERENCE_COPY_POSTFIX):
        '''
        Make a copy of the template file (with the addition of the file_postfix as an identifier).

        FileManager attributes are modified in-place.
        '''
        self.reference_fname = "".join([self.template_fname, fname_postfix])
        self.reference_file = full_path(self.reference_dir, self.reference_fname)
        shutil.copy(self.template_file, self.reference_file)

    def get_reference_file(self):
        '''
        Get the full filepath specification of the reference file.
        '''
        return self.reference_file

    def get_output_file(self):
        '''
        Get the full filepath specification of the output file.
        '''
        return self.output_file

    def clean(self):
        '''
        Clean up extraneous config files etc once all processing and measurements are complete. Also makes a copy of the script file for reference.

        TODO: proper error/exception handling.

        Potential TODO: can implement this as destructor method?
        '''
        ## Copy running script (the actual script with all the parameters and stuff)
        script_path = os.path.realpath(__file__)
        script_dest = os.path.join(self.output_dir, "".join([self.output_fname, "_script.py"]))
        shutil.copyfile(script_path, script_dest)
        ## Delete temporary reference config file
        if os.path.isfile(self.reference_file):
            os.remove(self.reference_file)
        else:
            print("*** ERROR: Could not find temporary reference file", self.reference_file, "to delete.")

###############################################################################

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

## Iteration-ordering-related functions for hdf5 direct editing

def swap_items_by_index(container, index_1, index_2):
    '''
    Swap two items in the container by specifying their indices.
    '''
    temp = container[index_1]
    container[index_1] = container[index_2]
    container[index_2] = temp

def sort_step_entries(fconfig, param_order):
     '''
     This is a docstring...
     '''
     index_counter = 0
     for param_name in param_order:
         ## generate list of param names in order they currently appear
         current_param_order = [xx[0] for xx in fconfig['Step list'].value]
         ## get index of desired param name in current order
         param_index = current_param_order.index(param_name)
         ## swap current param with that at index_counter
         swap_items_by_index(fconfig['Step list'], index_counter, param_index)
         ## increment index counter
         index_counter = index_counter + 1


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class InputStrParser:

    def __init__(self):
        ## config dicts to define parameter names and dtypes
        self.main_config = {}
        self.pulse_config = {}
        self.main_config_nparams = 0
        self.pulse_config_nparams = 0

        ## number of pulses
        self.npulses = 0

        ## containers for parameter input and output values
        self.main_values_in = {}
        self.pulse_values_in = {}
        self.main_values_out = {}
        self.pulse_values_out = {}
        self.add_values_out = {}    # additional parameters of interest not passed directly to Labber

        ## set main config dict (at beginning of this file)
        self.set_main_config(params_main_config)
        ## set pulse config dict (at beginning of this file)
        self.set_pulse_config(params_pulse_config)

        ##

    def set_main_config(self, main_config):
        '''
        Sets the config dict, which acts as a reference for the main parameter names and dtypes.
        '''
        self.main_config = main_config
        self.main_config_nparams = len(self.main_config)

    def set_pulse_config(self, pulse_config):
        '''
        Sets the pulse dict, which acts as a reference for the pulse parameter names and dtypes.
        '''
        self.pulse_config = pulse_config
        self.pulse_config_nparams = len(self.pulse_config)

    def set_npulses(self, npulses):
        '''
        Set the total number of pulses to be sent out.
        '''
        self.npulses = npulses

    def get_full_name(self, param_code, pulse_num = 0):
        '''
        Return the full name of a parameter setting from the specified shortcode and pulse number.
        '''
        if not self.target_name:
            print("WARNING: Attempted to fetch full name of parameter with no target instrument set; None returned.")
            return
        if pulse_num == 0:
            target_string = "".join([self.target_name, " - ", shortcodes[param_code]])
        else:
            target_string = "".join([self.target_name, " - ", shortcodes[param_code], " #", str(pulse_num)])
        return target_string


    def parse_input(self, input_str_list, verbose = False):
        '''
        Parse the input string according to the formats specified for the class instance.

        Splits input string into (<parameter>, <value>) tuples which are then parsed and assigned dimensions based on the specification in the config.
        '''

        ## cat separate pulse strings, split into individual <param>_<value> strings
        param_strings =  [xx.strip().split() for xx in [" ".join(input_str_list)]][0]
        if verbose: print(param_strings)

        ## convert list of strings into list of (<param>, <value>) tuples (no string parsing yet)
        param_tuples = [(key, val) for key, val in [xx.split("_") for xx in param_strings]]
        if verbose: print(param_tuples)

        ## check if config dicts are set
        # if self.main_config == {} or self.pulse_config == {}:
        #     print("Main and/or pulse config dicts are not set; cannot parse input parameters.")
        #     return

        ## separate main and pulse config values
        params_main_tuples = param_tuples[:self.main_config_nparams]
        params_pulse_tuples = param_tuples[self.main_config_nparams:]
        if verbose: print(params_main_tuples)


        ## parse main config values
        self.main_values_in = self.parse_param_tuples(params_main_tuples, self.main_config)
        if verbose: print("Main input value dict:\n", self.main_values_in, sep="")


        ## extract number of pulses from input
        self.npulses = len(params_pulse_tuples)//self.pulse_config_nparams
        if verbose: print("Number of pulses (from input string length):", self.npulses)
        ## Compare number of pulses specified in main input string to number of pulses
        ##      calculated from length of input string. Also compare both to MAX_PULSES
        if self.npulses != self.main_values_in["np"]:
            print("*** WARNING: Mismatch between number of pulses specified in main config (", \
                    str(self.main_values_in["np"]), ") and number of pulses calculated from input string (", \
                    str(self.npulses), ").\nValue based on input string will take precedence, but this may cause undesired behaviour.\n***", sep = "")
        if self.npulses > MAX_PULSES:
            print("*** WARNING: The number of pulse config specifications in the input string (", str(self.npulses),\
                    ") exceeds the maximum number of pulses allowed by the driver (", str(MAX_PULSES), \
                    ").\nThe pulse config specifications will be truncated to ", str(MAX_PULSES), \
                    ", but note that undesired behaviour may occur.\n***", sep = "")
        if self.main_values_in["np"] > MAX_PULSES:
            print("*** WARNING: The number of pulses specified in the main config string (", str(self.main_values_in["np"]),\
                    ") exceeds the maximum number of pulses allowed by the driver (", str(MAX_PULSES), \
                    ").\nThe value passed to Labber will be set to ", str(MAX_PULSES), \
                    ", but note that undesired behaviour may occur.\n***", sep = "")

        # self.pulse_values_in = {}       # now created at init
        ## iterate through params for each pulse, parsing values
        for pulse_ix in range(self.npulses):
            pulse_num = pulse_ix + 1  # pulse numbering begins at 1

            ## extract relevant input param tuples from all input param tuples
            pulse_param_tuples = params_pulse_tuples[pulse_ix*self.pulse_config_nparams:(pulse_ix+1)*self.pulse_config_nparams]
            # if verbose: print("Pulse ", str(pulse_num), " parameter tuples:\n", pulse_param_tuples, sep="")

            ## parse input param tuples
            input_vals = self.parse_param_tuples(pulse_param_tuples, self.pulse_config)
            # if verbose: print("Pulse ", str(pulse_num), " input values:\n", input_vals, sep="")

            ## add to dict
            self.pulse_values_in[pulse_num] = input_vals

        if verbose: print("Pulse input value dict:\n", input_values_pulse, sep="")

        ## post-processing based on user-defined rules
        # self.main_values, self.pulse_values, self.add_values = post_process_params_values(input_values_main, input_values_pulse, verbose = verbose)
        post_process_params_values(self, self.main_values_in, self.pulse_values_in, verbose = verbose)


        if verbose:
            print("Main values stored in InputStrParser class:")
            print(self.main_values_out)
            print("Pulse values stored in InputStrParser class:")
            print(self.pulse_values_out)



    def parse_param_tuples(self, input_tuples, config):
        '''
        Parse list of (<param>, <value>) tuples against specified config.
        '''

        ## dict to store resulting parameter input values
        param_values = {}

        ## iterate, compare keys against config, parse value string
        for param_tuple in input_tuples:
            ## get parameter name
            param_name = param_tuple[0]
            ## attempt to fetch dtype from config dict
            try:
                param_type = config[param_name]
            except:
                print("ERROR: Could not retrieve parameter key:", param_name)
            ## attempt to parse input value using specified dtype
            try:
                param_value = param_type(param_tuple[1])
            except:
                print("ERROR: Could not convert parameter value", param_tuple[1], "to desired type", param_type)

            ## add pair to dict
            param_values[param_name] = param_value

        return param_values


    def set_MeasurementObject(self, target_MeasurementObject, target_instrument_name = "Single-Qubit Pulse Generator", verbose = False):
        '''
        Specify the target Labber MeasurementObject instance whose values should be updated, along with the instrument name (default is "Single-Qubit Pulse Generator").

        This method checks whether or not the file path specified for output at the MeasurementObject already exists, and, if so, exits the program in order to prevent appending data to an existing log file. If the file does not already exist, execution continues.
        '''
        self.target_MO = target_MeasurementObject
        if verbose: print("Measurement object set as:", self.target_MO)
        self.target_name = target_instrument_name

        #### this is now handled by the FileManager class
        # ## check if output file already exists, and either get new filename or exit script
        # file_MO_out = self.target_MO.sCfgFileOut
        # new_file_MO_out = get_valid_out_file(file_MO_out, verbose = verbose)
        # ## TODO: implement with proper exception handling at some stage (probably not very urgent...)
        # if new_file_MO_out is None:
        #     ## unable to get valid file name; exit script
        #     sys.exit("Unable to get valid output file.")
        # else:
        #     ## set filename again (can be the same if original filename was valid)
        #     print("Output file:", new_file_MO_out)
        #     self.target_MO.setOutputFile(new_file_MO_out)



    def update_param_values(self, verbose = False):
        '''
        Update the parameter values of the target Labber MeasurementObject for single-valued (ie not iterated) parameters.
        '''
        ## verify that target MeasurementObject has been specified
        if self.target_MO == None:
            print("ERROR: Target MeasurementObject has not been specified! Cannot update values.")
            return

        if verbose: print("Updating MeasurementObject values...")

        ## update main config values
        if verbose: print("Updating main config values...")
        # print(self.main_values)
        for main_param in self.main_values_out:
            # print(main_param, self.main_values[main_param])
            target_string = " - ".join([self.target_name, main_param])
            self.target_MO.updateValue(target_string, self.main_values_out[main_param], 'SINGLE')
        if verbose: print("Main config values updated.")

        ## reset pulse amplitudes to ensure no leftovers from previous experiments
        ##  eg 4 pulses used previously, amplitudes not modified => they will still
        ##  be nonzero!
        if verbose: print("Resetting pulse amplitudes...")
        for pulse_num in range(1,MAX_PULSES+1):
            target_string = "".join([self.target_name, " - Amplitude #", str(pulse_num)])
            self.target_MO.updateValue(target_string, 0.0, 'SINGLE')
            target_string = "".join([self.target_name, " - Width #", str(pulse_num)])
            self.target_MO.updateValue(target_string, 0.0, 'SINGLE')
            target_string = "".join([self.target_name, " - Plateau #", str(pulse_num)])
            self.target_MO.updateValue(target_string, 0.0, 'SINGLE')
            target_string = "".join([self.target_name, " - Spacing #", str(pulse_num)])
            self.target_MO.updateValue(target_string, 0.0, 'SINGLE')
        if verbose: print("Pulse amplitudes, widths, plateaux, spacings reset.")


        ## update pulse config values
        if verbose: print("Updating pulse config values...")
        for pulse_num in range(1,1+min(self.npulses, MAX_PULSES)):
            if verbose: print("Updating values for pulse", str(pulse_num))
            param_vals = self.pulse_values_out[pulse_num]
            for param_name in param_vals:
                if param_name in [shortcodes["cf"], shortcodes["if"], "LO frequency"]:
                    continue
                else:
                    target_string = "".join([self.target_name, " - ", param_name, " #", str(pulse_num)])
                    self.target_MO.updateValue(target_string, param_vals[param_name], 'SINGLE')
        if verbose: print("Pulse config values updated.")

        ## exit message
        if verbose: print("MeasurementObject values updated successfully.")

    def set_iteration_params(self, iteration_input, instrument_name = "Single-Qubit Pulse Generator", verbose = False):
        '''
        Parse input for variable iteration, and set the corresponding Labber MeasurementObject values.

        Note that shortcodes should be used to specify the parameter name.

        Input arg must be a list of the format:
        [<pulse>, <param>, <start value>, <end value>, <npts>]
        NB <pulse> should be set to 0 for main config parameters.
        '''

        ## verify that target MeasurementObject has been specified
        if self.target_MO == None:
            print("ERROR: Target MeasurementObject has not been specified! Cannot update values.")
            return

        if verbose: print("Parsing iteration spec input...")

        pulse_num = iteration_input[0]
        param_code = iteration_input[1]
        start_value_in = iteration_input[2]
        stop_value_in = iteration_input[3]
        n_pts = iteration_input[4]

        ## do post-processing on start and stop values
        if param_code in shortcodes:
            param_name = shortcodes[param_code]
        else:
            param_name = param_code
        ## main value
        if pulse_num == 0:
            if instrument_name == "Single-Qubit Pulse Generator":
                ## check if parameter is in additional or pulse-specific shortcodes
                if param_code in pulseapp_shortcodes or param_code in add_shortcodes:
                    ## not sure how best to handle this right now; probably not needed
                    print("*** ERROR No implementation for pulse-applied or additional parameters.")
                    return
                ## parameter is a valid main parameter
                else:
                    start_out, pulse_placeholder = post_process_params_values(self, in_main = {param_code: start_value_in})
                    start_value_out = start_out[param_name]
                    stop_out, pulse_placeholder = post_process_params_values(self, in_main = {param_code: stop_value_in})
                    stop_value_out = stop_out[param_name]
            ## parameter is from a different instrument - passthrough unchanged
            else:
                start_value_out = start_value_in
                stop_value_out = stop_value_in
        ## pulse value
        else:
            main_placeholder, start_out = post_process_params_values(self, in_pulses = {pulse_num: {param_code: start_value_in}})
            start_value_out = start_out[pulse_num][param_name]
            main_placeholder, stop_out = post_process_params_values(self, in_pulses = {pulse_num: {param_code: stop_value_in}})
            stop_value_out = stop_out[pulse_num][param_name]
        ## set up target string
        ## main
        if pulse_num == 0:
            target_string = "".join([instrument_name, " - ", param_name])
        ## pulse
        else:
            target_string = "".join([instrument_name, " - ", param_name, " #", str(pulse_num)])

        ## update values
        self.target_MO.updateValue(target_string, start_value_out, 'START')
        self.target_MO.updateValue(target_string, stop_value_out, 'STOP')
        self.target_MO.updateValue(target_string, n_pts, 'N_PTS')

    def order_iteration_params(self, iter_spec_list, verbose = False):
        '''
        This is a docstring...
        '''
        ## extract (ordered) full parameter names
        param_order_list = []
        for iter_spec in iter_spec_list:
            param_order_list.append(self.get_full_name(iter_spec[1], iter_spec[0]))
        if verbose: print("Desired parameter order extracted from iteration spec.")

        ## open reference config file and shift order around
        if verbose: print("Re-ordering iteration parameters in config file...")
        index_counter = 0     # tracks index which list item must be swapped to
        if verbose: print("Reference file:", self.target_MO.sCfgFileIn)
        with h5py.File(self.target_MO.sCfgFileIn, 'r+') as fconfig:
            sort_step_entries(fconfig, param_order_list)
        if verbose: print("Re-ordering of iteration parameters completed.")

    def set_all(self, point_values, iter_list, verbose = False):
        '''
        Wrapper method to set all variables for an experiment in one go.

        iter_list must be a list of iteration variables to be set. Even if only one variable is being set, it should still be wrapped as a list.
        '''
        ## verify that target MeasurementObject has been specified
        if self.target_MO == None:
            print("ERROR: Target MeasurementObject has not been specified! Cannot update values.")
            return

        ## parse and set point values
        if verbose: print("Parsing point value input...")
        self.parse_input(point_values, verbose = verbose)
        if verbose: print("Point value input parsed.")
        self.update_param_values()

        ## parse and set iteration values
        for iter_var in iter_list:
            self.set_iteration_params(iter_var)

        ## set correct order for iteration values
        self.order_iteration_params(iter_list)

##

class DummyMeasurementObject:
    def __init__(self, sCfgFileOut = "", silent_mode = False):
        self.sCfgFileOut = sCfgFileOut
        self.silent_mode = silent_mode

    def updateValue(self, target_string, value, value_spec):
        if self.silent_mode:
            return
        else:
            if value_spec == 'SINGLE':
                print("Instrument parameter \"", target_string, "\" updated to ", value, sep = "")
            else:
                print("Instrument parameter iteration set:\n\t\t\"", target_string, "\" updated to ", value, " as ", value_spec, " variable.", sep = "")


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

## extra stuff used for hdf5 editing

## dtype template used for 'Step list' entries
# sl_entry_dtype = np.dtype([('variable', 'O'), ('channel_name', 'O'), ('use_lookup', '?')])
## doesn't work - for some reason we have to fetch the dtype from the hdf5 file first...

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## #

##

class Hdf5Editor:

    def __init__(self, labber_MO, verbose = False):
        self.set_target_MO(labber_MO, verbose = verbose)
        self.channel_spec = {}
        self.sl_entry_dtype = None
        ##
        if verbose: print("Hdf5Editor instance initialised.")

    def set_target_MO(self, labber_MO, verbose = False):
        self.target_MO = labber_MO
        self.config_file = self.target_MO.sCfgFileIn
        ##
        if verbose: print("Target MeasurementObject set.")

    def add_channel_spec(self, channel_key, instrument_spec, verbose = False):
        '''
        Add a channel specification (to be used in channel relations) to the Hdf5Editor instance's database.

        Instrument spec should be a list of the format [<instrument name>, <parameter name or shortcode>, <pulse number (optional)>]; this list will be passed directly to get_full_label().

        The channel_key should be unique, and will correspond to the symbol used in the algebraic formulas expressing channel relations. DO NOT USE 'x'! -> this may cause undefined behaviour as it is the default label used as 'self' for all channels.
        '''
        ## convert instrument_spec into full channel name
        channel_name = get_full_label(*instrument_spec)
        # print("Full label is:", channel_name)
        ## fetch step list entry dtype if not already fetched
        if self.sl_entry_dtype is None:
            with h5py.File(self.config_file, 'r') as fconfig:
                for inst_key in fconfig['Step config']:
                    self.sl_entry_dtype = np.dtype(fconfig['Step config'][inst_key]['Relation parameters'].dtype)
                    break
        ## add full channel spec entry
        self.channel_spec[channel_key] = np.array([(channel_key, channel_name, False)], dtype = self.sl_entry_dtype)
        if verbose: print("Channel spec", self.channel_spec[channel_key], "added.")

    def remove_channel_spec(self, channel_key):
        '''
        Remove a channel specification (used for channel relations) from the Hdf5Editor instance's database.
        '''
        del self.channel_spec[channel_key]

    def get_sl_index(self, label_string, verbose = False):
        '''
        Gets the index of the entry matching the label string in the config file's "Step list".

        label_string should be a full spec (ie expanded by get_full_label).
        '''
        ## open file and extract existing step list
        if verbose: print("Extracting step list from config file...")
        with h5py.File(self.config_file, "r") as fconfig:
            step_list = fconfig['Step list'].value
        if verbose: print("Step list extracted")
        ## get index of element with matching label string
        step_list_labels = [xx['channel_name'] for xx in step_list]
        index = step_list_labels.index(label_string)
        if verbose: print("Step list index for", label_string, "is", str(index))
        return index

    def set_equation_string(self, equation_string, label_string, verbose = False):
        '''
        Set the equation string for a given parameter label.

        Note that it is the user's responsibility to ensure that the correct channel keys are provided and referenced in the step config (with respect to the corresponding equation specified in the step list config). Thus, it is recommended to use the Hdf5Editor.set_relation method, which is a wrapper for both the set_step_config and set_equation_string methods.
        '''
        if verbose: print("Setting equation string", equation_string, "for", label_string)
        ## get 'Step list' index of label string
        step_list_index = self.get_sl_index(label_string)
        ## modify step list entry
        with h5py.File(self.config_file, 'r+') as fconfig:
            new_entry = fconfig['Step list'][step_list_index]
            new_entry['equation'] = equation_string
            new_entry['use_relations'] = True
            new_entry['show_advanced'] = True
            fconfig['Step list'][step_list_index] = new_entry
        if verbose: print("Equation string set for", label_string)
        ##

    def set_step_config(self, label_string, channel_keys, verbose = False):
        '''
        Set the step config for a given parameter label.

        Note that it is the user's responsibility to ensure that the correct channel keys are provided and referenced in the step config (with respect to the corresponding equation specified in the step list config). Thus, it is recommended to use the Hdf5Editor.set_relation method, which is a wrapper for both the set_step_config and set_equation_string methods.
        '''
        if verbose:
            print("Setting step config for", label_string)
            print("Channel keys specified as:", channel_keys)
        ## iterate through channel keys and build up complete step config entry
        channel_entries = []
        for channel_key in channel_keys:
            channel_entries.append(self.channel_spec[channel_key])
        new_sc_entries = np.concatenate(channel_entries)
        if verbose: print("New step config entries:\n", new_sc_entries, sep = "")
        ## delete old step config entry and replace with new one
        with h5py.File(self.config_file, 'r+') as fconfig:
            try:
                del fconfig['Step config'][label_string]['Relation parameters']
            except:
                pass
            fconfig['Step config'][label_string].create_dataset('Relation parameters', data = new_sc_entries)
        if verbose: print("Step config entries set.")
        ##

    def set_relation(self, instrument_spec, equation_string, required_channel_keys, verbose = False):
        '''
        Set a new relation that determines the values of the parameter specified by <instrument_spec>.

        Note that the required channel keys should have previously been added to the Hdf5Editor instance using the add_channel_spec method; a KeyError (or worse) will result if this is not the case.

        <instrument_spec> should be a list of the format [<instrument name>, <parameter name>, <pulse number (optional)>]. A NoneType or blank string <instrument name> will default to the SQPG.
        '''
        ## convert instrument spec to label string
        label_string = get_full_label(*instrument_spec)
        ## set equation string (and other step list parameters)
        self.set_equation_string(equation_string, label_string, verbose = verbose)
        ## set step config entries
        self.set_step_config(label_string, required_channel_keys, verbose = verbose)
        ##



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


## Kinda-deprecated functions - use InputStrParser object methods instead.
## "Big" function to be used in scripts
def update_values_from_string(param_string_list, labber_measurement_object, instrument_name = None, verbose = False):
    '''
    Updates the values of the specified Labber MeasurementObject using the list of strings passed in.

    NOTE: This function should NOT be used if interaction with the Parser object in the external script is desired. Instead, use the InputStrParser parsing and setting methods directly (or one of the other convenience methods provided for that purpose).

    The param_string_list must be of the format:
        [<main config string>, <pulse 1 string>, <pulse 2 string>, ...].
    The string format is
        "<param 1 name>_<param 1 value> <param 2 name>_<param 2 value> ..."
    and must exactly match the parameter names specified in the params_main_config and params_pulse_config.

    If left blank, instrument_name will default to "Single-Qubit Pulse Generator".
    '''

    ## init parser object
    Parser = InputStrParser()

    ## set main config dict (at beginning of this file)
    Parser.set_main_config(params_main_config)
    ## set pulse config dict (at beginning of this file)
    Parser.set_pulse_config(params_pulse_config)

    ## parse input values
    Parser.parse_input(param_string_list, verbose = verbose)

    ## Set target MeasurementObject and update values
    Parser.set_MeasurementObject(labber_measurement_object)
    Parser.update_param_values(verbose = verbose)
##




##
