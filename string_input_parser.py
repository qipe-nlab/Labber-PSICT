### String input parser for Labber pulse sequences
## Author:         Sam Wolski
## Date modified:  2018/04/13

import os      # for checking if output file exists in InputStrParser.set_MeasurementObject
import sys     # for sys.exit

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
        "cf":     float,  # Control frequency in MHz
        "if":     float,  # IF frequency (to be modulated by Mod. freq) in MHz
    }

params_pulse_config = {
        "a":      float,  # Amplitude
        "w":      float,  # Width in ns
        "v":      float,  # Plateau in ns
        "s":      float,  # Spacing in ns
        "p":      float,  # Phase
        "f":      float,  # Mod. frequency (offset from IF frequency) in MHz
        "o":      str,    # Output
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
add_shortcodes = ["dead", "cf", "if"]
pulseapp_shortcodes = ["IQ", "dphi"]

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
convert_out = {"QubitControl": 0, "QubitReadout": 1, "MagnonControl": 2, "MagnonReadout": 3}
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
    if "cf" in in_main:
        parserObj.add_values_out[shortcodes["cf"]] = in_main["cf"]*1e6        # MHz
    if "if" in in_main:
        parserObj.add_values_out[shortcodes["if"]] = in_main["if"]*1e6             # MHz
    if "cf" in in_main and "if" in in_main:
        parserObj.add_values_out["LO frequency"] = parserObj.add_values_out[shortcodes["cf"]] - parserObj.add_values_out[shortcodes["if"]]
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
        ## same sign => same sideband
        if "f" in in_pulse:
            freq_offset = in_pulse["f"]*1e6      # MHz
            if parserObj.add_values_out[shortcodes["if"]]*(parserObj.add_values_out["IF frequency"] + freq_offset) >= 0:
                parserObj.pulse_values_out[pulse_num][shortcodes["f"]] = abs(parserObj.add_values_out["IF frequency"] + freq_offset)
            ## sideband switching
            else:
                print("*** WARNING: Specified frequency offset induces a sideband switch for pulse ", pulse_num, "; defaulting to 0.", sep = "")
                parserObj.pulse_values_out[pulse_num][shortcodes["f"]] = abs(parserObj.add_values_out["IF frequency"])
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
                    str(input_values_main["np"]), ") and number of pulses calculated from input string (", \
                    str(self.npulses), ").\nValue based on input string will take precedence, but this may cause undesired behaviour.\n***", sep = "")
        if self.npulses > MAX_PULSES:
            print("*** WARNING: The number of pulse config specifications in the input string (", str(self.npulses),\
                    ") exceeds the maximum number of pulses allowed by the driver (", str(MAX_PULSES), \
                    ").\nThe pulse config specifications will be truncated to ", str(MAX_PULSES), \
                    ", but note that undesired behaviour may occur.\n***", sep = "")
        if self.main_values_in["np"] > MAX_PULSES:
            print("*** WARNING: The number of pulses specified in the main config string (", str(input_values_main["np"]),\
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

        ## check if output file already exists
        file_MO_out = self.target_MO.sCfgFileOut
        if verbose: print("The output path specified is\n", file_MO_out, sep = "")
        if os.path.isfile(file_MO_out):
            errmsg = "".join(["The output file\n\t", file_MO_out, "\nalready exists; execution halted to prevent appending data."])
            sys.exit(errmsg)
        else:
            if verbose: print("Output file does not already exist, continuing...")


    def update_param_values(self, verbose = False):
        '''
        Update the parameter values of the target Labber MeasurementObject.
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
        if verbose: print("Pulse amplitude reset.")

        ## update pulse config values
        if verbose: print("Updating pulse config values...")
        for pulse_num in range(1,1+min(self.npulses, MAX_PULSES)):
            if verbose: print("Updating values for pulse", str(pulse_num))
            param_vals = self.pulse_values_out[pulse_num]
            for param_name in param_vals:
                target_string = "".join([self.target_name, " - ", param_name, " #", str(pulse_num)])
                self.target_MO.updateValue(target_string, param_vals[param_name], 'SINGLE')
        if verbose: print("Pulse config values updated.")

        ## exit message
        if verbose: print("MeasurementObject values updated successfully.")

    def set_iteration_params(self, iteration_input, verbose = False):
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
        param_name = shortcodes[param_code]
        ## main value
        if pulse_num == 0:
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
        ## pulse value
        else:
            main_placeholder, start_out = post_process_params_values(self, in_pulses = {pulse_num: {param_code: start_value_in}})
            start_value_out = start_out[pulse_num][param_name]
            main_placeholder, stop_out = post_process_params_values(self, in_pulses = {pulse_num: {param_code: stop_value_in}})
            stop_value_out = stop_out[pulse_num][param_name]
        ## set up target string
        ## main
        if pulse_num == 0:
            target_string = "".join([self.target_name, " - ", param_name])
        ## pulse
        else:
            target_string = "".join([self.target_name, " - ", param_name, " #", str(pulse_num)])

        ## update values
        self.target_MO.updateValue(target_string, start_value_out, 'START')
        self.target_MO.updateValue(target_string, stop_value_out, 'STOP')
        self.target_MO.updateValue(target_string, n_pts, 'N_PTS')


    def set_all(self, point_values, iter_list):
        '''
        Wrapper method to set all variables for an experiment in one go.

        iter_list must be a list of iteration variables to be set. Even if only one variable is being set, it should still be wrapped as a list.
        '''
        ## verify that target MeasurementObject has been specified
        if self.target_MO == None:
            print("ERROR: Target MeasurementObject has not been specified! Cannot update values.")
            return

        ## parse and set point values
        self.parse_input(point_values)
        self.update_param_values()

        ## parse and set iteration values
        for iter_var in iter_list:
            self.set_iteration_params(iter_var)

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
