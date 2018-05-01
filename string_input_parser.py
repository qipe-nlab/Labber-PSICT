### String input parser for Labber pulse sequences
## Author:         Sam Wolski
## Date modified:  2018/04/13



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
## Configs for admissible parameter input values.

params_main_config = {
        "sr":     float,  # sample rate
        # "npts":   float,  # number of points - calculated from dead, sr, and pulse sequence
        "dead":   float,  # Dead time (relaxation of qubit after pulse sequence)
        "delay":  float,  # first pulse delay
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
        "cf":     float,  # Control frequency
        "if":     float,  # IF frequency (to be modulated by Mod. freq)
    }

params_pulse_config = {
        "a":      float,  # Amplitude
        "w":      float,  # Width
        "v":      float,  # Plateau
        "s":      float,  # Spacing
        "p":      float,  # Phase
        "f":      float,  # Mod. frequency
        "o":      str,    # Output
    }

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
def post_process_params_values(in_main, in_pulse, verbose = False):
    '''
    Defines post-processing operations to be carried out on raw input values.

    Twofold main purpose:
        - Converts more descriptive strings (eg for output channel name)
            into integer switch values
        - Calculates parameters that should be based on other parameters
            (eg pulse spacing as a function of pulse width)

    - out_main variable names (ie output) must match the variable names on the
        instrument as these will be passed directly to the Labber API
        updateValue methods.
    - Pulses should be referred to by their actual number (starting at 1, not 0).
    '''
    if verbose: print("Beginning post-processing...")
    ## output dicts
    out_main = {}
    out_pulse = {}

    ## main values
    out_main["Sample rate"] = in_main["sr"]
    # out_main["Number of points"] = in_main["npts"]
    out_main["First pulse delay"] = in_main["delay"]
    out_main["Trim waveform to sequence"] = 0 if in_main["trim"] == 0 else 1
    out_main["Number of outputs"] = convert_nout[in_main["nout"]]
    out_main["# of pulses"] = in_main["np"] if in_main["np"] <= MAX_PULSES else MAX_PULSES
    out_main["Pulse type"] = convert_ptype[in_main["ptype"]]
    out_main["Truncation range"] = in_main["tr"]
    out_main["Start at zero"] = 0 if in_main["saz"] == 0 else 1
    out_main["Edge-to-edge pulses"] = 0 if in_main["e2e"] == 0 else 1
    out_main["Edge position"] = in_main["epos"]
    out_main["Use SSB mixing"] = 0 if in_main["SSB"] == 0 else 1
    out_main["Use DRAG"] = 0 if in_main["DRAG"] == 0 else 1
    ## status print
    if verbose:
        print("(main) Sample rate:", out_main["Sample rate"])
        # print("(main) Number of points:", out_main["Number of points"])
        print("(main) First pulse delay:", out_main["First pulse delay"])

    ## pulse values
    npulses = len(in_pulse)
    if verbose: print("(pulse) Number of pulses:", npulses)
    for pulse_num in range(1,npulses+1):
        ## init sub-dict for each pulse
        out_pulse[pulse_num] = {}

        out_pulse[pulse_num]["Amplitude"] = in_pulse[pulse_num]["a"]
        out_pulse[pulse_num]["Width"] = in_pulse[pulse_num]["w"]
        out_pulse[pulse_num]["Plateau"] = in_pulse[pulse_num]["v"]
        out_pulse[pulse_num]["Spacing"] = in_pulse[pulse_num]["s"]
        out_pulse[pulse_num]["Phase"] = in_pulse[pulse_num]["p"]
        out_pulse[pulse_num]["Mod. frequency"] = in_pulse[pulse_num]["f"]
        out_pulse[pulse_num]["Output"] = convert_out[in_pulse[pulse_num]["o"]]
        ## overall parameters applied to pulses individually
        out_pulse[pulse_num]["Ratio I/Q"] = in_main["IQ"]
        out_pulse[pulse_num]["Phase diff."] = in_main["dphi"]

        ## status print
        if verbose:
            print("(pulse)", pulse_num, "Amplitude:", out_pulse[pulse_num]["Amplitude"])
            print("(pulse)", pulse_num, "Width:", out_pulse[pulse_num]["Width"])
            print("(pulse)", pulse_num, "Plateau:", out_pulse[pulse_num]["Plateau"])

    ##

    # # # # # # # # # # # # # # # # #
    ## Additional calculations

    ## Number of points from pulse sequence, dead time, and sample rate
    ##   Calculation depends on whether or not pulses are e2e
    if out_main["Edge-to-edge pulses"]:
        total_time = out_main["First pulse delay"] + sum([out_pulse[xx]["Width"] + \
                out_pulse[xx]["Plateau"] + out_pulse[xx]["Spacing"] for xx in range(1, npulses+1)]) \
                + in_main["dead"]
    else:
        total_time = out_main["First pulse delay"] + sum([out_pulse[xx]["Spacing"] for xx in range(1, npulses+1)]) + in_main["dead"]
    if verbose: print("Total time for pulse sequence (incl dead time):", str(total_time), "ns")
    out_main["Number of points"] = int(out_main["Sample rate"]*total_time*1e-9)
    if verbose: print("Calculated number of points:", str(out_main["Number of points"]))

    # # # # # # # # # # # # # # # # #


    ## complete debug printing
    if verbose:
        print("Main parameters:")
        print(out_main)
        print("Pulse parameters:")
        print(out_pulse)

    ## completion status message
    if verbose: print("Post-processing completed.")

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
        input_values_main = self.parse_param_tuples(params_main_tuples, self.main_config)
        if verbose: print(input_values_main)


        ## extract number of pulses from input
        self.npulses = len(params_pulse_tuples)//self.pulse_config_nparams
        if verbose: print("Number of pulses (from input string length):", self.npulses)
        ## Compare number of pulses specified in main input string to number of pulses
        ##      calculated from length of input string. Also compare both to MAX_PULSES
        if self.npulses != input_values_main["np"]:
            print("*** WARNING: Mismatch between number of pulses specified in main config (", \
                    str(input_values_main["np"]), ") and number of pulses calculated from input string (", \
                    str(self.npulses), ").\nValue based on input string will take precedence, but this may cause undesired behaviour.\n***", sep = "")
        if self.npulses > MAX_PULSES:
            print("*** WARNING: The number of pulse config specifications in the input string (", str(self.npulses),\
                    ") exceeds the maximum number of pulses allowed by the driver (", str(MAX_PULSES), \
                    ").\nThe pulse config specifications will be truncated to ", str(MAX_PULSES), \
                    ", but note that undesired behaviour may occur.\n***", sep = "")
        if input_values_main["np"] > MAX_PULSES:
            print("*** WARNING: The number of pulses specified in the main config string (", str(input_values_main["np"]),\
                    ") exceeds the maximum number of pulses allowed by the driver (", str(MAX_PULSES), \
                    ").\nThe value passed to Labber will be set to ", str(MAX_PULSES), \
                    ", but note that undesired behaviour may occur.\n***", sep = "")

        input_values_pulse = {}
        ## iterate through params for each pulse, parsing values
        for pulse_ix in range(self.npulses):
            pulse_num = pulse_ix + 1  # pulse numbering begins at 1

            ## extract relevant input param tuples from all input param tuples
            pulse_param_tuples = params_pulse_tuples[pulse_ix*self.pulse_config_nparams:(pulse_ix+1)*self.pulse_config_nparams]
            if verbose: print(pulse_param_tuples)

            ## parse input param tuples
            input_vals = self.parse_param_tuples(pulse_param_tuples, self.pulse_config)
            if verbose: print(input_vals)

            ## add to dict
            input_values_pulse[pulse_num] = input_vals

        if verbose: print(input_values_pulse)

        ## post-processing based on user-defined rules
        self.main_values, self.pulse_values = post_process_params_values(input_values_main, input_values_pulse, verbose = False)

        if verbose:
            print("Main values stored in InputStrParser class:")
            print(self.main_values)
            print("Pulse values stored in InputStrParser class:")
            print(self.pulse_values)



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


    def set_MeasurementObject(self, target_MeasurementObject, target_instrument_name = "Single-Qubit Pulse Generator"):
        '''
        Specify the target Labber MeasurementObject instance whose values should be updated, along with the instrument name (default is "Single-Qubit Pulse Generator").
        '''
        self.target_MO = target_MeasurementObject
        print("Measurement object set as:", self.target_MO)
        self.target_name = target_instrument_name

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
        for main_param in self.main_values:
            # print(main_param, self.main_values[main_param])
            target_string = " - ".join([self.target_name, main_param])
            self.target_MO.updateValue(target_string, self.main_values[main_param], 'SINGLE')
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
            param_vals = self.pulse_values[pulse_num]
            for param_name in param_vals:
                target_string = "".join([self.target_name, " - ", param_name, " #", str(pulse_num)])
                self.target_MO.updateValue(target_string, param_vals[param_name], 'SINGLE')
        if verbose: print("Pulse config values updated.")

        ## exit message
        if verbose: print("MeasurementObject values updated successfully.")


##

class DummyMeasurementObject:
    def __init__(self):
        pass

    def updateValue(self, target_string, value, value_spec):
        print("Instrument parameter \"", target_string, "\" updated to ", value, sep = "")


## "Big" function to be used in scripts
def update_values_from_string(param_string_list, labber_measurement_object, instrument_name = None, verbose = False):
    '''
    Updates the values of the specified Labber MeasurementObject using the list of strings passed in.

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
