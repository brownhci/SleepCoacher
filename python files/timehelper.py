#!/usr/bin/env python
import csv
from scipy.stats import linregress
import pandas as pd
import numpy as np
from sklearn.base import TransformerMixin
import os
from datetime import datetime, timedelta
from math import floor


# create a consistency column
# get average mean
# what percentage of 

# input: user (and assumes their sleep file is in Sleep e.g. "../Sleep/sleeper3.csv")
# output: a series representing their sleep consistency 
# (the minutes the current sleep time deviates from the mean sleep time)

def consistencyCreator(user="sleeper3.csv"):
    userSleepPath = "../Sleep/" + user
    sleepdf= pd.DataFrame.from_csv(userSleepPath, index_col=None)

    bedtimes = list(sleepdf["start_time_str"])
    waketimes =list(sleepdf["end_time_str"])

    meanBedtime, meanWaketime = calculate_average_bedwaketime(bedtimes, waketimes)

    bedtime_consistency = [0] * len(bedtimes)
    waketime_consistency = [0] * len(waketimes)
    
    for i in range(len(bedtimes)):
        # decimalize
        bedtime = str2datetime(bedtimes[i])
        waketime = str2datetime(waketimes[i])

        # print "meanBedtime", meanBedtime
        # print "bedtime", bedtime, "waketime", waketime

        nightdate = waketime.date() - timedelta(days=1)

        bedtime_decimal = bedtimehour(bedtime, nightdate)
        # print "bedtime_decimal", bedtime_decimal
        waketime_decimal = waketimehour(waketime, nightdate)

        bedtime_consistency[i] = abs(bedtime_decimal - meanBedtime)
        waketime_consistency[i] = abs(waketime_decimal - meanWaketime)

    return bedtime_consistency, waketime_consistency

# input: list of alarms like : ["2015-02-20T10:58:55Z|2015-02-20T10:58:55Z", "2015-02-20T10:58:55Z"]
# output: counts like : [2, 1]
def alarm_countify(alarm):
    for i in range(len(alarm)):
        alarmstr = str(alarm[i])
        alarmarr = alarmstr.split("|")
        if alarmarr is None or alarmarr == [''] or alarmarr == ['nan']: 
        # safe checking in case there is no alarm, it doesn't count as length 1
            alarm[i] = 0
        else:
            alarm[i] = len(alarmarr)

    return alarm

# waketimes are currently represented as ints e.g. 29, 32
# which represent 0:00 hours from nightdate
# eg if someone slept from 12am to 7am:
# bedtime: 24, waketime: 31
def convert_bedwaketime(bedwakeint):
    cur = 0

    if bedwakeint < 25:
        cur = bedwakeint
    elif bedwakeint > 24:
        cur = bedwakeint - 24

    return cur

def decimal2time(time_hours):
    time_minutes = time_hours * 60
    time_seconds = time_minutes * 60

    try:
        hours_part   = int(floor(time_hours))
        minutes_part = int(floor(time_minutes % 60))
        seconds_part = int(floor(time_seconds % 60))

        if hours_part >= 24:
            hours_part = hours_part - 24

        output = "{h:02d}:{m:02d}:{s:02d}".format(h=hours_part, m=minutes_part, s=seconds_part)
    except:
        output = np.nan
    # print output
    return output

# input: time represented as string '2015-03-20T06:13:00Z'
# output: seconds in day '22380'
# TODO: in future- create a seconds to time to recommend an *optimal* bedtime/waketime
# based on a person's circadian rhythm 
def time2seconds(time):
    (h,m,s) = time.split(':')
    result=int(h) * 3600 + int(m) * 60 + int(s)
    return result

# input: datetime represented as string '2015-03-20T06:13:00Z'
# output: time represented as string '06:13:00'
def date2time(datetime):
    t2=datetime.split("T")
    t3=t2[1].split("Z")
    t4=t3[0]

    return t4

# input: "2015-03-20T09:32:00Z"
# output: datetime.datetime(2015, 3, 20, 9, 32)
def str2datetime(str1):
    # print "inside function: str2datetime"
    # print "str", str1
    npdatetime = np.datetime64(str1)
    return npdatetime.astype(datetime)


# this gets the number hours since 0:00 that they go to bed
# for example, this would be 23 if they go to bed at 11pm, or 27 if they go to bed at 3am
def bedtimehour(bedtimedt, nightdate):
    # print "inside function: bedtimehour"
    # print "bedtimedt", bedtimedt
    # print "nightdate", nightdate
    # print "type(nightdate)", type(nightdate)
    # print "type(bedtimedt)", type(bedtimedt)
    return (bedtimedt - datetime.combine(nightdate, datetime.min.time())).total_seconds() / 60 / 60

def waketimehour(waketimedt, wakedate):
    # print "inside function: waketimehour"
    # print "waketimedt", waketimedt
    # print "wakedate", wakedate
    return (waketimedt - datetime.combine(wakedate, datetime.min.time())).total_seconds() / 60 / 60


# input: a list (or pandas series) of bedtimes and waketimes as strings
# e.g. [2015-03-20T06:13:00Z, 2015-03-19T06:21:00Z, 2015-03-18T04:33:00Z]
# 2015-03-20T12:24:00Z, 2015-03-19T12:49:00Z, 2015-03-18T12:29:00Z]
# output: bedtime, waketime
def calculate_average_bedwaketime(bedtime, waketime):
    # print "inside calculate_average_bedwaketime"
    # produce the nightdates
    # nightdate_list = []
    bedtimehour_list = []
    waketimehour_list = []

    for i in range(len(bedtime)):
        bedtime_dt = str2datetime(bedtime[i])
        waketime_dt = str2datetime(waketime[i])

        # print "bedtime_dt", bedtime_dt
        # print "type(bedtime_dt)", type(bedtime_dt)

        nightdate = waketime_dt.date() - timedelta(days=1)
        bedtimehour_list.append(bedtimehour(bedtime_dt, nightdate))

        hoursofsleep = (waketime_dt - bedtime_dt).seconds / 60.0 / 60.0

        if hoursofsleep > 3: # don't count naps
            wakedate = nightdate #waketime_dt.date()#bedtime_dt.date() + timedelta(days=1)
            waketimehour_list.append(waketimehour(waketime_dt, wakedate))

    # all the bed times are now in their proper format in bedtimehour_list
    # print "bedtimehour_list", bedtimehour_list

    # 5.0 controls for zulu time
    try:
        meanBedHour = (sum(bedtimehour_list) / len(bedtimehour_list)) - 5.0
    except:
        meanBedHour = np.nan
        # ^ arbitrary negative number indicates the use never had a high dependent variable(e.g. rating)

    try:
        meanWakeHour = (sum(waketimehour_list) / len(waketimehour_list)) - 5.0
        # ^ arbitrary negative number indicates the use never had a high dependent variable(e.g. rating)
    except:
        meanWakeHour = np.nan
    # print "- - - - checkpoint #1 - - - -"
    return meanBedHour, meanWakeHour

