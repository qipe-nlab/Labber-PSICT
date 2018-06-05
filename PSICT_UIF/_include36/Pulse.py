## Class for storing individual pulses and their attributes
##  Non-"programming" attributes can be either physical or non-physical (ordering);
##  the intention is for these to be handled differently by the input-output
##  pulse conversion algorithm

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


    ###########################################################################
