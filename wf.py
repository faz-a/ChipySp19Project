# -*- coding: utf-8 -*-
"""
Created on Thu Feb 14 22:36:41 2019

@author: Fazal
"""

#from pprint import pprint
import requests, matplotlib
import numpy as np
import datetime as dt
from datetime import date
def get_response(q, after, before):
    parameters = {"q":q,"aggs":aggs, "frequency":frequency, "size":size, "after":after, "before":before}
    response=requests.get("https://api.pushshift.io/reddit/search/comment/",params=parameters)
    print('url used is', response.url)
    #pprint(response.json())
    data = response.json()
    #print(type(data))
    #print(data)
    #!! THE POINT HERE IS TO PROCESS/RETURN IN A USABLE FORMAT, NOT TO PRINT !!
    return data

q = '"' + input('enter a word or phrase: ') + '"'
aggs = 'created_utc'
frequency = 'month'
size = 0
after = input('how many days ago is the starting point? ') + 'd' #modify later to take dates
before = input('how many days ago is the ending point? ') + 'd' #modify  later to take dates
parameters = {"q":q,"aggs":aggs, "frequency":frequency, "size":size, "after":after, "before":before}

data_aggs = get_response(q, after, before)
data_created_utc = data_aggs['aggs']
data_bucketed = data_created_utc['created_utc']



counts, timestamps = [], []
#for this, re-use the similar function from wf_monthly_aggregates.py, or vice versa
for e in data_bucketed:
    counts.append(e['doc_count'])
    timestamps.append(date.fromtimestamp(e['key']))
counts_array = np.array(counts)
timestamps_array = np.array(timestamps)
print(counts_array, timestamps_array)

matplotlib.pyplot.title('Reddit Posts with the Term over Time')
matplotlib.pyplot.xlabel('Time')
matplotlib.pyplot.ylabel('Number of Posts per Month')
matplotlib.pyplot.plot(timestamps_array, counts_array)
matplotlib.pyplot.show()
#counts_array = numpy.array(LIST COMPREHENSION); timestamps_array = numpy.array(LIST COMPREHENSION)
#use this for total counts per month: https://beta.pushshift.io/reddit/statistics
#it looks like it's not case sensitive
#major issue - not all subs/comments are english
#use small bars