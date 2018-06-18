## Testing the functionality of PSICT-UIF as a module

import sys

import PSICT_UIF

print("------------------------------------------------")
print("PSICT_UIF version is", PSICT_UIF.__version__)

## Initialise PSICT-UIF interface object
psictInterface = PSICT_UIF.psictUIFInterface(verbose = 1)
## Set script rcfile
psictInterface.load_script_rcfile("uif_script_rc_sample.py", verbose = 0)
# psictInterface.set_cwd(os.path.abspath(__file__))


## Manually set Labber executable path
# psictInterface.set_labber_exe_path("foo/bar/baz/quux/", verbose = 0)

## Set template and output hdf5 files
template_dir = "~/Google-Drive/Tokyo_research/labber_scripts/2018/06/Data_0613"
template_file = "K2018-06-13_030"
psictInterface.set_template_file(template_dir, template_file, verbose = 0)
output_dir = "~/Google-Drive/Tokyo_research/labber_scripts/2018/06/Data_0613"
output_file = "K2018-06-13_iteration_001"
psictInterface.set_output_file(output_dir, output_file, verbose = 1)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#### Instrument settings

pulse_sequence = "foo"

if pulse_sequence == "evaluate_SNR":

    ##
    readout_amplitude_list = [0.0, 1.0, 101]

    sideband = -1   # -1 for lower frequency

    readout_LO_power = 19        # dBm
    readout_IF_frequency = 90E6  # detuned from LO
    readout_frequency = 10.44E9  # optimal readout frequency
    readout_plateau = 400E-9

    qubit_LO_power = 16        # dBm
    qubit_IF_frequency = 100E6   # detuned from LO
    qubit_frequency = 7.91E9     # resonant frequency of qubit
    qubit_amplitude = 1.0
    qubit_width = 100E-9

    dead_plateau = 10E-6

    N_shots = 1
    digitizer_length = 1E-6

    SQPG_tr = 3
    ##

    point_values = {
            "SQPG":
                {
                    ## Parameters for overall pulse sequence - general SGPQ parameters
                    "main": {
                            "Truncation range": SQPG_tr, "Sample rate": 1E9,
                        },
                    ## Parameters which apply to all inverted pulses
                    "inverted": {"w": 0.0},

                    "buffer": {"time_reference": "absolute",
                            "time_offset": 0.0, "pulse_number": 1,
                            "a": 0.0, "w": 0.0, "v": 0.0, "f": 0.0,
                            "o": 4,
                        },
                    "qubit": {"relative_to": "buffer",
                            "time_offset": 0.0, "time_reference": "relative", "relative_marker": "end",
                            "a": qubit_amplitude, "w": qubit_width, "v": 0.0, "f": qubit_IF_frequency,
                            "o": 2,
                        },
                    "trigger": {"relative_to": "qubit",
                            "time_offset": 0.0, "time_reference": "relative", "relative_marker": "end",
                            "a": 1.5, "w": 0.0, "v": 20E-9, "f": 0.0,
                            "o": 4,
                        },
                    "readout": {"relative_to": "trigger",
                            "time_offset": 0.0, "time_reference": "relative", "relative_marker": "end",
                            "a": readout_amplitude_list[0], "w": 0.0, "v": readout_plateau, "f": readout_IF_frequency,
                            "o": 1,
                        },
                    "dead": {"relative_to": "readout",
                            "time_offset": 0.0, "time_reference": "relative", "relative_marker": "end",
                            "a": 0.0, "w": 0.0, "v": dead_plateau, "f": 0.0,
                            "o": 4,
                        },
                }, # end SQPG
            "Digitizer": {"Number of samples": digitizer_length * 500E6, "Number of averages": N_shots, 'Ch1 - Range': 4, 'Ch2 - Range': 4},
            "I": {"Modulation frequency": readout_IF_frequency, "Skip start": 0.0, "Length": 1E-6},
            "Q": {"Modulation frequency": readout_IF_frequency, "Skip start": 0.0, "Length": 1E-6},
            "RF1": {'Frequency': readout_frequency - sideband * readout_IF_frequency, 'Power': readout_LO_power},
            "RF2": {'Frequency': qubit_frequency - sideband * qubit_IF_frequency, 'Power': qubit_LO_power},
            "Manual": {"Value 1": qubit_width * SQPG_tr, "Value 2": 0},
        } # end point values

    iteration_values = {
            "SQPG": {"readout": {
                            "a": readout_amplitude_list,
                        }, # end readout
                     "dead": {
                            "f": [0.0, 150.0, 31],
                        },
                }, # end SQPG
            # "I": {"Skip start": [0.0, 10.0, 11]},
            # "Manual": {#"Value 2": [0, 9, 10],
                      # "Value 4": [0, 5, 6]},
        } # end iteration values

    iteration_order = [
            # ("Manual", "Value 4"),
            ("SQPG", ("dead", "Mod. frequency")),
            ("SQPG", ("readout", "Amplitude")),
            # ("I", "Skip start"),

            # ("Manual", "Value 2"),
        ] # end iteration order

    ## Channel relations - set available quantities (could be outsourced to rcfile?)
    channel_defs = {
            "SQPG":
                {   "main": {"SQPG_tr": "Truncation range", "SQPG_delay": "First pulse delay", "SQPG_sr": "Sample rate"},
                    "buffer": {"b_w": "Width", "b_v": "Plateau", "b_s": "Spacing",},
                    "dead": {"d_w": "Width", "d_v": "Plateau", "d_s": "Spacing",},
                    "qubit": {"q_w": "Width", "q_v": "Plateau", "q_s": "Spacing", "q_f": "Mod. frequency"},
                    "trigger": {"t_w": "Width", "t_v": "Plateau", "t_s": "Spacing",},
                    "readout": {"m_w": "Width", "m_v": "Plateau", "m_s": "Spacing", "r_f": "Mod. frequency"},
                }, # end SQPG
            "Manual":
                {
                    "max_q_w": "Value 1",
                },
        } # end relation channels

    channel_relations = {
            "SQPG":
                {
                    "main": {
                        'Number of points': ["(SQPG_delay + b_w + b_v + b_s + (SQPG_tr * d_w) + d_v + d_s + q_w + q_v + q_s + t_w + t_v + t_s + m_w + m_v + m_s) * SQPG_sr", ["SQPG_delay", "b_w", "b_v", "b_s", "d_w", "d_v", "d_s", "q_w", "q_v", "q_s", "t_w", "t_v", "t_s", "m_w", "m_v", "m_s", "SQPG_sr", "SQPG_tr"]],
                    },
                    "buffer": {
                        'Plateau': ["(max_q_w) - q_w*SQPG_tr", ["q_w", "SQPG_tr", "max_q_w"]],
                        'Spacing': ["(q_w / 2) * (SQPG_tr - 1)", ["q_w", "SQPG_tr"]],
                    },
                    "qubit": {
                        'Spacing': ["(q_w / 2) * (SQPG_tr - 1)", ["q_w", "SQPG_tr"]],
                    },
                    "readout": {
                        'Phase': ["(1/2 + 2 * r_f * (max_q_w + t_w + t_v + t_s)) * 180", ["max_q_w", "SQPG_tr", "r_f", "b_w", "b_v", "b_s", "q_w", "q_v", "q_s", "t_w", "t_v", "t_s", "SQPG_delay", "SQPG_sr"]],
                    },
                }, # end SQPG
        } # end channel relations
    ## end Rabi width
##
else:
    ## Point values
    point_values = {
            "SQPG":
                {
                    "main": {       # parameters for overall pulse sequence - general SGPQ parameters
                            "Truncation range": 5, "Sample rate": 1e9,
                        },
                    "inverted": {   # physical parameters that will be applied to all inverted pulses - the inverted pulse entries should not specify these, otherwise they will be overwritten
                            "a": 200, "w": 100e-9,
                        },
                    "AAA": \
                        {
                            "a": 2, "v": 200e-9,
                            "time_offset": 450e-9, "time_reference": "previous", "relative_to": "second", "pulse_number": 2, "relative_marker": "start",
                            'o': 1,
                        },
                    "BBB": \
                        {
                            "a": 5, "w": 95e-9,
                            "time_offset": 650e-9, "time_reference": "relative", "relative_to": "CCC", "relative_marker": "end", 'o': 1,
                        },
                    "CCC": \
                        {
                            "a": 5,
                            "time_offset": 400e-9, "time_reference": "absolute", "relative_to": "AAA", "pulse_number": 1, 'o': 1,
                        },
                    "dead": \
                        {
                            "a": 0, "w": 0, "v": 1e-6,
                            "time_offset": 200e-9, "time_reference": "previous",
                            "pulse_number": 99, 'o': 1,
                        },
                }, # end SQPG
            "Signal demodulation":
                {
                    "Skip start": 145e-9,
                },
        } # end point values

    ## Iteration values
    # iteration_values = [
    #         ["Digitizer", "Number of samples", [1e3, 1.5e3, 6]],
    #         ["SQPG", ("BBB", "Amplitude"), [0, 1e3, 3]],
    #     ]
    iteration_values = {
            "SQPG":
                {
                    "CCC": {
                            "w": [500e-9, 1500e-9, 3],
                           },
                    "AAA": {
                            "f": [0.0, 150, 6],
                        },
                },
            "Digitizer":
                {
                    "Number of samples": [100, 200, 3],
                },
            "Manual":
                {
                    "Value 1": [2, 3, 2],
                },
        } # end iteration values

    iteration_order = [
            ("SQPG", ("AAA", "Mod. frequency")),
            ("Digitizer", "Number of samples"),
            ("Manual", "Value 1"),
            ("SQPG", ("CCC", "Width")),
        ] # end iteration order

    ## Channel relations - set available quantities (could be outsourced to rcfile?)
    channel_defs = {
            "SQPG":
                {
                    # "main":
                    #     {
                    #         "delay": "First pulse delay",
                    #     },
                    "CCC":
                        {
                            "a_CCC": "Amplitude",
                        },
                }, # end SQPG
            "Digitizer":
                {
                    "Digitizer_n_avgs": "Number of averages",
                }, # end AWG_A
            "Manual":
                {
                    'Re': "Value 1",
                    'Im': "Value 2",
                },
        } # end relation channels

    ## Channel relations - set relation strings
    channel_relations = {
            "SQPG":
                {
                    "CCC": {
                        'Amplitude': ["Re - Im", ['Re', 'Im']],
                    },
                }, # end SQPG
            "Digitizer": {
                'Number of averages': ["Re + Im", ['Re', 'Im']],
            },
            "Manual": {
                'Value 2': ["Re * np.pi", ['Re']],
            },
        } # end channel relations

## End instrument parameter settings
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

## Set input pulse sequence
psictInterface.set_point_values(point_values, verbose = 0)
psictInterface.set_iteration_values(iteration_values, iteration_order, verbose = 1)
psictInterface.set_channel_relations(channel_defs, channel_relations, verbose = 0)

# Set up Labber MeasurementObject in case we would like to explicitly access it
# psictInterface.init_MeasurementObject(verbose = 0)
## explicit access to MeasurementObject
# print(psictInterface.MeasurementObject)

## Run measurement
psictInterface.perform_measurement(dry_run = True, verbose = 0)

# sys.exit()
