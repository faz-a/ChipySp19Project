# -*- coding: utf-8 -*-
"""
Created on Thu Feb 14 22:36:41 2019
@author: Fazal
"""

import requests, matplotlib, pytz
import numpy as np
import datetime as dt
from datetime import date
from datetime import datetime
from pytz import timezone
from tzlocal import get_localzone
import pandas as pd

def get_response(q, after, before):
    parameters = {"q":q,"aggs":aggs, "frequency":frequency, "size":size, "after":after, "before":before}
    response=requests.get("https://api.pushshift.io/reddit/search/comment/",params=parameters)
    print('url used is', response.url)
    data = response.json()
    return data

def get_epoch(aYear, aMonth):
    local = get_localzone()
    utc = pytz.utc
    return int(utc.localize(datetime(aYear, aMonth, 1, 0, 0)).timestamp())

def get_utc_dt(epoch):
    local_dt = dt.datetime.fromtimestamp(epoch)
    utc = pytz.utc
    utc_dt_aware = local_dt.astimezone(utc)
    return datetime(utc_dt_aware.year, utc_dt_aware.month, utc_dt_aware.day)

after_month, after_year = int(input('enter a start month for the search')), int(input('enter a start year for the search'))
before_month, before_year = int(input('enter an end month for the search')), int(input('enter an end year for the search'))

before = get_epoch(before_year, before_month)
after = get_epoch(after_year, after_month)
print('the below should be in a function!')
q = '"' + input('enter a word or phrase: ') + '"'
aggs = 'created_utc'
frequency = 'month'
size = 0

parameters = {"q" : q, "aggs" : aggs, "frequency" : frequency, "size" : size, "after" : after, "before" : before}

data_aggs = get_response(q, after, before)
data_created_utc = data_aggs['aggs']
data_bucketed = data_created_utc['created_utc']

def return_arrays(bucketed_counts, reverse):
    """takes in a list of dictionaries; returns a pandas dataframe"""
    d1 = list(bucketed_counts[0].keys())
#    if "count" in d1:
#        d1.sort()
#    elif "doc_count" in d1
#        d1.sort(reverse = True)
#    else:
#        #raise an error...
    d1.sort(reverse = reverse)
    count, timestamp = d1[1], d1[0]
    counts, timestamps = [], []
    for e in bucketed_counts: #here, it means "for e in data_bucketed"
        counts.append(e[count])
        print("e:", e, "count:", count, "timestamp:", timestamp, "type(count):", type(count), "type(timestamp):", type(timestamp))
        print('count: ', e[count])
        print('timestamp: ', e[timestamp])
        timestamps.append(get_utc_dt(e[timestamp]))
    df = pd.DataFrame()
    #df['Counts'], df['Timestamps'] = counts, timestamps
    df['Timestamps'], df['Counts'] = timestamps, counts
    return df


dataframe = return_arrays(data_bucketed, True)
dataframe.set_index('Timestamps', inplace=True)
dataframe.plot()
