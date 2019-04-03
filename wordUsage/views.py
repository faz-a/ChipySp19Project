import requests, matplotlib, pytz
import numpy as np
import datetime as dt
from datetime import date
from datetime import datetime
from pytz import timezone
from tzlocal import get_localzone
import pandas as pd
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import ContactForm
from django.http import HttpResponse

import io
from io import BytesIO
import matplotlib.pyplot as plt


def get_response_term(q, after, before):
    aggs, frequency, size = 'created_utc', 'month', 0
    parameters = {"q":q,"aggs":aggs, "frequency":frequency, "size":size, "after":after, "before":before}
    response=requests.get("https://api.pushshift.io/reddit/search/comment/",params=parameters)
    data = response.json()
    return data

def get_response_all():
    response = requests.get("https://beta.pushshift.io/reddit/statistics")
    return response.json()['comment_all_activity']

def get_epoch(aYear, aMonth):
    utc = pytz.utc
    return int(utc.localize(datetime(aYear, aMonth, 1, 0, 0)).timestamp())

def get_utc_dt(epoch):
    local_dt = dt.datetime.fromtimestamp(epoch)
    utc = pytz.utc
    utc_dt_aware = local_dt.astimezone(utc)
    return datetime(utc_dt_aware.year, utc_dt_aware.month, utc_dt_aware.day)

def return_arrays(bucketed_counts, reverse):
    """takes in a list of dictionaries; returns a pandas dataframe"""
    try:
        d1 = list(bucketed_counts[0].keys())
    except IndexError:
        raise IndexError('There was an issue accessing the API')
    d1.sort(reverse = reverse)
    count, timestamp = d1[1], d1[0]
    counts, timestamps = [], []
    for e in bucketed_counts: #here, it means "for e in data_bucketed"
        counts.append(e[count])
        timestamps.append(get_utc_dt(e[timestamp]))
    df = pd.DataFrame()
    df['Timestamps'], df['Counts'] = timestamps, counts
    return df

def wordUsage(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ContactForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:

            t1 = form.cleaned_data['t1']
            t2 = form.cleaned_data['t2']
            t3 = form.cleaned_data['t3']
            start_mo = int(form.cleaned_data['start_mo'])
            start_yr = int(form.cleaned_data['start_yr'])
            end_mo = int(form.cleaned_data['end_mo'])
            end_yr = int(form.cleaned_data['end_yr'])
            #return HttpResponseRedirect('/thanks/')
            return returnPlot(start_mo, start_yr, end_mo, end_yr, t1, t2, t3)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ContactForm()

    return render(request, 'wordUsage/wordUsage.html', {'form': form})


#def returnPlot(request):
def returnPlot(start_mo, start_yr, end_mo, end_yr, t1, t2 = '', t3 = ''):

    
    after = get_epoch(start_yr, start_mo)
    before = get_epoch(end_yr, end_mo)
    
    
    q_tuple = (['"' + t1 + '"'], ['"' + t2 + '"'], ['"' + t3 + '"'])
    counter = 0
    for e in q_tuple:
        if e[0] == '""':
            break
        else:
            counter += 1
            e.append(get_response_term(e[0], after, before)['aggs']['created_utc'])
            if e[1] == []:
                counter -=1

    try:
        df_all = (return_arrays(get_response_all(), True).groupby(pd.Grouper(key='Timestamps', freq='MS')).sum())
    except IndexError:
        return HttpResponse('There was an issue accessing the data. Please try again later.')
    df_term = return_arrays(q_tuple[0][1], True)
    if q_tuple[1][0] != '""' and len(q_tuple[1][1]) > 0:
        df_term = df_term.merge(return_arrays(q_tuple[1][1], True), on = 'Timestamps', how = 'left')#, suffixes=(q_tuple[0][0], q_tuple[1][0]))
    if q_tuple[2] != []:
        if q_tuple[2][0] != '""' and len(q_tuple[2][1]) > 0:
            df_term = df_term.merge(return_arrays(q_tuple[2][1], True), on = 'Timestamps', how = 'left')
    
    mapping = {df_term.columns[0]:'Timestamps'}
    for i in range(counter):
        mapping[df_term.columns[i+1]] = q_tuple[i][0][1:-1]
        
    df_term = df_term.rename(columns = mapping)
    df_merged = df_term.merge(df_all, left_on = 'Timestamps', right_index = True, how = 'left')
    df_plot = pd.DataFrame()
    df_plot['Timestamps'] = df_merged['Timestamps']
    for i in range(counter):
        df_plot[q_tuple[i][0][1:-1]] = df_merged[q_tuple[i][0][1:-1]]/df_merged['Counts']

    fig = plt.figure()
    df_plot.plot(x = 'Timestamps')
    plt.xlabel('Year')
    plt.ylabel('Percentage of Reddit Comments Containing Term')
    #plt.plot(df_plot)
    figdata = BytesIO()
    plt.savefig(figdata, format='png')
    print(df_plot)
    return HttpResponse(figdata.getvalue(), content_type="image/png")