# -*- coding: utf-8 -*-

import sys
import re
import json
import codecs
import numpy as np
import pandas as pd 

from itertools import islice, chain
movie_basic_info_path = './data/movie_basic_info.json'
def lines_per_n(f, n):
    for line in f:
        yield ''.join(chain([line], islice(f, n - 1)))

def read_multi_json(file):
    data = []
    i = 0
    temp = []
    for line in codecs.open(file, encoding='utf-8'):
        if line == '}\n':
            
            temp.append(line)
            sample = json.loads(''.join(temp))
            i += 1
            temp = []
            data.append(sample)
        else:
            if 'ISODate' in line:
                line = line.replace('ISODate(', '').replace(')', '')
            if 'NumberInt' in line:
                line = line.replace('NumberInt(', '').replace(')', '')
            temp.append(line)
    return data

def get_movie_basic_info(path=movie_basic_info_path):
    """
    return a dict of {"id": {"Boxofficd":xx, "EnName":xx, "Name":xx, "Year": xx}}
    """
    return json.load(open(path))

