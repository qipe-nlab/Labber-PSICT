### String input parser for Labber pulse sequences
## Author:         Sam Wolski
## Date modified:  2018/04/13




class InputStrParser:

    def __init__(self):
        ## config dicts to define parameter names and dtypes
        self.main_config = {}
        self.pulse_config = {}
        self.main_config_nparams = 0
        self.pulse_config_nparams = 0


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

        ## parse pulse config values
        input_values_main = self.parse_param_tuples(params_main_tuples, self.main_config)
        if verbose: print(input_values_main)

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
                print("Could not retrieve parameter key:", param_name)
            ## attempt to parse input value using specified dtype
            try:
                param_value = param_type(param_tuple[1])
            except:
                print("Could not convert parameter value", param_tuple[1], "to desired type", param_type)

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

Parser = InputStrParser()

## set main config dict
Parser.set_main_config(params_main_config)

## parse input values
Parser.parse_input(example_input_string)





##
