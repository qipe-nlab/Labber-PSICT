## Classes for parameter settings, more advanced than point values

from numbers import Number

class IterationSpec:
    '''
    Specify a parameter as an iteration.
    '''
    def __init__(self, spec_dict):
        self.set_iteration_spec(spec_dict)

    def __repr__(self):
        return "".join(["<Iteration: [", str(self.start_value), " --> ", str(self.stop_value), ", ", str(self.n_pts), "]>"])

    def __add__(self, other):
        if isinstance(other, Number):
            return self.start_value + other
            # return IterationSpec({
            #             "start_value": self.start_value + other,
            #             "stop_value": self.stop_value + other,
            #             "n_pts": self.n_pts,
            #         })
        else:
            raise NotImplementedError("Only numeric types can be added to an IterationSpec instance.")

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Number):
            return self.start_value - number
            # return IterationSpec({
            #             "start_value": self.start_value - other,
            #             "stop_value": self.stop_value - other,
            #             "n_pts": self.n_pts,
            #         })
        else:
            raise NotImplementedError("Only numeric types can be subtracted from an IterationSpec instance.")

    def __lt__(self, other):
        if isinstance(other, Number):
            return self.start_value < other
        else:
            raise NotImplementedError("Only numeric types can be compared to an IterationSpec instance.")
    def __gt__(self, other):
        if isinstance(other, Number):
            return self.start_value > other
        else:
            raise NotImplementedError("Only numeric types can be compared to an IterationSpec instance.")
    def __rlt__(self, other):
        return self > other
    def __rgt__(self, other):
        return self < other


    def set_iteration_spec(self, spec_dict):
        '''
        The keys used for the specifications are "parameter_name", "start_value", "stop_value", "n_pts", and an optional "pulse_number".
        '''
        self.start_value = spec_dict["start_value"]
        self.stop_value = spec_dict["stop_value"]
        self.n_pts = spec_dict["n_pts"]
