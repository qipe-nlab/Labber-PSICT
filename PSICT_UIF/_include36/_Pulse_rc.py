## Resource file for Pulse and related classes

## Lists of ordering and physical parameters
NAME_PARAMS = ["name"]
PHYS_PARAMS = [
                "a",     # amplitude
                "w",     # width
                "v",     # plateau
                ## etc
              ]
ORD_PARAMS = [
                "pulse_number",    # pulse number in sequence (set by user initially; changed by post-import in OutputPulseSeq)
                "time_reference",  # what the passed-in time will be relative to (eg absolute, previous, or a pulse number)
                "absolute_time",   # time relative to the start of the pulse sequence
                "is_inverted",     # is the pulse specified as an "off" signal state?
                "is_measurement",  # is the pulse a measurement pulse?
                ## etc
             ]

## all single-pulse parameter names (for checking validity etc)
ALL_PARAMS = [param for param_list in [NAME_PARAMS, PHYS_PARAMS, ORD_PARAMS] for param in param_list]

## Overall pulse sequence parameters
SEQ_PARAMS = [
                "control_freq",    # microwave input control frequency
            ]

## Pulse sorting
pulse_sort_attr = "absolute_time"
