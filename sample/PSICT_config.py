## Logging
logging_config = {
    'console_log_enabled': True,
    'console_log_level': 25, # SPECIAL
    'console_fmt': '[%(asctime)s] %(message)s',
    'console_datefmt': '%y-%m-%d %H:%M:%S',
    ##
    'file_log_enabled': True,
    'file_log_level': 15,    # VERBOSE
    'file_fmt': '%(asctime)s %(levelname)-8s %(name)s: %(message)s',
    'file_datefmt': '%y-%m-%d %H:%M:%S',
    'log_dir': 'logs',
    'log_file': 'psict_{:%y%m%d_%H%M%S}',
}

## Parameter value pre-processing and conversion
parameter_pre_process = {
        "SQPG": {
            "pulse": {
                "o": { # Actual channel number is 1 more than the Labber lookup table specification
                    1: 0,
                    2: 1,
                    3: 2,
                    4: 3,
                }, # end o (Output)
            }, # end pulse
        }, # end SQPG
    }

## Iteration permissions
outfile_iter_automatic = True
outfile_iter_user_check = True

## Post-measurement script copy options
script_copy_enabled = True        # Copy the measurement script to the specified target directory
script_copy_postfix = '_script'   # postfixed to the script name after copying
