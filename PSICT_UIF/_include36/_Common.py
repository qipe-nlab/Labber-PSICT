## Functions common to multiple modules

import re

def extract_relation_variables(input_string):
    '''
    Given an equation string (for a Labber channel relation), extract the valid python variable names (excluding those from modules such as numpy)
    '''
    re_pattern = re.compile('[A-Za-z_]+[A-Za-z0-9_]*\s*\.?\s*[A-Za-z0-9_]*')
    match_list = re.findall(re_pattern, input_string)
    extracted_vars = []
    ## Filter out matches with dots ('.')
    for match_string in match_list:
        if '.' in match_string:
            continue
        else:
            extracted_vars.append(match_string.strip())
    return extracted_vars
