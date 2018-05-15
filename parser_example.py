## String input parsing using string_input_parser.py example script
## Author: Sam Wolski
## Contains minimal usage with associated Labber functions; should run as a self-contained script.

import Labber
from Labber import ScriptTools
import os      # for os.path.join() and os.path.isfile()
import sys     # for sys.exit()

# print(Labber.version)

## Run string_input_parser.py
exec(open("string_input_parser.py").read())

## Path of reference measurements files
reference_path = 'C:\\Users\\qcpi\\Labber\\Data\\reference_config'
## Path for data; if folder does not exist, please manually create it before
output_path = 'C:\\Users\\qcpi\\Labber\\Data\\2018\\05\\Data_0515'
## Config file names
template_file_name = "alpha_01"
output_file_name = "alpha_out_001"

FileMgr = FileManager(reference_path, template_file_name, output_path, output_file_name)

## Set up directories and open config file
ScriptTools.setExePath("C:\Program Files (x86)\Labber\Program")
labber_MO = ScriptTools.MeasurementObject(\
        FileMgr.get_reference_file(),\
        FileMgr.get_output_file())


## Input variables
point_values = [
    "sr_1e9 dead_1000 delay_100 trim_0 nout_4 np_3 ptype_gauss tr_7 saz_0 e2e_1 epos_1 SSB_1 DRAG_0 IQ_1 dphi_90",
    "a_100e-3   w_100   v_20    s_200   p_0  f_-100  o_QubitControl cf_1750 if_-150",
    "a_150e-3   w_200   v_46    s_200   p_0  f_+20   o_QubitControl cf_0 if_0",
    "a_200e-3   w_150   v_75    s_100   p_0  f_-250  o_QubitControl cf_1000 if_0",
]
iter_var_1 = [4, "a", 0, 150e-3, 2]
iter_var_2 = [1, "w", 0, 300, 3]
iter_var_3 = [1, "v", 0, 200, 2]
iter_vars = [iter_var_3, iter_var_2, iter_var_1]
# labber_dummy = DummyMeasurementObject() # dummy MeasurementObject for debugging

## Set up InputStrParser object
Parser = InputStrParser()
Parser.set_MeasurementObject(labber_MO, verbose = False)

## Apply input - point and iteration values
Parser.set_all(point_values, iter_vars)

## Update values for Manual instrument using default Labber API
labber_MO.updateValue("Manual - Value 1", 0.5, 'SINGLE')
labber_MO.updateValue("Manual - Value 2", 0.0, 'START')
labber_MO.updateValue("Manual - Value 2", 5.0, 'STOP')
labber_MO.updateValue("Manual - Value 2", 3, 'N_PTS')

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
Editor.add_channel_spec('man1', ["Manual", 'Value 1', 0])
Editor.add_channel_spec('man2', ["Manual", 'Value 2', 0])
Editor.add_channel_spec('man3', ["Manual", 'Value 3', 0])
Editor.add_channel_spec('man4', ["Manual", 'Value 4', 0])
Editor.add_channel_spec('man5', ["Manual", 'Value 5', 0])
Editor.add_channel_spec('man6', ["Manual", 'Value 6', 0])

## set relations
Editor.set_relation(['SQPG', 'a', 2], "a1", ['a1'])
Editor.set_relation(['SQPG', 'w', 2], "man1 + man2", ["man1", "man2"])

# sys.exit("Finished execution.")
## Run measurement
labber_MO.performMeasurement(return_data = False)

## clean the FileManager object
FileMgr.clean()

## Done! (in principle)
##
