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
            ## Numbering
                "pulse_number",    # pulse number in sequence (set by user initially; changed by post-import in OutputPulseSeq)
            ## Timing
                "time_reference",  # what the passed-in time will be relative to (eg absolute, previous, or a pulse number); note that the unused options can still be set without causing an error
                "absolute_time",   # time relative to the start of the pulse sequence (requires time_reference to be "absolute")
                "relative_to",     # which pulse number the time offset should be taken relative to (requires time_reference to be "relative" or "previous")
                "time_offset",     # what the time offset will be from the relative pulse (requires time_reference to be "relative" or "previous")
            ## Types
                "is_inverted",     # is the pulse specified as an "off" signal state?
                "is_measurement",  # is the pulse a measurement pulse?
            ##
            ]

## all single-pulse parameter names (for checking validity etc)
ALL_PARAMS = [param for param_list in [NAME_PARAMS, PHYS_PARAMS, ORD_PARAMS] for param in param_list]

## Overall pulse sequence parameters
SEQ_PARAMS = [
                "control_freq",    # microwave input control frequency
            ]

## Pulse sorting
pulse_sort_attr = "absolute_time"
