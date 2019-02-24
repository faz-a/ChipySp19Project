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

#utc = pytz.utc #later, but this and the next line and the for loop in a functions(s)
counts, timestamps = [], []
for e in data_bucketed:
    counts.append(e['doc_count'])
    timestamps.append(get_utc_dt(e['key']))
#    timestamps.append(date.fromtimestamp(e['key']))
#    utc.localize(timestamps[-1])
counts_array = np.array(counts)
timestamps_array = np.array(timestamps)
print(counts_array, timestamps_array)

matplotlib.pyplot.title('Reddit Comments with the Term per Month')
matplotlib.pyplot.xlabel('Year')
matplotlib.pyplot.ylabel('Comments per Month')
matplotlib.pyplot.plot(timestamps_array, counts_array)
matplotlib.pyplot.show()