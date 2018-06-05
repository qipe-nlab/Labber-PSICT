## Resource file for Pulse and related classes

## Lists of ordering and physical parameters
PHYS_PARAMS = [
                "a",     # amplitude
                "w",     # width
                "v",     # plateau
                ## etc
              ]
ORD_PARAMS = [
                "pulse_number",    # pulse number in sequence (initially)
                "time_reference",  # what the passed-in time will be relative to (eg absolute, previous, or a pulse number)
                "absolute_time",   # time relative to the start of the pulse sequence
                "is_inverted",     # is the pulse specified as an "off" signal state?
                "is_measurement",  # is the pulse a measurement pulse?
                ## etc
             ]
