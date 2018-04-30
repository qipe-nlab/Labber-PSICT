### String input parser for Labber pulse sequences
## Author:         Sam Wolski
## Date modified:  2018/04/13




class InputStrParser:

    def __init__(self):
        pass

    def parse_input(self, input_str_list):
        '''
        Parse the input string according to the formats specified for the class instance.

        Splits input string into (<parameter>, <value>) tuples which are then parsed and assigned dimensions based on the specification in the config.
        '''

        # cat separate pulse strings, split into individual <param>_<value> strings
        param_strings =  [xx.strip().split() for xx in [" ".join(input_str_list)]][0]
        print(param_strings)

        # convert list of strings into list of (<param>, <value>) tuples (no string parsing yet)
        param_tuples = [(key, val) for key, val in [xx.split("_") for xx in param_strings]]
        print(param_tuples)

##


example_input_string = [
        "sr_1E9 npts_10E3 delay_400", # overall config
        "A_12 W_16 P_2",              # 1st pulse
        "A_15 W_2 P_0",               # 2nd pulse
    ]

Parser = InputStrParser()

Parser.parse_input(example_input_string)





##
