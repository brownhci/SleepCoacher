# for every user, find their file in user_stats folder, and read all of the lines. 
# pull all the variables. 
# fill in the following sentence:
# Last night it took you onset_latency minutes to fall asleep, you woke up awakenings times during the night,
# and slept for a total of hours_slept hours.

# actually, this wouldn't come from the averages! this is strictly for last night!
# this would come from each participant's raw data for last night 
# maybe after it has passed through pull data?

import os
from datetime import datetime, date, time
import csv
from random import randint


DATA_PATH = "../SimpleData" #/home/nediyana/TheRealSleepCoacher

hours_slept ={}
rating = {}
awakenings_per_hour = {}
onset_latency = {}
rec_text = {}
full_date = {}
# mylist = []
# # today = date.today()
# mylist.append(today)
# mylist[0] = str(mylist[0])
# day = mylist[0].split('-')[2]
# month = mylist[0].split('-')[1]
# year = mylist[0].split('-')[0]
fromTime = {}
fromTime_hour = {}
hours_slept_addon = {}
few = {}
sessions = {} # if there is more than one recording for the night, then the user stopped the app during the night and then started it again and stopped it in the morning. thus, we are not calculating awakenings per hour and i am not giving them an updated about the number of awakenings per hour. 

# formatted_today = day+"."+month+'.'+year
start_date = {}
# today_day = int(day)
today = date(2016,3,14)
formatted_today = '14.03.2016'
length_A1 = {}
length_A2 = {}
length_B1 = {}
length_B2 = {}

conclusions = {}

def days_between(d1, d2):
    return abs((d2 - d1).days)

# counter = 1
for row in csv.reader(open("../python files/conclusions_rec1.csv")):
	if row[0].strip() != 'ID' and len(row[0].strip())>1:
		conclusions[row[0].strip()] = row[1].strip()


for filename in os.listdir(DATA_PATH):
	skip = False
	user_id = filename.split('.')[0]
	hours_slept_addon[user_id] = 0
	sessions[user_id] = 0

	if user_id not in start_date:
		start_date[user_id] = date(2016,3,1)

	for entry in csv.reader(open("../phase_lengths/"+user_id+".csv")):
		if entry[0] =="A2":
			few[user_id]=entry[1]
			length_A2[user_id] = int(entry[1])
		elif entry[0]=='A1':
			length_A1[user_id] = int(entry[1])
		elif entry[0]=='B1':
			length_B1[user_id] = int(entry[1])
		elif entry[0] =='B2':
			length_B2[user_id] = int(entry[1])

	if 'DS' not in filename:
		counter = 0
		last_night = ""
		for line in csv.reader(open(DATA_PATH+"/"+filename)):
			if counter == 1:
				last_night = line
				fromTime[user_id] = last_night[6]

				#check if this entry was a nap post last night's entry
				if (int(fromTime[user_id].split(':')[0]) > 11 and int(fromTime[user_id].split(':')[0]) < 20) and (full_date[user_id] == formatted_today):
					#then this was a daytime nap
					print "this was a nap"
				else:	
					if float(line[2]) > 0.5:
						counter = counter + 1
				full_date[user_id] = last_night[0]
			else:
				if counter == 0:
					counter  = counter + 1
				else:
					if (line[0] == full_date[user_id] and line[0]==formatted_today) and (float(line[2]) > 0.5 and fromTime[user_id].split(':')[0] > 20): #then this is again a line with data from last night


					# 	# add up the hours slept 
					# 	# take the earliest onset latency - keep reading lines down the csv until we get to the last line with today's date, which actually has the onset latency for last night
					# 	# take the morning (latest) rating 
						hours_slept_addon[user_id] = float(line[2]) + hours_slept_addon[user_id]
						onset_latency[user_id] = float(line[3])/float(60)
						sessions[user_id] = sessions[user_id] + 1
						counter = counter + 1

		if len(last_night)>1:
			hours_slept[user_id] = float(last_night[2]) + hours_slept_addon[user_id]
			if hours_slept[user_id] > 2:
				if user_id not in onset_latency:
					onset_latency[user_id] = float(last_night[3])/float(60)					
				awakenings_per_hour[user_id] = float(last_night[5])
				if last_night[1] != "none":
					rating[user_id] = float(last_night[1])

mean_hours_slept = 0	
mean_latency = 0 
mean_awakenings = 0

for key in hours_slept:
	mean_hours_slept = mean_hours_slept + hours_slept[key]

for key in onset_latency:
	mean_latency = mean_latency+onset_latency[key]

for key in awakenings_per_hour:
	mean_awakenings = mean_awakenings + awakenings_per_hour[key]

mean_awakenings = float(mean_awakenings)/len(awakenings_per_hour)
mean_latency = float(mean_latency)/len(onset_latency)
mean_hours_slept = float(mean_hours_slept)/len(hours_slept)

for filename in os.listdir(DATA_PATH):
	skip = False
	user_id = filename.split('.')[0]
	if user_id not in onset_latency:
		rec_text[user_id] = "We do not have data for your sleep last night. If you did not use the app, remember to use it tonight."

	else:
		# if the person went to bed after 00:00 last night, it makes it today's date
		# if the person went to bed before 11:59pm last night, it will be yesterday's date
		# we check that by looking at the hour of "fromTime": if fromTime is larger than 20, and the date is one less than today's date, that's still last night's sleep
		fromTime_hour[user_id] = int(fromTime[user_id].split(':')[0])
		today_minus_one = int(formatted_today.split('.')[0]) - 1
		last_night_bedtime_date = int(full_date[user_id].split('.')[0])
	
		if days_between(today, start_date[user_id]) < length_A1[user_id]:
			rec_text[user_id] = ""
		elif days_between(today,start_date[user_id]) == (length_A1[user_id]):
			rec_text[user_id] = '' #MAIN RECOMMENDATION, send as a separate message?
		elif (days_between(today,start_date[user_id])<(length_A1[user_id]+length_B1[user_id])) and (days_between(today, start_date[user_id]) >length_A1[user_id]):
			rec_text[user_id]= "Please remember to follow your recommendation today and add a rating and a comment in the morning. " 
		elif days_between(today,start_date[user_id])== (length_A1[user_id]+length_B1[user_id]):
			rec_text[user_id] = "Starting tonight, for the next FEW days, you do not need to follow the recommendation. ".replace("FEW",str(length_A2[user_id]))
		elif (days_between(today,start_date[user_id]) < (length_A1[user_id]+length_B1[user_id]+length_A2[user_id])) and (days_between(today, start_date[user_id])>(length_A1[user_id]+length_B1[user_id])):
			rec_text[user_id] = "No need to follow the rec tonight. "
		elif days_between(today, start_date[user_id]) == (length_A1[user_id] + length_B1[user_id]+length_A2[user_id]):
			rec_text[user_id]="Starting tonight, please follow the same rec again for the next FEW days. ".replace("FEW",str(length_B2[user_id])) # add the text of the rec in case they forgot it? so just send the same rec again?? 
		elif (days_between(today,start_date[user_id]) < (length_A1[user_id] + length_B1[user_id]+length_A2[user_id]+length_B2[user_id])) and (days_between(today,start_date[user_id])>(length_A1[user_id] + length_B1[user_id]+length_A2[user_id])):
			rec_text[user_id]= "Please remember to follow your recommendation again today and add a rating and a comment in the morning. "
		elif days_between(today,start_date[user_id]) == (length_A1[user_id]+length_B1[user_id]+length_A2[user_id]+length_B2[user_id]):
			start_date[user_id] = today
			rec_text[user_id]= conclusions[user_id]+" " #send as a separate message?
			# update start day to this day
			# design for future: have a different start day for each user;

		if full_date[user_id] == formatted_today or (fromTime_hour[user_id]>20 and (today_minus_one == last_night_bedtime_date)):

			# so that users get a somewhat different rec every day, randomize which text they would get today. 
			if onset_latency[user_id] < 1.5:
				rec = randint(0,1)
				rec_list = [0, 2]
				rec = rec_list[rec]
			else:
				if sessions[user_id] >= 1:
					rec = randint(1,3)
				else:
					rec = randint(0,3)


			if rec == 1:
				rec_text[user_id] = rec_text[user_id]+"Last night, it took you " + "{:.2f}".format(onset_latency[user_id]) + " minutes to fall asleep, and you slept for a total of " + "{:.2f}".format(hours_slept[user_id]) + " hours."
			elif rec == 0:
				rec_text[user_id] = rec_text[user_id]+"Last night, you slept for a total of " + "{:.2f}".format(hours_slept[user_id]) + " hours and woke up about " + "{:.2f}".format(awakenings_per_hour[user_id])+ " times per hour. Usually we experience 3-5 awakening arousals every 90 minutes."
			elif rec == 3:
				if onset_latency[user_id] < mean_latency:
					rec_text[user_id] = rec_text[user_id]+"Last night, it took you " + "{:.2f}".format(onset_latency[user_id]) + " minutes to fall asleep, which is "+"{:.2f}".format(mean_latency - onset_latency[user_id])+" minutes less than the average for all participants in this study."
				else:
					rec_text[user_id] = rec_text[user_id]+"Last night, it took you " + "{:.2f}".format(onset_latency[user_id]) + " minutes to fall asleep, which is "+"{:.2f}".format(onset_latency[user_id] - mean_latency)+" minutes longer than the average for all participants in this study."

			else:
				if hours_slept[user_id] < mean_hours_slept:
					rec_text[user_id] = rec_text[user_id]+"Last night, you slept " + "{:.2f}".format(hours_slept[user_id]) +" hours, which is "+ "{:.2f}".format(mean_hours_slept - hours_slept[user_id]) +" hours less than the average hours slept by all participants in this study. Experts recommend 7-9 hours of sleep. "
		 		else:
		 			rec_text[user_id] = rec_text[user_id]+"Last night, you slept " + "{:.2f}".format(hours_slept[user_id]) +" hours, which is "+ "{:.2f}".format(abs(mean_hours_slept - hours_slept[user_id]))+" hours more than the average hours slept by all participants in this study. Experts recommend 7-9 hours of sleep. "
			

		#design question - now if we have no data, we are still counting this day towards the length of whichever phase the user is in
		# however, if we are not limited by the study, would we just skip the day and continue with the phase counting once the user starts collecting data?

		else:
		 	rec_text[user_id] = "We do not have data for your sleep last night. If you did not use the app, remember to use it tonight."


if not os.path.exists("../daily_updates"):
    os.makedirs("../daily_updates")

for key in rec_text:
	file_id = "../daily_updates/"+key+".csv"
	with open(file_id, 'wb') as csvfile:
		spamwriter=csv.writer(csvfile)
		spamwriter.writerow([rec_text[key]])

# every time we start appending, first put the new date!!
with open("../python files/all_daily_updates.csv", 'a') as csvfile:
	spamwriter=csv.writer(csvfile)
	spamwriter.writerow([formatted_today])
	for key in rec_text:
		spamwriter.writerow([key, rec_text[key]])


