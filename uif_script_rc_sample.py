'''
This is the rc (resources) file for additional definitions required by the Labber-PSICT library.

It defines the quantities that the PSICT-UIF interface works with in a way that they are not hard-coded into the "procedural" code, but can in principle be changed for different scripts and so on. Note that the *parameter names cannot be changed*; those are hard-coded at this stage.

There are other rc files that are part of the PSICT-UIF package; these contain all the internal definitions and values which do not change from script to script. The specifications in this file are separate from those.

The key difference is as follows:
 - If the parameters in this rc file are not set up correctly, the code will run but the output may be nonsensical.
 - If the package rc files are not set up correctly, the code may fail to run.

This file may be copied alongside the script in future PSICT releases.

'''

## Iteration-permission options
outfile_iter_automatic = True   # Filename iteration will be carried out automatically
outfile_iter_user_check = True   # User will always be prompted to allow filename iteration

## Post-measurement script copies
script_copy_enabled = False   # option to copy the script to the specified target directory after the measurement has been run; subsumes script_rc_copy_enabled
script_copy_target_dir = "/Users/sam/Google-Drive/Tokyo_research/labber_scripts/2018/05/Data_0501/scripts/"
script_rc_copy_enabled = True  # option to copy this file (the script rcfile) - will be copied into the same directory as the script
script_copy_matches_output = True     # if set, the script copy will be renamed to match the output file name
script_copy_postfix = "_script"       # the postfix applied to the script name if it is set to match the output file by script_copy_matches_output

##
