params_main_config = {
        "sr":     float,  # sample rate
        # "npts":   float,  # number of points - calculated from dead, sr, and pulse sequence
        "dead":   float,  # Dead time (relaxation of qubit after pulse sequence) in ns
        "delay":  float,  # first pulse delay in ns
        "trim":   int,    # Trim waveform to sequence (bool)
        "nout":   int,    # number of outputs
        "np":     int,    # number of pulses
        "ptype":  str,    # pulse type
        "tr":     int,    # truncation range
        "saz":    int,    # start at zero (bool)
        "e2e":    int,    # edge-to-edge pulses (bool)
        "epos":   int,    # edge position
        "SSB":    int,    # use SSB mixing (bool)
        "DRAG":   int,    # use DRAG (bool)
        ## these are 'main' parameters, but they are set per-pulse in post-processing:
        "IQ":     float,  # I/Q ratio
        "dphi":   float,  # Phase diff.
        ## IF/Control frequency specification
        "cf":     float,  # Control frequency in MHz
        "if":     float,  # IF frequency (to be modulated by Mod. freq) in MHz
    }

params_pulse_config = {
        "a":      float,  # Amplitude
        "w":      float,  # Width in ns
        "v":      float,  # Plateau in ns
        "s":      float,  # Spacing in ns
        "p":      float,  # Phase
        "f":      float,  # Mod. frequency (offset from IF frequency) in MHz
        "o":      str,    # Output
    }

## dict for shortcode conversion
shortcodes = {
    ## main
    "sr":       "Sample rate",
    "npts":     "Number of points",
    "delay":    "First pulse delay",
    "trim":     "Trim waveform to sequence",
    "nout":     "Number of outputs",
    "np":       "# of pulses",
    "ptype":    "Pulse type",
    "tr":       "Truncation range",
    "saz":      "Start at zero",
    "e2e":      "Edge-to-edge pulses",
    "epos":     "Edge position",
    "SSB":      "Use SSB mixing",
    "DRAG":     "Use DRAG",
    ## additional
    "dead":     "Dead time",
    "cf":       "Control frequency",
    "if":       "IF frequency",
    ## pulse
    "a":        "Amplitude",
    "w":        "Width",
    "v":        "Plateau",
    "s":        "Spacing",
    "p":        "Phase",
    "f":        "Mod. frequency",
    "o":        "Output",
    ## main applied to pulses
    "IQ":       "Ratio I/Q",
    "dphi":     "Phase diff.",
}

## lists of shortcodes for sorting tests
add_shortcodes = ["dead", "cf", "if"]
pulseapp_shortcodes = ["IQ", "dphi"]

###############################################################################
## Conversions for nonstandard input types
##  eg To specify a channel name instead of the expected value (int), conversion
##  rules must be specified here.
##  NB Boolean values are converted using if ... else during post-processing

## main config
convert_nout = {1: 0, 2: 1, 3: 2, 4: 3}
convert_ptype = {"gauss": 0, "square": 1, "ramp": 2}
MAX_PULSES = 8         # maximum number of pulses supported by driver

## pulse config
convert_out = {"QubitControl": 0, "QubitReadout": 1, "MagnonControl": 2, "MagnonReadout": 3}
##      ## NB pulse output names cannot contain underscores (_) or spaces


###############################################################################

## post-processing functionality
def post_process_params_values(parserObj, in_main = [], in_pulses = [], verbose = False):
    '''
    Defines post-processing operations to be carried out on the raw input value of the specified parameter(s); these are carried out on the specified input parameters when the function is called.

    Dependencies are calculated based on stored values within the parserObj (InputStrParser instance). parserObj values are modified in-place; the function also returns the post-processed values of any parameters passed in (but _not_ their potential dependents!) such that this function can be used with iteration variables.

    Currently, any dependencies must be set explicitly in the InputStrParser parserObj (and are not read from the reference file). A warning or error will be raised (don't know which just yet...), and so this may cause undefined behaviour.

    Twofold main purpose:
        - Converts more descriptive strings (eg for output channel name)
            into integer switch values
        - Calculates parameters based on specified dependencies
            (eg pulse spacing as a function of pulse width)

    - out_main variable names (ie output) must match the variable names on the
        instrument as these will be passed directly to the Labber API
        updateValue methods.
    - Pulses should be referred to by their actual number (starting at 1, not 0).
    - This function should be called any time parameters are updated, eg setting iteration variables after main variables have already been set.
    '''
    if verbose: print("Beginning post-processing...")
    ## output dicts
    # out_main = {}
    # out_pulse = {}
    # out_add = {}     # additional parameters not passed directly to labber

    ## main values
    if "sr" in in_main:
        parserObj.main_values_out[shortcodes["sr"]] = in_main["sr"]
    # parserObj.main_values_out["Number of points"] = in_main["npts"]
    if "delay" in in_main:
        parserObj.main_values_out[shortcodes["delay"]] = in_main["delay"]*1e-9   # ns
    if "trim" in in_main:
        parserObj.main_values_out[shortcodes["trim"]] = 0 if in_main["trim"] == 0 else 1
    if "nout" in in_main:
        parserObj.main_values_out[shortcodes["nout"]] = convert_nout[in_main["nout"]]
    if "np" in in_main:
        parserObj.main_values_out[shortcodes["np"]] = in_main["np"] if in_main["np"] <= MAX_PULSES else MAX_PULSES
    if "ptype" in in_main:
        parserObj.main_values_out[shortcodes["ptype"]] = convert_ptype[in_main["ptype"]]
    if "tr" in in_main:
        parserObj.main_values_out[shortcodes["tr"]] = in_main["tr"]
    if "saz" in in_main:
        parserObj.main_values_out[shortcodes["saz"]] = 0 if in_main["saz"] == 0 else 1
    if "e2e" in in_main:
        parserObj.main_values_out[shortcodes["e2e"]] = 0 if in_main["e2e"] == 0 else 1
    if "epos" in in_main:
        parserObj.main_values_out[shortcodes["epos"]] = in_main["epos"]
    if "SSB" in in_main:
        parserObj.main_values_out[shortcodes["SSB"]] = 0 if in_main["SSB"] == 0 else 1
    if "DRAG" in in_main:
        parserObj.main_values_out[shortcodes["DRAG"]] = 0 if in_main["DRAG"] == 0 else 1
    ## additional data - not passed directly
    if "dead" in in_main:
        parserObj.add_values_out[shortcodes["dead"]] = in_main["dead"]*1e-9   # ns
    if "cf" in in_main:
        parserObj.add_values_out[shortcodes["cf"]] = in_main["cf"]*1e6        # MHz
    if "if" in in_main:
        parserObj.add_values_out[shortcodes["if"]] = in_main["if"]*1e6             # MHz
    if "cf" in in_main and "if" in in_main:
        parserObj.add_values_out["LO frequency"] = parserObj.add_values_out[shortcodes["cf"]] - parserObj.add_values_out[shortcodes["if"]]
    ## status print
    # if verbose:
        # print("(main) Sample rate:", parserObj.main_values_out["Sample rate"])
        # # print("(main) Number of points:", parserObj.main_values_out["Number of points"])
        # print("(main) First pulse delay:", parserObj.main_values_out["First pulse delay"])

    ## pulse values
    # npulses = len(in_pulse)
    # if verbose: print("(pulse) Number of pulses:", npulses)
    for pulse_num in in_pulses:
        # print(pulse_num)
        in_pulse = in_pulses[pulse_num]    # unpacks number, dict from list of lists

        # print(parserObj.pulse_values_out)
        ## init sub-dict for each pulse if nonexistent
        if not pulse_num in parserObj.pulse_values_out:
            parserObj.pulse_values_out[pulse_num] = {}

        if "a" in in_pulse:
            parserObj.pulse_values_out[pulse_num][shortcodes["a"]] = in_pulse["a"]
        if "w" in in_pulse:
            parserObj.pulse_values_out[pulse_num][shortcodes["w"]] = in_pulse["w"]*1e-9  # ns
        if "v" in in_pulse:
            parserObj.pulse_values_out[pulse_num][shortcodes["v"]] = in_pulse["v"]*1e-9  # ns
        if "s" in in_pulse:
            parserObj.pulse_values_out[pulse_num][shortcodes["s"]] = in_pulse["s"]*1e-9  # ns
        if "p" in in_pulse:
            parserObj.pulse_values_out[pulse_num][shortcodes["p"]] = in_pulse["p"]
        ## modulation frequency calculations: potential sideband switching
        ## same sign => same sideband
        if "f" in in_pulse:
            freq_offset = in_pulse["f"]*1e6      # MHz
            if parserObj.add_values_out[shortcodes["if"]]*(parserObj.add_values_out["IF frequency"] + freq_offset) >= 0:
                parserObj.pulse_values_out[pulse_num][shortcodes["f"]] = abs(parserObj.add_values_out["IF frequency"] + freq_offset)
            ## sideband switching
            else:
                print("*** WARNING: Specified frequency offset induces a sideband switch for pulse ", pulse_num, "; defaulting to 0.", sep = "")
                parserObj.pulse_values_out[pulse_num][shortcodes["f"]] = abs(parserObj.add_values_out["IF frequency"])
        ##
        if "o" in in_pulse:
            parserObj.pulse_values_out[pulse_num][shortcodes["o"]] = convert_out[in_pulse["o"]]
        ## overall parameters applied to pulses individually
        if "IQ" in in_main:
            parserObj.pulse_values_out[pulse_num][shortcodes["IQ"]] = in_main["IQ"]
        if "dphi" in in_main:
            parserObj.pulse_values_out[pulse_num][shortcodes["dphi"]] = in_main["dphi"]

        ## status print
        if verbose:
            print("(pulse)", pulse_num, "Amplitude:", parserObj.pulse_values_out[pulse_num]["Amplitude"])
            print("(pulse)", pulse_num, "Width:", parserObj.pulse_values_out[pulse_num]["Width"])
            print("(pulse)", pulse_num, "Plateau:", parserObj.pulse_values_out[pulse_num]["Plateau"])
            print("(pulse)", pulse_num, "Mod. Frequency:", parserObj.pulse_values_out[pulse_num]["Mod. frequency"])

    ##

    # # # # # # # # # # # # # # # # #
    ## Additional calculations

    ## Number of points from pulse sequence, dead time, and sample rate
    ##   Calculation depends on whether or not pulses are e2e
    if parserObj.main_values_out[shortcodes["e2e"]]:
        total_time = parserObj.main_values_out[shortcodes["delay"]] + sum([parserObj.pulse_values_out[xx][shortcodes["w"]] + \
                parserObj.pulse_values_out[xx][shortcodes["v"]] + parserObj.pulse_values_out[xx][shortcodes["s"]] for xx in range(1, parserObj.npulses+1)]) \
                + parserObj.add_values_out[shortcodes["dead"]]
    else:
        total_time = parserObj.main_values_out[shortcodes["delay"]] + sum([parserObj.pulse_values_out[xx][shortcodes["s"]] for xx in range(1, parserObj.npulses+1)]) + parserObj.add_values_out[shortcodes["dead"]]
    if verbose: print("Total time for pulse sequence (incl dead time):", str(total_time), "ns")
    parserObj.main_values_out["Number of points"] = int(parserObj.main_values_out[shortcodes["sr"]]*total_time)
    if verbose: print("Calculated number of points:", str(parserObj.main_values_out["Number of points"]))

    # # # # # # # # # # # # # # # # #


    ## complete debug printing
    if verbose:
        print("Main parameters:")
        print(parserObj.main_values_out)
        print("Pulse parameters:")
        print(parserObj.pulse_values_out)

    ## completion status message
    if verbose: print("Post-processing completed.")

    ## get return values corresponding to input params
    ## main - contains add
    out_main = {}
    for param_code in in_main:
        ## param is part of additional params
        if param_code in add_shortcodes:
            out_main[shortcodes[param_code]] = parserObj.add_values_out[shortcodes[param_code]]
        ## param is main but set for each pulse
        elif param_code in pulseapp_shortcodes:
            continue
        ## param is ordinary main param
        else:
            out_main[shortcodes[param_code]] = parserObj.main_values_out[shortcodes[param_code]]

    ## pulse
    out_pulse = {}
    # print(in_pulses)
    for pulse_num in in_pulses:
        in_pulse_data = in_pulses[pulse_num]
        pulse_dict = {}
        for param_code in in_pulse_data:
            pulse_dict[shortcodes[param_code]] = parserObj.pulse_values_out[pulse_num][shortcodes[param_code]]
        out_pulse[pulse_num] = pulse_dict

    ## output
    return out_main, out_pulse

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
