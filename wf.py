# -*- coding: utf-8 -*-
"""
Created on Thu Feb 14 22:36:41 2019
@author: Fazal
"""

#from  pprint import pprint
import requests, matplotlib, pytz
import numpy as np
import datetime as dt
from datetime import date
from datetime import datetime
#from pytz import timezone
#import pytz
#from tzlocal import get_localzone
#
#local = get_localzone()
#utc = pytz.utc

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

def get_epoch(aYear, aMonth):
    utcDiff = datetime.utcnow()- datetime.now()
    dt_local = dt.datetime(aYear, aMonth, 1, 0, 0) 
    dt_utc = dt_local - utcDiff
    print('dt_local is', dt_local.timestamp(), 'and dt_utc is', dt_utc.timestamp())
    return int(dt_utc.timestamp())



#after = input('how many days ago is the starting point? ') + 'd' #modify later to take dates
#before = input('how many days ago is the ending point? ') + 'd' #modify  later to take dates
after_month, after_year = int(input('enter a start month for the search')), int(input('enter a start year for the search'))
before_month, before_year = int(input('enter an end month for the search')), int(input('enter an end year for the search'))

before = get_epoch(before_year, before_month)
after = get_epoch(after_year, after_month)
print('the below should be in a function!')
q = '"' + input('enter a word or phrase: ') + '"'
aggs = 'created_utc'
frequency = 'month'
size = 0

print('NEED TO PASS NEW DATES INTO PARAMETERS CORRECTLY')
print('NEED TO MAKE SURE THE TIMESTAMPS USE UNIX TIME')

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
print('BUT IT IS USING YOUR LOCAL TIME FOR TIMESTAMPS NEED UTC TIME')
#counts_array = numpy.array(LIST COMPREHENSION); timestamps_array = numpy.array(LIST COMPREHENSION)
#use this for total counts per month: https://beta.pushshift.io/reddit/statistics
#it looks like it's not case sensitive
#major issue - not all subs/comments are english
#use small bars