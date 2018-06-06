## Class for storing individual pulses and their attributes
##  Non-"programming" attributes can be either physical or non-physical (ordering);
##  the intention is for these to be handled differently by the input-output
##  pulse conversion algorithm

import PSICT_UIF._include36._Pulse_rc as _rc

class Pulse:
    '''
    Abstract representation of an individual pulse in the pulse sequence.

    This class should not in general be used directly, but instead managed through PulseSeq objects (which act as containers for the pulse sequence as a whole)
    '''
    def __init__(self, spec, *, verbose = 0):
        self.attributes = {}
        if isinstance(spec, dict):  # create from dict of parameters
            if verbose >= 4:
                print("Creating Pulse object from parameter dict...")
            self.set_attributes(spec, verbose = verbose)
        elif isinstance(spec, str): # create from string as name
            if verbose >= 4:
                print("Creating pulse object by name:", spec)
            self.name = spec
        else:
            raise TypeError("Invalid specification for Pulse creation:", spec)

    def __repr__(self):
        return "".join(["<Pulse \"", self.name, "\">"])


    ###########################################################################
    ## Properties and attributes

    ## Pulse name
    @property
    def name(self):
        return self.attributes["name"]
    @name.setter
    def name(self, name):
        self.attributes["name"] = name

    def __getitem__(self, key):
        return self.attributes[key]

    def __setitem__(self, key, value):
        if key in _rc.ALL_PARAMS:
            self.attributes[key] = value
        else:
            raise KeyError(" ".join(["Key", key, "is not defined as a valid pulse parameter."]))

    ###########################################################################
    ## Attribute import and input

    def set_attributes(self, input_attributes, *, verbose = 0):
        '''
        Set attributes from an input dictionary input_attributes.
        '''
        for key, value in input_attributes.items():
            self[key] = value
            if verbose >= 3:
                try:
                    print("Pulse ", self.name, ": attribute ", key, " set to value ", value, sep = "")
                except KeyError:
                    print("<unnamed pulse>: attribute", key, "set to value", value)
