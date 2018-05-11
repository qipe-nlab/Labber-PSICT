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
data_path = 'C:\\Users\\qcpi\\Labber\\Data\\2018\\05\\Data_0511'

## Set up directories and open config file
ScriptTools.setExePath("C:\Program Files (x86)\Labber\Program")
labber_MO = ScriptTools.MeasurementObject(\
        os.path.join(reference_path, "hdf5_edit_04.hdf5"),\
        os.path.join(data_path, "hdf5_out_010.hdf5"))

## Run string_input_parser.py
exec(open("string_input_parser.py").read())

## Input variables
point_values = [
    "sr_1e9 dead_1000 delay_100 trim_0 nout_4 np_3 ptype_gauss tr_7 saz_0 e2e_1 epos_1 SSB_1 DRAG_0 IQ_1 dphi_90 cf_7850 if_-150",
    "a_100e-3   w_100   v_20    s_200   p_0  f_-100  o_QubitControl",
    "a_150e-3   w_200   v_46    s_200   p_0  f_+20   o_QubitControl",
    "a_200e-3   w_150   v_75    s_100   p_0  f_-250  o_QubitControl",
]
iter_var_1 = [1, "a", 0, 150e-3, 5]
iter_var_2 = [1, "w", 0, 300, 3]
iter_var_3 = [1, "v", 0, 200, 6]
iter_vars = [iter_var_3, iter_var_2, iter_var_1]
# labber_dummy = DummyMeasurementObject() # dummy MeasurementObject for debugging

## Set up InputStrParser object
Parser = InputStrParser()
Parser.set_MeasurementObject(labber_MO, verbose = False)

## Apply input - point and iteration values
Parser.set_all(point_values, iter_vars)

## Set up Hdf5Editor object
Editor = Hdf5Editor(labber_MO)

## Set channel spec parameters
Editor.add_channel_spec('a1', ["SQPG", 'a', 1])
Editor.add_channel_spec('w1', ["SQPG", 'w', 1])
Editor.add_channel_spec('v1', ["SQPG", 'v', 1])
Editor.add_channel_spec('s1', ["SQPG", 's', 1])
Editor.add_channel_spec('a2', ["SQPG", 'a', 2])
Editor.add_channel_spec('w2', ["SQPG", 'w', 2])
Editor.add_channel_spec('v2', ["SQPG", 'v', 2])
Editor.add_channel_spec('s2', ["SQPG", 's', 2])
Editor.add_channel_spec('a3', ["SQPG", 'a', 3])
Editor.add_channel_spec('w3', ["SQPG", 'w', 3])
Editor.add_channel_spec('v3', ["SQPG", 'v', 3])
Editor.add_channel_spec('s3', ["SQPG", 's', 3])
Editor.add_channel_spec('delay', ["SQPG", 'delay', 0])

## set relations
Editor.set_relation(['SQPG', 'a', 2], "a1", ['a1'])
Editor.set_relation(['SQPG', 'w', 2], "w1 + v1", ["w1", "v1"])

# sys.exit("Finished execution.")
## Run measurement
labber_MO.performMeasurement(return_data = False)

## Done! (in principle)
##
