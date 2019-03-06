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

def get_response_term(q, after, before):
    parameters = {"q":q,"aggs":aggs, "frequency":frequency, "size":size, "after":after, "before":before}
    response=requests.get("https://api.pushshift.io/reddit/search/comment/",params=parameters)
    print('url used is', response.url)
    data = response.json()
    return data

def get_response_all():
    response = requests.get("https://beta.pushshift.io/reddit/statistics")
    return response.json()['comment_all_activity']

def get_epoch(aYear, aMonth):
    local = get_localzone()
    utc = pytz.utc
    return int(utc.localize(datetime(aYear, aMonth, 1, 0, 0)).timestamp())

def get_utc_dt(epoch):
    local_dt = dt.datetime.fromtimestamp(epoch)
    utc = pytz.utc
    utc_dt_aware = local_dt.astimezone(utc)
    return datetime(utc_dt_aware.year, utc_dt_aware.month, utc_dt_aware.day)

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
#        print("e:", e, "count:", count, "timestamp:", timestamp, "type(count):", type(count), "type(timestamp):", type(timestamp))
#        print('count: ', e[count])
#        print('timestamp: ', e[timestamp])
        timestamps.append(get_utc_dt(e[timestamp]))
    df = pd.DataFrame()
    #df['Counts'], df['Timestamps'] = counts, timestamps
    df['Timestamps'], df['Counts'] = timestamps, counts
    return df

after_month, after_year = int(input('enter a start month for the search')), int(input('enter a start year for the search'))
before_month, before_year = int(input('enter an end month for the search')), int(input('enter an end year for the search'))

before = get_epoch(before_year, before_month)
after = get_epoch(after_year, after_month)
#q = '"' + input('enter a word or phrase: ') + '"'
aggs = 'created_utc'
frequency = 'month'
size = 0

''' start of new attempt - to take in three terms'''
q_tuple = ([], [], [])
counter = 0
for e in q_tuple:
    e.append('"' + input('enter a word or phrase: ') + '"')
    if e[0] == '""':
        break
    else:
        counter += 1
        e.append(get_response_term(e[0], after, before)['aggs']['created_utc'])
''' end of new attempt - to take in three terms'''

''' write a left-join loop; run it while q_tuple[-][0] != '""' '''
df_all = (return_arrays(get_response_all(), True))
df_term = return_arrays(q_tuple[0][1], True)
if q_tuple[1][0] != '""':
    df_term = df_term.merge(return_arrays(q_tuple[1][1], True), on = 'Timestamps', how = 'left')#, suffixes=(q_tuple[0][0], q_tuple[1][0]))
if q_tuple[2] != []:
    if q_tuple[2][0] != '""':
        df_term = df_term.merge(return_arrays(q_tuple[2][1], True), on = 'Timestamps', how = 'left')

mapping = {df_term.columns[0]:'Timestamps'}
for i in range(counter):
    mapping[df_term.columns[i+1]] = q_tuple[i][0][1:-1]
    
df_term = df_term.rename(columns = mapping)
df_merged = df_term.merge(df_all, on = 'Timestamps', how = 'left')
df_plot = pd.DataFrame()
df_plot['Timestamps'] = df_merged['Timestamps']
for i in range(counter):
    df_plot[q_tuple[i][0][1:-1]] = df_merged[q_tuple[i][0][1:-1]]/df_merged['Counts']

df_plot.plot(x = 'Timestamps')
        
''' '''
'''********* IF ONE/THREE TERMS HAS MISSING MONTHS, WILL ERROR************'''

#data_bucketed = get_response_term(q, after, before)['aggs']['created_utc']
#
#df_all = (return_arrays(get_response_all(), True))
#
#
#df_term = return_arrays(data_bucketed, True)
#df_term.plot(x='Timestamps')
#
#df_merged = df_term.merge(df_all, on = 'Timestamps', how = 'left')
#
#df_merged[['Rate']] = df_merged[['Counts_x']].div(df_merged.Counts_y, axis=0)
#df_merged.plot(x = 'Timestamps', y = 'Rate')
