## Additional functions for the PSICT MultiPulse driver

def pulseDefList2DictList(lPulseDefinitions, lKeyOrder):
    '''
    Convert raw definitions list (pulled from file) to list of keyed dicts
    '''
    lDefsOut = []
    ## Each item in the outermost list represents a complete pulse definition
    for lDef in lPulseDefinitions:
        oDef = {}
        for dDefValue, sDefKey in zip(lDef, lKeyOrder):
            oDef[sDefKey] = dDefValue
        ## Append dict to output list
        lDefsOut.append(oDef)
    ## Return list of dicts containing keyed pulse defs
    return lDefsOut
