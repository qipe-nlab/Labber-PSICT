### String input parser for Labber pulse sequences
## Author:         Sam Wolski
## Date modified:  2018/04/13


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

    NB: Pulses should be referred to by their actual number (starting at 1, not 0).
    '''
    if verbose: print("Beginning post-processing...")
    ## output dicts
    out_main = {}
    out_pulse = {}

    ## main values
    out_main["sr"] = in_main["sr"]             # sample rate
    out_main["npts"] = in_main["npts"]         # number of points
    out_main["delay"] = in_main["delay"]       # first signal delay
    ## status print
    if verbose:
        print("(main) Sample rate:", out_main["sr"])
        print("(main) Number of points:", out_main["npts"])
        print("(main) First pulse delay:", out_main["delay"])

    ## pulse values
    npulses = len(in_pulse)
    if verbose: print("(pulse) Number of pulses:", npulses)
    for pulse_num in range(1,npulses+1):
        ## init sub-dict for each pulse
        out_pulse[pulse_num] = {}

        out_pulse[pulse_num]["A"] = in_pulse[pulse_num]["A"]    # pulse amplitude
        out_pulse[pulse_num]["W"] = in_pulse[pulse_num]["W"]    # pulse amplitude
        out_pulse[pulse_num]["P"] = in_pulse[pulse_num]["P"]    # pulse amplitude
        ## status print
        if verbose:
            print("(pulse)", pulse_num, "Amplitude:", out_pulse[pulse_num]["A"])
            print("(pulse)", pulse_num, "Width:", out_pulse[pulse_num]["W"])
            print("(pulse)", pulse_num, "Plateau:", out_pulse[pulse_num]["P"])

    ##

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
        if verbose: print("Number of pulses:", self.npulses)

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
        self.main_values, self.pulse_values = post_process_params_values(input_values_main, input_values_pulse, verbose = verbose)

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

##


example_input_string = [
        "sr_1E9 npts_10E3 delay_400", # overall config
        "A_12 W_16 P_2",              # 1st pulse
        "A_15 W_2 P_0",               # 2nd pulse
    ]

params_main_config = {
        "sr":     float,  # sample rate
        "npts":   float,  # number of points
        "delay":  float,  # first pulse delay
    }

params_pulse_config = {
        "A":      float,  # pulse apmlitude
        "W":      float,  # pulse width
        "P":      float,  # pulse plateau width
    }



Parser = InputStrParser()

## set main config dict
Parser.set_main_config(params_main_config)
## set pulse config dict
Parser.set_pulse_config(params_pulse_config)

## parse input values
Parser.parse_input(example_input_string, verbose = True)





##
