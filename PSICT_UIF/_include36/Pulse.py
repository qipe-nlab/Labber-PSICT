## Class for storing individual pulses and their attributes
##  Non-"programming" attributes can be either physical or non-physical (ordering);
##  the intention is for these to be handled differently by the input-output
##  pulse conversion algorithm

import PSICT_UIF._include36._Pulse_rc as _rc

class Pulse:
    '''
    Docstring for Pulse class.
    '''
    def __init__(self, spec):
        self.attributes = {}
        if isinstance(spec, dict):
            self.set_attributes(spec) # all attributes (including the name) will be stored in this dict
        elif isinstance(spec, str):
            self.name = name     # the pulse name will be used as a reference when setting relations etc
        else:
            raise TypeError("Invalid specification for Pulse creation:", spec)

    def __repr__(self):
        return "".join(["<Pulse \"", self.name, "\">"])
    # def __str__(self):
    #     return "".join(["Pulse \"", self.name, "\""])


    ###########################################################################
    ## Properties and attributes

    ## pulse name
    @property
    def name(self):
        # print("Executing getter")
        return self.attributes["name"]
    @name.setter
    def name(self, name):
        # print("Executing setter.")
        self.attributes["name"] = name

    def __getitem__(self, key):
        return self.attributes[key]


    ###########################################################################
    ## Attribute import and input

    def set_attributes(self, input_attributes, *, verbose = 0):
        '''
        Set attributes from the dict input_attributes.
        '''
        for key, value in input_attributes.items():
            if key in _rc.ALL_PARAMS:
                self.attributes[key] = value
            else:
                raise KeyError(" ".join(["Key", key, "is not defined as a valid pulse parameter."]))
