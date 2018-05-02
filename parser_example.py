## String input parsing using string_input_parser.py example script
## Author: Sam Wolski
## Contains minimal usage with associated Labber functions; should run as a self-contained script.

import Labber
from Labber import ScriptTools

print(Labber.version)

## Set up directories and open config file
ScriptTools.setExePath("path/to/executable")
labber_MO = ScriptTools.MeasurementObject("reference_file.hdf5", "output_file.hdf5")

## Run string_input_parser.py
exec(open("string_input_parser.py").read())

## Input variables
point_values = [
    "sr_1e9 dead_1000 delay_400 trim_0 nout_4 np_3 ptype_gauss tr_7 saz_0 e2e_1 epos_3 SSB_1 DRAG_0 IQ_1 dphi_90 cf_7850 if_-150",
    "a_2   w_400   v_25  s_0  p_-90  f_20    o_QubitControl",
    "a_2   w_400   v_0  s_11  p_-90  f_-20   o_QubitControl",
    "a_2   w_400   v_0  s_0   p_-90  f_-300   o_QubitControl",
]
iter_var_1 = [3, "Amplitude", 0.0, 1.0, 25]
iter_var_2 = [0, "Phase difference", -90.0, 90.0, 101]
iter_vars = [iter_var_1, iter_var_2]
# labber_dummy = DummyMeasurementObject() # dummy MeasurementObject for debugging

## Set up InputStrParser object
Parser = InputStrParser()
Parser.set_MeasurementObject(labber_MO)

## Apply input
Parser.set_all(point_values, iter_vars)

## Run measurement
labber_MO.performMeasurement(return_data = False)

## Done! (in principle)
##
