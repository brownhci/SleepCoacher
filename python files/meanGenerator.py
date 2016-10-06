#!/usr/bin/env python
import csv
from scipy.stats import linregress
import pandas as pd
import numpy as np
from sklearn.base import TransformerMixin
import os
from datetime import datetime, timedelta
from math import floor
import csvHelper
import timehelper
import warnings


# Input:
# (1) User (e.g. sleeper1)
# (2) Independendent variable (e.g. bedtime)
# (3) Dependent variable (e.g. ratings)

# Output:
# low mean, high mean


# def meanNumbers(user="sleeper3.csv", indep="waketime", dep="rating"):
def meanNumbers(user, indep, dep):
    userSleepPath = "../Sleep/" + user
    userSimplePath = "../SimpleData/" + user

    # read csvs in Sleep and SimpleData into DataFrame
    sleepdf= pd.DataFrame.from_csv(userSleepPath, index_col=None)
    simpledf= pd.DataFrame.from_csv(userSimplePath, index_col=None)
    simpledf.drop(['rating'],inplace=True,axis=1,errors='ignore') # remove rating from simpledf (it's already in sleepdf)

    bedtime_consistency, waketime_consistency = timehelper.consistencyCreator(user)
    #print bedtime_consistency
    # print 'len(simpledf[consistency])',len(simpledf['consistency'])
    #print 'len(bedtime_consistency)',len(bedtime_consistency)
    simpledf["consistency"] = bedtime_consistency 
    # print "HELLOW"
    #print 'len(simpledf[consistency])',len(simpledf['consistency'])
    # print 'len(bedtime_consistency)',len(bedtime_consistency)
    # ^ TO REFACTOR- create a "consistency" column in the SimpleData itself from pullinfo.py
    # instead of generating it twice in (1) meanGenerator.py, (2) postSleepAnalyzer.py

    # merge sleepdf + simpledf
    result = pd.concat([sleepdf, simpledf], axis=1, join='inner')

    # Find all the rows for the "low" and "highs" of dependent variables
    if dep == "rating":
        # remove 0 from "ratings" using a mask
        result["rating"].mask(result["rating"] == 0, inplace=True)
        ratingThreshold = np.mean(result["rating"]) # compute normalized median for user

        lowDepAll = result[result[dep] <= ratingThreshold] # create ratings 0~3
        highDepAll = result[result[dep] > ratingThreshold] # create ratings 3~5

    elif dep == "onsetlatency":
        # remove 0 from "ratings" using a mask
        result["onsetlatency"].mask(result["onsetlatency"] == 0, inplace=True)
        onsetlatencyThreshold = np.mean(result["onsetlatency"]) # compute normalized median for user

        # onsetlatencyThreshold = 60*30 # 30 minutes
        lowDepAll = result[result[dep] <= onsetlatencyThreshold]
        highDepAll = result[result[dep] > onsetlatencyThreshold]

    # based on sleep clinician data: we have an average of 3-5 arousals per 90 minutes
    # this sets threshold at 4 arousals per hour
    elif dep == "awakenings":
        # awakeningsThreshold = 4
        # remove 0 from "ratings" using a mask
        result["awakeningsPerHour"].mask(result["awakeningsPerHour"] == 0, inplace=True)
        awakeningsThreshold = np.mean(result["awakeningsPerHour"]) # compute normalized median for user

        lowDepAll = result[result["awakeningsPerHour"] <= awakeningsThreshold]
        highDepAll = result[result["awakeningsPerHour"] > awakeningsThreshold]

        # print "lowDepAll", lowDepAll
        # print "highDepAll", highDepAll

    # Find the means of the independent variables
    if indep == "bedtime" or indep == "waketime":
        lowDep_bedtime = list(lowDepAll["start_time_str"]) # panda series
        lowDep_waketime = list(lowDepAll["end_time_str"]) # panda series
        meanBedtimeLow, meanWaketimeLow = timehelper.calculate_average_bedwaketime(lowDep_bedtime, lowDep_waketime)

        highDep_bedtime = list(highDepAll["start_time_str"]) # panda series
        highDep_waketime = list(highDepAll["end_time_str"]) # panda series
        # print type(highDep_waketime)
        # highDep_waketime = ['2016-03-04T07:52:00Z', '2016-03-04T07:58:00Z', '2016-02-27T07:18:00Z', '2016-02-26T06:50:00Z', '2016-02-24T06:30:00Z', '2016-02-20T07:13:00Z', '2016-02-20T07:11:00Z', '2016-02-19T07:02:00Z', '2016-02-14T07:49:00Z', '2016-02-10T07:04:00Z']
        # lowDep_waketime = ['2016-03-02T05:00:00Z', '2016-02-27T03:36:00Z', '2016-02-25T05:38:00Z', '2016-02-23T06:15:00Z', '2016-02-21T05:49:00Z', '2016-02-17T05:00:00Z', '2016-02-16T05:00:00Z', '2016-02-15T05:00:00Z', '2016-02-12T07:07:00Z', '2016-02-09T05:12:00Z', '2016-02-08T06:14:00Z']
        meanBedtimeHigh, meanWaketimeHigh = timehelper.calculate_average_bedwaketime(highDep_bedtime, highDep_waketime)      
        # print "HIGH", meanWaketimeHigh
        # print "LOW", meanWaketimeLow
        # if indep == "bedtime":
        #     return timehelper.decimal2time(meanBedtimeLow), timehelper.decimal2time(meanBedtimeHigh)

        # elif indep == "waketime":
        #     return timehelper.decimal2time(meanWaketimeLow), timehelper.decimal2time(meanWaketimeHigh)


        if indep == "bedtime":
            bedtimeLow = str(timehelper.decimal2time(meanBedtimeLow)).split(":")
            bedtimeHigh = str(timehelper.decimal2time(meanBedtimeHigh)).split(":")
            if bedtimeLow != ['nan']:
                bedtimeLow = bedtimeLow[0]+":"+bedtimeLow[1]
            if bedtimeHigh != ['nan']:
                bedtimeHigh = bedtimeHigh[0]+":"+bedtimeHigh[1]
            return bedtimeLow, bedtimeHigh

        elif indep == "waketime":
            waketimeLow = str(timehelper.decimal2time(meanWaketimeLow)).split(":")
            waketimeHigh = str(timehelper.decimal2time(meanWaketimeHigh)).split(":")
            if waketimeLow != ['nan']:
                waketimeLow = waketimeLow[0]+":"+waketimeLow[1]
            if waketimeHigh != ['nan']:
                waketimeHigh = waketimeHigh[0]+":"+waketimeHigh[1]
            return waketimeLow, waketimeHigh


    elif indep == "hoursslept":
        lowDep_hoursslept = list(lowDepAll["hoursslept"])
        highDep_hoursslept = list(highDepAll["hoursslept"])
        return np.mean(lowDep_hoursslept), np.mean(highDep_hoursslept)

    elif indep == "alarm":
        lowDep_alarm = timehelper.alarm_countify(list(lowDepAll["alarm_str"]))
        highDep_alarm = timehelper.alarm_countify(list(highDepAll["alarm_str"]))

        return np.mean(lowDep_alarm), np.mean(highDep_alarm)

    elif indep == "noisiness":
        lowDep_noisiness = lowDepAll["noisiness"]
        lowDep_noisiness.fillna(0.0, inplace=True)
        lowDep_noisiness = list(lowDep_noisiness)

        highDep_noisiness = highDepAll["noisiness"]
        highDep_noisiness.fillna(0.0, inplace=True)
        highDep_noisiness = list(highDep_noisiness)

        return np.mean(lowDep_noisiness), np.mean(highDep_noisiness)

    elif indep == "consistency":
        lowDep_consistency = lowDepAll["consistency"]
        lowDep_consistency.fillna(0.0, inplace=True)
        lowDep_consistency = list(lowDep_consistency)

        #print "lowDep_consistency", lowDep_consistency


        highDep_consistency = highDepAll["consistency"]
        #print "highDep_consistency", highDep_consistency
        highDep_consistency.fillna(0.0, inplace=True)
        highDep_consistency = list(highDep_consistency)

        try:
            lowMean = np.mean(lowDep_consistency)
        except:
            lowMean = -99.0

        try:
            highMean = np.mean(highDep_consistency)
        except:
            highMean = -99.0

        # low/high mean represents average hours from mean bedtime
        return lowMean, highMean






if __name__ == "__main__":
    print meanNumbers("sleeper18.csv", "waketime", "rating")


    # Sample input: meanNumbers("sleeper3.csv", "consistency", "rating")
    # Sample output: (5.5173926767676722, 4.5130421865715933)
    # 5.5 <- hours deviated from mean bedtime when low rating
    # 4.5 <- hours deviated from mean bedtime when high rating

    # Interpreting Results:
    # Note: If output = 'nan' when dep var = 'awakenings'
    # -> Means there were no rows where awakenings > 4

