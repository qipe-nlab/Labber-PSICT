## Resource file for Pulse and related classes

## Lists of ordering and physical parameters
NAME_PARAMS = ["name"]
PHYS_PARAMS = [
                "a",     # amplitude
                "w",     # width
                "v",     # plateau
                "s",     # spacing
                ## etc
              ]
ORD_PARAMS = [
            ## Numbering
                "pulse_number",    # pulse number in sequence (set by user initially; changed by post-import in OutputPulseSeq)
            ## Timing
                "time_reference",  # what the passed-in time will be relative to (eg absolute, previous, or a pulse number); note that the unused options can still be set without causing an error
                "absolute_time",   # time relative to the start of the pulse sequence (requires time_reference to be "absolute")
                "relative_to",     # which pulse number the time offset should be taken relative to (requires time_reference to be "relative" or "previous")
                "relative_marker", # 'start' or 'end', specifying from which point of the reference pulse we begin counting (requires time_reference to be 'relative' or 'previous')
                # "ref_pulse_name",  # name of the pulse to be used as time reference (requires time_reference to be 'relative')
                "time_offset",     # what the time offset will be from the relative pulse (requires time_reference to be "relative" or "previous")
            ## Types
                "is_inverted",     # is the pulse specified as an "off" signal state?
                "is_measurement",  # is the pulse a measurement pulse?
            ##
            ]

## all single-pulse parameter names (for checking validity etc)
PULSE_PARAMS = [param for param_list in [NAME_PARAMS, PHYS_PARAMS, ORD_PARAMS] for param in param_list]

## Overall pulse sequence parameters
MAIN_PARAMS = [
                "control_freq",    # microwave input control frequency
            ]


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
## Fixed and always-default parameters

## These parameters have defaults, as they must always be set for the script to actually work!
PULSE_PARAM_DEFAULTS = {
            "w": 0.0,   # 0 width
            "v": 0.0,   # 0 plateau
            "s": 0.0,   # 0 spacing (not currently used)
        }

## These (main) parameters are fixed and cannot be changed using Labber-PSICT; these are *always* set to the following values when using the script.
CONST_MAIN_PARAMS = {
                "Edge-to-edge pulses": 1,  # ON
                "Pulse type": 2,           # Gaussian
            }

## Pulse sorting - DO NOT CHANGE!
pulse_sort_attr = "absolute_time"
