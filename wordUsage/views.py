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


from django.shortcuts import render_to_response
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.resources import INLINE
#
from bokeh.models import ColumnDataSource, HoverTool, Legend
from bokeh.palettes import Category10
#
import itertools


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


#the next two functions were adapted from the example on https://medium.com/@andrewm4894/bokeh-battles-part-1-multi-line-plots-311109992fdc
def color_gen():
    yield from itertools.cycle(Category10[10])

def plot_lines_multi(df,lw=2,pw=700,ph=400,t_loc='above'):
    '''...
    '''
    source = ColumnDataSource(df)
    col_names = source.column_names
    p = figure(x_axis_type="datetime",plot_width=pw, plot_height=ph,toolbar_location=t_loc)
    p_dict = dict()
    color = color_gen()
    for col, c, col_name in zip(df.columns,color,col_names[1:]):
        p_dict[col_name] = p.line('Timestamps', col, source=source, color=c,line_width=lw)###just edited
        p.add_tools(HoverTool(
            renderers=[p_dict[col_name]],
            tooltips=[('Month','@Timestamps{%Y-%m}'),(col, f'@{col}')],###just edited
            formatters={'Timestamps': 'datetime'}###just edited
        ))
    legend = Legend(items=[(x, [p_dict[x]]) for x in p_dict])
    p.add_layout(legend,'right')
    return(p)
########################################

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
    df_plot = pd.DataFrame()
    df_plot['Timestamps'] = df_term['Timestamps']
    df_term['sum'] = df_term.iloc[:,1] +  df_term.iloc[:,2] + df_term.iloc[:,3]
    for i in range(counter):
        df_plot[q_tuple[i][0][1:-1]] = df_term.iloc[:,i+1] / df_term.iloc[:,4]

    df_plot = df_plot.set_index('Timestamps')
    p = plot_lines_multi(df_plot)
    script, div = components(p)
    return render_to_response('wordUsage/bokehTutorial.html', {'resources': INLINE.render(), 'script': script, 'div': div})


def bokehTutorial(request):
    x, y, = [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]
    #Setup graph plot
    plot = figure(title = 'Line Chart', x_axis_label = 'X axis', y_axis_label = 'Y axis', plot_width = 400, plot_height = 400)
    #plot line
    plot.line(x, y, line_width = 2)
    #store components
    script, div = components(plot)
    #return to django homepage with components sent as arguments which will then be displayed
    return render_to_response('wordUsage/bokehTutorial.html', {'resources': INLINE.render(), 'script': script, 'div': div})