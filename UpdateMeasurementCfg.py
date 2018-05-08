#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import h5py

file_name = os.path.expanduser('~/Desktop/Spectrum.hdf5')
with h5py.File(file_name, 'r+') as f:
    # get keys for controlling step items
    print('Keys available:')
    print(f['Step list'].dtype.fields.keys())
    print()
    
    # print settings for first step item    
    print('Current settings of first step item')
    entry = f['Step list'][0]
    print(entry)
    print('Relations in use: ',entry['use_relations'])
    print()

    # update settings for relation
    entry['use_relations'] = True
    f['Step list'][0]= entry

    # print settings for first step item    
    print('New settings of first step item')
    print('Relations in use: ',f['Step list'][0]['use_relations'])
    