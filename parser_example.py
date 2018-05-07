## String input parsing using string_input_parser.py example script
## Author: Sam Wolski
## Contains minimal usage with associated Labber functions; should run as a self-contained script.

import Labber
from Labber import ScriptTools
import os      # for os.path.join() and os.path.isfile()
import sys     # for sys.exit()

# print(Labber.version)

# Path of reference measurements files
reference_path = 'C:\\Users\\qcpi\\Labber\\Data\\reference_config'
# Path for data; if folder does not exist, please manually create it before
data_path = 'C:\\Users\\qcpi\\Labber\\Data\\2018\\05\\Data_0507'

## Set up directories and open config file
ScriptTools.setExePath("C:\Program Files (x86)\Labber\Program")
labber_MO = ScriptTools.MeasurementObject(\
        os.path.join(reference_path, "unit_tests.hdf5"),\
        os.path.join(data_path, "ut_out_017.hdf5"))

## quick implementation in main file to check functionality
file_MO_out = labber_MO.sCfgFileOut
print("The output path specified is\n", file_MO_out, sep = "")
## check if output file already exists
flag_outfile_exists = os.path.isfile(file_MO_out)
if flag_outfile_exists:
    errmsg = "".join(["The output file\n\t", file_MO_out, "\nalready exists; execution halted to prevent appending data."])
    sys.exit(errmsg)
else:
    print("Output file does not already exist, continuing...")
sys.exit("Exit before code is actually run.")

## Run string_input_parser.py
exec(open("string_input_parser.py").read())

## Input variables
point_values = [
    "sr_1e9 dead_1000 delay_400 trim_0 nout_4 np_3 ptype_gauss tr_7 saz_0 e2e_1 epos_1 SSB_1 DRAG_0 IQ_1 dphi_90 cf_7850 if_-150",
    "a_200e-3   w_400   v_600  s_0  p_0  f_20     o_QubitControl",
    "a_300e-3   w_400   v_0    s_11  p_0  f_-20   o_QubitControl",
    "a_600e-3   w_400   v_0    s_0   p_0  f_-300  o_QubitControl",
]
iter_var_1 = [1, "a", 0.0, 1.0, 11]
iter_var_2 = [0, "delay", 200, 500, 6]
iter_var_3 = [2, "s", 100, 400, 11]
iter_vars = [iter_var_1, iter_var_2, iter_var_3]
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
