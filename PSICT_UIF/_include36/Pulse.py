## Class for storing individual pulses and their attributes
##  Non-"programming" attributes can be either physical or non-physical (ordering);
##  the intention is for these to be handled differently by the input-output
##  pulse conversion algorithm

import PSICT_UIF._include36._Pulse_rc as _rc

class Pulse:
    '''
    Docstring for Pulse class.
    '''
    def __init__(self, name):
        self.name = name     # the pulse name will be used as a reference when setting relations etc
        self.phys_attr = {}  # physical attributes
        self.ord_attr = {}   # ordering attrbutes

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
        return self.__name
    @name.setter
    def name(self, name):
        # print("Executing setter.")
        self.__name = name

    ## physical attributes
    @property
    def phys_attr(self):
        return self.__phys_attr
    @phys_attr.setter
    def phys_attr(self, new_dict):
        self.__phys_attr = new_dict

    ## ordering attributes
    @property
    def ord_attr(self):
        return self.__ord_attr
    @ord_attr.setter
    def ord_attr(self, new_dict):
        self.__ord_attr = new_dict

    def __getitem__(self, key):
        if key == "name":
            return self.name
        elif key in self.phys_attr:
            return self.phys_attr[key]
        elif key in self.ord_attr:
            return self.ord_attr[key]
        else:
            raise KeyError(key)


    ###########################################################################
    ## Attribute import and input

    def set_attributes(self, input_attributes, *, verbose = 0):
        '''
        Set attributes from the dict input_attributes.
        '''
        for key, value in input_attributes.items():
            if key == "name":
                ## update name
                self.name = value
                if verbose >= 2:
                    print("Pulse name updated to:", self.name)
            elif key in _rc.PHYS_PARAMS:
                ## update physical attributes
                self.phys_attr[key] = value
                if verbose >= 2:
                    print("Pulse physical attribute", key, "updated to", value)
            elif key in _rc.ORD_PARAMS:
                ## update ordering attribute
                self.ord_attr[key] = value
                if verbose >= 2:
                    print("Pulse ordering attribute", key, "updated to", value)
            else:
                raise KeyError(" ".join(["Key", key, "is not defined as a valid pulse parameter."]))
