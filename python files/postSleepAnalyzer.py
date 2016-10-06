#!/usr/bin/env python
from __future__ import division
import csv
from scipy.stats import linregress
import pandas as pd
import numpy as np
from sklearn.base import TransformerMixin
import os
from datetime import datetime, timedelta
from math import floor
import timehelper

# Requires that there are two folders: (1) Sleep and (2) SimpleData
# that contain user data

# Running this file pulls the relevant columns from that folder
# and populates a folder 'UserCorrelations' that contains
# the dependent variables on the x axis, the independent variables on the y-axis
# and the corresponding correlation co-efficients for each.

# Note: only pulls tags if tagcount > 2
# Note: right now does not account for naps, takes every line into account for calculation.
# BUT it does take in account naps for calculating average bedtime (naps = less than 3 hours)
# Note: default is Zulu time

# REFACTOR LATER:
# summary_hash is a global variable

# DataFrameImputer
# takes all NaNs in an array of values and replaces the NaN with the average
# e.g. if x is an array of values represented by a pandas DataFrame
# DataFrameImputer().fit_transform(x)

class DataFrameImputer(TransformerMixin):

    def __init__(self):
        """Impute missing values.

        Columns of dtype object are imputed with the most frequent value 
        in column.

        Columns of other types are imputed with mean of column.

        """
    def fit(self, X, y=None):

        self.fill = pd.Series([X[c].value_counts().index[0]
            if X[c].dtype == np.dtype('O') else X[c].mean() for c in X],
            index=X.columns)

        return self

    def transform(self, X, y=None):
        return X.fillna(self.fill)

# input: time represented as string '2015-03-20T06:13:00Z'
# output: seconds in day '22380'

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
def str2datetime(str):
    npdatetime = np.datetime64(str)
    return npdatetime.astype(datetime)

# this gets the number hours since 0:00 that they go to bed
# for example, this would be 23 if they go to bed at 11pm, or 27 if they go to bed at 3am
def bedtimehour(bedtimedt, nightdate):
    return (bedtimedt - datetime.combine(nightdate, datetime.min.time())).total_seconds() / 60 / 60

def waketimehour(waketimedt, wakedate):
    return (waketimedt - datetime.combine(wakedate, datetime.min.time())).total_seconds() / 60 / 60


# input: a list (or pandas series) of bedtimes and waketimes as strings
# e.g. [2015-03-20T06:13:00Z, 2015-03-19T06:21:00Z, 2015-03-18T04:33:00Z]
# 2015-03-20T12:24:00Z, 2015-03-19T12:49:00Z, 2015-03-18T12:29:00Z]
# output: bedtime, waketime
def calculate_average_bedwaketime(bedtime, waketime):
    # produce the nightdates
    bedtimehour_list = []
    waketimehour_list = []

    for i in range(len(bedtime)):
        bedtime_dt = str2datetime(bedtime[i])
        waketime_dt = str2datetime(waketime[i])

        nightdate = waketime_dt.date() - timedelta(days=1)
        bedtimehour_list.append(bedtimehour(bedtime_dt, nightdate))

        hoursofsleep = (waketime_dt - bedtime_dt).seconds / 60.0 / 60.0
        
        if hoursofsleep > 3: # don't count naps
            wakedate = nightdate 
            waketimehour_list.append(waketimehour(waketime_dt, wakedate))

    # all the bed times are now in their proper format in bedtimehour_list
    meanBedHour = sum(bedtimehour_list) / len(bedtimehour_list)
    meanWakeHour = sum(waketimehour_list) / len(waketimehour_list)

    return meanBedHour - 5.0, meanWakeHour - 5.0

summary_hash = {}

def create_correlation_csv(simplecsv, sleepcsv, outputcsv_corr, outputcsv_max_corr, sleepername):
        global summary_hash

        if sleepername not in summary_hash:
            summary_hash[sleepername] = {}

        sleeper_simple = pd.read_csv(simplecsv)
        sleeper_sleep = pd.read_csv(sleepcsv)
        # Pull out dependent variables from csv
        ratings = sleeper_sleep.rating
        onsetlatency = sleeper_simple.onsetlatency
        awakeningsPerHour = sleeper_simple.awakeningsPerHour

        # Pull out independent var from csv
        # waketime and bedtime are represented as seconds
        hoursslept = sleeper_simple.hoursslept

        
        bedtime = sleeper_sleep.start_time_str
        waketime = sleeper_sleep.end_time_str

        # COMPUTE AVERAGE BEDTIME AND WAKETIME 
        average_bedtime, average_waketime = calculate_average_bedwaketime(bedtime, waketime)

        summary_hash[sleepername]["bedtime"] = timehelper.decimal2time(timehelper.convert_bedwaketime(average_bedtime))
        summary_hash[sleepername]["waketime"] = timehelper.decimal2time(timehelper.convert_bedwaketime(average_waketime))

        # Conversion to seconds for our regression
        try: # convert waketime to seconds
            for i in range(len(waketime)):
                time_wake = date2time(waketime[i])
                waketime[i] = time2seconds(time_wake)
        except:
            print ""

        try: # convert bedtime to seconds
            for i in range(len(bedtime)):
                time_bed = date2time(bedtime[i])
                bedtime[i] = time2seconds(time_bed)
        except:
            print ""

        noisiness = sleeper_sleep.noisiness 
        
        alarm = sleeper_sleep.alarm_str
        counter = sleeper_sleep.alarm_count

        summary_hash[sleepername]['more_than_1_alarm_per_day']= 'no'
        summary_hash[sleepername]['alarm_rings'] = 0
        summary_hash[sleepername]['days_with_alarms'] = 0
        for i in range(0, len(counter)):
            if int(counter[i])>0:
                summary_hash[sleepername]['days_with_alarms'] = summary_hash[sleepername]['days_with_alarms'] + 1
                summary_hash[sleepername]['alarm_rings'] = summary_hash[sleepername]['alarm_rings']+int(counter[i])
            if int(counter[i])>1:
                summary_hash[sleepername]['more_than_1_alarm_per_day']= 'yes'
        if int(summary_hash[sleepername]['days_with_alarms']) > 0:
            summary_hash[sleepername]['alarm_rings']= float(summary_hash[sleepername]['alarm_rings'])/float(summary_hash[sleepername]['days_with_alarms'])

        alarm.fillna("", inplace=True)

        # alarm string is separated by '|' for each alarm
        # this code splits on '|' to create a list
        # the length of the is the number of time the alarm sounds

        alarm = timehelper.alarm_countify(alarm)

        summary_hash[sleepername]["alarm"] = sum(alarm)/len(alarm)

        tags = sleeper_sleep.comment

        # e.g. taghash: {"#food": [0, ..., 0]}
        tags.fillna("", inplace=True) # remove NaN values from tags column
        taghash = {}

        tags_to_omit = ["#home", 'stress',"#geo", "#geo0", "#geo1", "#snore", "up", "#newmoon", "Wake"]

        for i in range (len(tags)):
            tagstringarray = tags[i].split(" ")
            for item in tagstringarray:
                # ignore certain tags
                if item in tags_to_omit:
                    continue
                if item not in taghash: # create array and add 1
                    taghash[item] = np.array([0]*len(tags)) #wake time guaranteed to be max
                taghash[item][i] = 1

        tagseries = {}
        # create a series out of each taghash if more than 2
        for tag, counts_array in taghash.iteritems():
            if counts_array.sum() > 2:
                # create a series
                tagseries[tag] = pd.Series(counts_array)

        # delete unnecessary tags
        tagseries.pop("", None) # sometimes split operation makes "" a tag
        tagseries.pop("#", None)



        # combine series into a dataframe in order to impute it
        depv = pd.concat([ratings, onsetlatency, awakeningsPerHour], axis=1)
        indepv = pd.concat([hoursslept, waketime, bedtime, noisiness, alarm], axis=1)

        depv_imputed = DataFrameImputer().fit_transform(depv)
        indepv_imputed = DataFrameImputer().fit_transform(indepv)

        # Turn into hashtable
        # .ix[:, #] <- grabs the column as a series from a dataframe
        ratings2 = depv_imputed.ix[:,0]
        ratingsx = ratings2.replace("none", 0)

        # remove 0 from "ratings" using a mask to set 0 as NaN
        ratingsx.mask(ratingsx == 0, inplace=True)

        onsetlatency2 = depv_imputed.ix[:,1]
        onsetlatencyx = onsetlatency2.replace("none", 0)
        onsetlatencyx = onsetlatencyx.convert_objects(convert_numeric=True)

        awakeningsPerHour2 = depv_imputed.ix[:,2]
        awakeningsPerHourx = awakeningsPerHour2.replace("none", 0)
        awakeningsPerHourx = awakeningsPerHourx.convert_objects(convert_numeric=True)

        hoursslept2 = indepv_imputed.ix[:,0]
        hourssleptx = hoursslept2.replace("none", 0)
        hourssleptx = hourssleptx.convert_objects(convert_numeric=True)

        waketimex = indepv_imputed.ix[:,1]
        bedtimex = indepv_imputed.ix[:,2]
        noisinessx = indepv_imputed.ix[:,3]
        alarmx = indepv_imputed.ix[:,4]

        # # # # # # # # # # # # GENERATE TEMP CONSISTENCY COLUMN HERE # # # # # # # # # # #
        bedtime_consistency, waketime_consistency = timehelper.consistencyCreator(sleepername)
        # only focus on bedtime consistency for now. 
        # it's easier to go to bed than to wake up.

        # Compute average (1) noisiness, (2) onset latency, (3) awakeningsPerHour, (4) hours slept
        summary_hash[sleepername]["noisiness"] = sum(noisinessx)/len(noisinessx)
        summary_hash[sleepername]["onsetlatency"] = sum(onsetlatencyx)/len(onsetlatencyx)
        summary_hash[sleepername]["awakeningsPerHour"] = sum(awakeningsPerHourx)/len(awakeningsPerHourx)

        newhrs = []
        for hr in hourssleptx:
            if float(hr) > 2: # disregard hours less than 2 (naps) in the mean hours of sleep calculation
                newhrs.append(hr)
        summary_hash[sleepername]["hoursslept"] = sum(newhrs)/len(newhrs)


        dep_var = {"ratings": ratingsx, "onsetlatency": onsetlatencyx, "awakeningsPerHour": awakeningsPerHourx}

        indep_var={"hoursslept": hourssleptx, "waketime": waketimex, "bedtime": bedtimex, "noisiness": noisinessx, "alarm": alarmx, "consistency": bedtime_consistency}

        for tag, series in tagseries.iteritems():
            indep_var[tag] = series

        rows = dep_var.keys()
        rows.insert(0, "")
        cols = ["waketime", "hoursslept", "bedtime", "noisiness", "alarm", "consistency"] #never used

        # Calculate correlation coefficients for every combination    
        csvfile = open(outputcsv_corr, 'wb')
        wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)

        wr.writerow(rows) # first write the names of all the dependent variables into the first row

        csvfile2 = open(outputcsv_max_corr, 'wb')
        wr2 = csv.writer(csvfile2, quoting=csv.QUOTE_ALL)

        curPosMax = [0, "x", "y"]
        curNegMax = [0, "x", "y"]

        secPosMax = [0, "x", "y"]
        secNegMax = [0, "x", "y"]

        # iterate through all combinations of independent var and dependent var
        # calculate the correlation co-efficient
        for label_x, values_x in indep_var.iteritems():
            templist = [label_x]
            for label_y, values_y in dep_var.iteritems():

                # in the case that people stop tagging
                # make the number of rows the same
                # so we can run the linear regression
                if len(values_x) != len(values_y):
                    difference = len(values_y) - len(values_x)
                    values_x = np.append(values_x, [0]*(difference))
                    values_x = pd.Series(data=values_x)


                # special case because we want to compare alarms with how long it takes to fall asleep the NEXT DAY
                if (label_x == "alarm" or label_x == "waketime" or label_x == "hoursslept") and label_y == "onsetlatency":

                    values_x = values_x.shift(periods=1, freq=None, axis=0)
                    values_x= values_x[1:]
                    values_y = values_y[1:]
                    slope, intercept, r_value, p_value, std_err = linregress(values_x, values_y)
                    templist.append(r_value)

                elif label_y == "ratings":

                    # mask the values in both x and y for which there is a NaN in y:
                    xm = np.ma.masked_array(values_x,mask=np.isnan(values_y)).compressed()
                    ym = np.ma.masked_array(values_y,mask=np.isnan(values_y)).compressed()

                    slope, intercept, r_value, p_value, std_err = linregress(xm, ym)
                    templist.append(r_value)

                else:
                    slope, intercept, r_value, p_value, std_err = linregress(values_x, values_y)
                    templist.append(r_value)
                
                if r_value > secPosMax[0]:
                    if r_value >= curPosMax[0]:
                        curPosMax[0], curPosMax[1], curPosMax[2], secPosMax[0], secPosMax[1], secPosMax[2] = r_value, label_x, label_y, curPosMax[0], curPosMax[1], curPosMax[2]
                    else:
                        secPosMax[0] = r_value
                        secPosMax[1] = label_x
                        secPosMax[2] = label_y

                if r_value < secNegMax[0]:
                    if r_value <= curNegMax[0]:
                        curNegMax[0], curNegMax[1], curNegMax[2], secNegMax[0], secNegMax[1], secNegMax[2] = r_value, label_x, label_y, curNegMax[0], curNegMax[1], curNegMax[2]
                    else:
                        secNegMax[0] = r_value
                        secNegMax[1] = label_x
                        secNegMax[2] = label_y
                                      
                # ^ creates a row of correlation coefficients for 
                # respective independent variables x dependent var
                # e.g. ["waketime", 192312, 231, ..., 12312]

            wr.writerow(templist)

        # max and min correlations
        corr_row = curPosMax + curNegMax + secPosMax + secNegMax
        corr_row.insert(0, sleepername)
        wr2.writerow(corr_row)

        csvfile.close()

# returns a list of all filesnames in a directory with *.csv
def find_csv_filenames( path_to_dir, suffix=".csv" ):
    filenames = os.listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]

def create_dir(dir_string):
    if not os.path.exists(dir_string):
        os.makedirs(dir_string)

def create_summary_stats_csv(name):
    global summary_hash
    # create a csv file from name
    csvfile = open("../UserSummaryStats/" + name, 'wb')
    wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)

    for attr, val in summary_hash[name].iteritems():
        l = [attr, val]
        wr.writerow(l)
        
    csvfile.close()

if __name__ == "__main__":

    create_dir("../UserCorrelations")
    create_dir("../UserMaxCorrelations")
    create_dir("../UserSummaryStats")

    filenames = find_csv_filenames("../Sleep")

    for name in filenames:
        simple = '../SimpleData/' + name
        sleep = '../Sleep/' + name
        outputcsv_corr = "../UserCorrelations/" + name
        outputcsv_max_corr = "../UserMaxCorrelations/" + name
        create_correlation_csv(simple, sleep, outputcsv_corr, outputcsv_max_corr, name)
        create_summary_stats_csv(name)

    # aggregate all files in UserMaxCorrelations to one file
    filenames_max_corr = find_csv_filenames("../UserMaxCorrelations")
    filewriter_max = csv.writer(open("../UserMaxCorrelations/aggregated_user_data.csv",'wb'))
    for filename in filenames_max_corr:
        csv_user_file = open("../UserMaxCorrelations/" + filename)
        for row in csv_user_file:
            row = row.split(",")
            filewriter_max.writerow(row)

    csv_user_file.close()


