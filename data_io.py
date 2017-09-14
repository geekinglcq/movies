# -*- coding: utf-8 -*-

import sys
import re
import json
import codecs
import numpy as np
import pandas as pd 

from itertools import islice, chain
def lines_per_n(f, n):
    for line in f:
        yield ''.join(chain([line], islice(f, n - 1)))

def read_multi_json(file):
    data = []
    i = 0
    print(i)
    temp = []
    for line in codecs.open(file, encoding='utf-8'):
        if line == '}\n':
            
            temp.append(line)
            # print(''.join(temp))
            sample = json.loads(''.join(temp))
            # print(sample)
            print(i)
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
    # return data
    # with open(file, encoding='utf-8') as f:
    #     for line in f:
    #         while True:
    #             try:
    #                 sigle_json = json.loads(line)
    #                 data.append(sigle_json)
    #                 print(i)
    #                 i += 1
    #                 break
    #             except ValueError:
    #                 line += next(f)


