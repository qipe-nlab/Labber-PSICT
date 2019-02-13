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
    def __init__(self, spec, *, parent_logger_name = None):
        self.attributes = {}
        self.valid_abs_time = False
        if isinstance(spec, dict):  # create from dict of parameters
            # if verbose >= 4:
            #     print("Creating Pulse object from parameter dict...")
            self.set_attributes(spec)
        elif isinstance(spec, str): # create from string as name
            # if verbose >= 4:
            #     print("Creating pulse object by name:", spec)
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

    ## Valid absolute_time spec flag
    @property
    def valid_abs_time(self):
        return self.__valid_abs_time
    @valid_abs_time.setter
    def valid_abs_time(self, new_value):
        self.__valid_abs_time = bool(new_value)

    ## Get start and end times as attributes (will only work if appropriate params are set already)
    @property
    def start_time(self):
        assert self.valid_abs_time
        return self.attributes["absolute_time"]
    @property
    def end_time(self):
        try:
            assert "Width" in self.attributes
            assert "Plateau" in self.attributes
        except AssertionError:
            try:
                assert "w" in self.attributes
                assert "v" in self.attributes
            except AsserionError as AssE:
                raise AssE
            else:
                return self.start_time + self['w'] + self['v']
        else:
            return self.start_time + self["Width"] + self["Plateau"]

    def __getitem__(self, key):
        return self.attributes[key]

    def __setitem__(self, key, value):
        if key in _rc.PULSE_PARAMS:
            self.attributes[key] = value
        else:
            raise KeyError(" ".join(["Key", key, "is not defined as a valid pulse parameter."]))

    def __delitem__(self, key):
        del self.attributes[key]

    def print_info(self):
        '''
        Print all information about the pulse.
        '''
        print("Attributes for pulse", self.name)
        print(self.attributes)

    ###########################################################################
    ## Attribute import and input

    def set_attributes(self, input_attributes):
        '''
        Set attributes from an input dictionary input_attributes.
        '''
        for key, value in input_attributes.items():
            self[key] = value
            # if verbose >= 3:
            #     try:
            #         print("Pulse ", self.name, ": attribute ", key, " set to value ", value, sep = "")
            #     except KeyError:
            #         print("<unnamed pulse>: attribute", key, "set to value", value)
