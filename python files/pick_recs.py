# give a correlation value and a DV and IV
# read all the lines in CSV until line[0] says that IV
	# if line[1] says that DV, you have found the correlation! else: keep
	# reading lines until line[1] says that DV get line[3] and line[4] for the
	# recommendation text.  get line[6] for the top recommendation for this
	# category - ask clinicians to rank hypothesis in a hierarchy based on what they think will be most useful. 


import csv
import os
from random import randint
import meanGenerator
from datetime import datetime, date, time
import numpy 
import timehelper

#if we have one file where every line is a new user and it contains correlation, DV, IV

rec_text = {} # dictionary where each key is a user_id and each value is the text of the recommendation we should send them 
average_bedtime = {}
average_hoursslept = {}
average_waketime = {}
average_alarm = {}
average_noisiness ={}
average_onsetlatency ={}
average_awakenings = {}
few = {}
phase_a1 = {}
multiple_alarms = {}
days_with_alarms = {}
combinations = {}
weekday_waketime_high = {}
weekday_waketime_low = {}
rating = {}



def calculate_waketime(sleeper):
	weeks = {}
	sorted_weeks = {}
	average_weeks = {}

	counter = 0
	weekday_waketime_high[sleeper] =[]
	weekday_waketime_low[sleeper] = []
	rating[sleeper] = []
 	for line in csv.reader(open('../SimpleData/'+sleeper+'.csv')):
		if counter == 0:
			counter = counter + 1
		else:
			if line[1].strip() != 'none':
				rating[sleeper].append(float(line[1].strip()))
	rating_threshold = numpy.mean(rating[sleeper])
	counter = 0
	for line in csv.reader(open('../SimpleData/'+sleeper+'.csv')):
		if counter == 0:
			counter = counter + 1
		else:	
			day = line[7].split()[0].split('.')[0]
			month = line[7].split()[1].split('.')[0]
			year = line[7].split()[2]
			minute_proportion_of_hour = (float(line[7].split()[3].split(':')[1])/60)

			wake_time =(float(line[7].split()[3].split(':')[0]) +float(format(minute_proportion_of_hour, '.2f')))
			wake_date = date(int(year), int(month), int(day))
			if (wake_date.weekday() <= 4) and (wake_date.weekday() >=0):
				week_id = wake_date.isocalendar()[1]
				if week_id in weeks:
					weeks[week_id].append(wake_time)
				else:
					weeks[week_id] = []
					weeks[week_id].append(wake_time)
	for week in weeks:
		sorted_weeks[week] = sorted(weeks[week])
		average_weeks[week] = format(numpy.mean(weeks[week]), '.2f')

	optimal_waketime = []
	for week in sorted_weeks:
		if len(sorted_weeks[week])>1:
			if abs(sorted_weeks[week][0]-sorted_weeks[week][1]) < 0.5:
				mean_waketime = numpy.mean([sorted_weeks[week][0],sorted_weeks[week][1]])
				optimal_waketime.append(float(format(mean_waketime, '.2f')))
			elif abs(sorted_weeks[week][1]-sorted_weeks[week][2]) < 1:
				mean_waketime = numpy.mean([sorted_weeks[week][1],sorted_weeks[week][2]])
				optimal_waketime.append(float(format(mean_waketime, '.2f')))
	optimal_waketime = str(format(numpy.median(optimal_waketime), '.2f'))

	optimal_hour = optimal_waketime.split('.')[0]
	optimal_minutes = float('0.'+str(optimal_waketime).split('.')[1])*60
	optimal_minutes = str(round(optimal_minutes)).split('.')[0]

	optimal_waketime = optimal_hour+":"+optimal_minutes

	return optimal_waketime

	'''
			day = line[0].strip()
			# print day
			if line[6].strip().split(':')[0] > 20:
				# print day
				hour = str(line[7].strip().split(':')[0])
				year = str(day.split('.')[2])
				month = str(day.split('.')[1])
				date_date = str(day.split('.')[0])
				formatted_day = date(int(year),int(month), int(date_date))
				if len(hour) ==1:
					hour_minute = str(0)+line[7].strip()
					# print 'HOUR', hour_minute
				if formatted_day.weekday() <= 3 or formatted_day.weekday() >=1:
					if line[1].strip() != 'none':
						if float(line[1].strip()) >= rating_threshold:
							# print line[1], line[7]
							wake_dt = (year+'-'+month+'-'+date_date+'T'+hour_minute+':00Z')
							# wake_dt = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
							# weekday_waketime_high[sleeper].append(line[7].strip())
							weekday_waketime_high[sleeper].append(wake_dt)
						else:
							wake_dt = (year+'-'+month+'-'+date_date +'T'+hour_minute+':00Z')
							#weekday_waketime_low[sleeper].append(line[7].strip())
							weekday_waketime_low[sleeper].append(wake_dt)
			elif line[6].strip().split(':')[0] < 10:
				hour = str(line[7].strip().split(':')[0])
				year = str(day.split('.')[2])
				month = str(day.split('.')[1])
				date_date = str(int(day.split('.')[0])-1)
				formatted_day = date(int(year),int(month), int(date_date))
				if len(hour) ==1:
					hour_minute = str(0)+line[7].strip()
					# print 'HOUR', hour_minute
				if formatted_day.weekday() <= 3 or formatted_day.weekday() >=1:
					if line[1].strip() != 'none':
						if float(line[1].strip()) >= rating_threshold:
							wake_dt = (year+'-'+month+'-'+date_date+'T'+hour_minute+':00Z')
							#weekday_waketime_high[sleeper].append(line[7].strip())
							weekday_waketime_high[sleeper].append(wake_dt)
						else:
							wake_dt = (year+'-'+month+'-'+date_date+'T'+hour_minute+':00Z')
							#weekday_waketime_low[sleeper].append(line[7].strip())
							weekday_waketime_low[sleeper].append(wake_dt)
	'''

for line in csv.reader(open('../python files/combinations_round_1.csv')):
	user_id = line[0].strip()
	independent = line[1].strip()
	dependent = line[2].strip()
	combinations[user_id] = [independent, dependent]


for line in csv.reader(open("../UserMaxCorrelations/aggregated_user_data.csv")):
	user_id = line[0].replace("\"", "").split('.')[0]
	filename = user_id+".csv"
	max_positive = float(line[1].replace("\"", ""))
	max_negative = float(line[4].replace("\"", ""))
	backup_positive = float(line[7].replace("\"", ""))
	backup_negative = float(line[10].replace("\"", ""))
	
	if max_positive > abs(max_negative):# and (line[2].replace("\"", "") != 'noisiness' and line[3].replace("\"", "").strip() != 'awakenings'):
		correlation = max_positive
		correlation_sign = 'positive'
		independent = line[2].replace("\"", "")
		dependent = line[3].replace("\"", "").strip()
		# find the next highest correlation
		other_correlations = [abs(max_negative), backup_positive, abs(backup_negative)]
		secondary_index = other_correlations.index(max(other_correlations))
		other_correlations[secondary_index] = 0
		tertiary_index = other_correlations.index(max(other_correlations))

		if secondary_index == 0:
			backup_dependent = line[6].replace("\"", "").strip()
			backup_independent = line[5].replace("\"", "")
			backup_correlation = max_negative
			backup_correlation_sign = 'negative'
		elif secondary_index == 1:
			backup_correlation = backup_positive
			backup_correlation_sign = 'positive'
			backup_independent = line[8].replace("\"", "")
			backup_dependent = line[9].replace("\"", "").strip()
		elif secondary_index == 2:
			backup_correlation = max_negative
			backup_correlation_sign = 'negative'
			backup_independent = line[11].replace("\"", "")
			backup_dependent = line[12].replace("\"", "").strip()

		if tertiary_index == 0:
			tertiary_dependent = line[6].replace("\"", "").strip()
			tertiary_independent=line[5].replace("\"", "")
			tertiary_correlation = max_negative
			tertiary_correlation_sign = 'negative'
		elif tertiary_index==1:
			tertiary_correlation=backup_positive
			tertiary_correlation_sign='positive'
			tertiary_independent=line[8].replace("\"", "")
			tertiary_dependent = line[9].replace("\"", "").strip()
		elif tertiary_index==2:
			tertiary_correlation==max_negative
			tertiary_correlation_sign ='negative'
			tertiary_independent = line[11].replace("\"", "")
			tertiary_dependent = line[12].replace("\"", "").strip()

	else:
		correlation = max_negative
		correlation_sign = 'negative'
		independent = line[5].replace("\"", "")
		dependent = line[6].replace("\"", "").strip()

		other_correlations = [max_positive, backup_positive, abs(backup_negative)]
		secondary_index = other_correlations.index(max(other_correlations))
		if secondary_index == 0:
			backup_dependent = line[3].replace("\"", "").strip()
			backup_independent = line[2].replace("\"", "")
			backup_correlation = max_positive
			backup_correlation_sign = 'positive'
		elif secondary_index == 1:
			backup_correlation = backup_positive
			backup_correlation_sign = 'positive'
			backup_independent = line[8].replace("\"", "")
			backup_dependent = line[9].replace("\"", "").strip()
		elif secondary_index == 2:
			backup_correlation = max_negative
			backup_correlation_sign = 'negative'
			backup_independent = line[11].replace("\"", "")
			backup_dependent = line[12].replace("\"", "").strip()

		if tertiary_index == 0:
			tertiary_dependent = line[3].replace("\"", "").strip()
			tertiary_independent=line[2].replace("\"", "")
			tertiary_correlation = max_positive
			tertiary_correlation_sign = 'positive'
		elif tertiary_index==1:
			tertiary_correlation=backup_positive
			tertiary_correlation_sign='positive'
			tertiary_independent=line[8].replace("\"", "")
			tertiary_dependent = line[9].replace("\"", "").strip()
		elif tertiary_index==2:
			tertiary_correlation==max_negative
			tertiary_correlation_sign ='negative'
			tertiary_independent = line[11].replace("\"", "")
			tertiary_dependent = line[12].replace("\"", "").strip()

	if dependent == 'ratings':
		dependent = 'rating'
	if backup_dependent == 'ratings':
		backup_dependent = 'rating'

	for entry in csv.reader(open("../UserSummaryStats/"+user_id+".csv")):
		if entry[0] == "hoursslept":
			average_hoursslept[user_id] = entry[1]
		elif entry[0] == "bedtime":
			average_bedtime[user_id] = entry[1] 
		elif entry[0] == "waketime":
			average_waketime[user_id] = entry[1]
		elif entry[0] == "alarm_rings":
			average_alarm[user_id] = entry[1]
		elif entry[0] == 'noisiness':
			average_noisiness[user_id] = entry[1]
		elif entry[0] == 'onsetlatency':
			average_onsetlatency[user_id] = float(entry[1])/float(60)
		elif entry[0] == 'awakeningsPerHour':
			average_awakenings[user_id] = float(entry[1])/float(average_hoursslept[user_id])
		elif entry[0] == 'days_with_alarms':
			days_with_alarms[user_id] = entry[1]
 		elif entry[0].strip() == 'more_than_1_alarm_per_day':
			if entry[1] == 'yes':
				multiple_alarms[user_id] = True
			else:
				multiple_alarms[user_id] = False

	# if the user has only set an alarm on one day, that is not a good correlation to base our recommendatio on, so pick the next highest correlation
	# if the user only sets one alarm per day, we cannot recommend to them to use less alarms because they have no way of waking up, so pick the next highest correlation


	if ((multiple_alarms[user_id]== False and independent.strip()=='alarm')or ((user_id.strip() == 'sleeper12' and independent.strip()=='alarm')or (independent.strip() =='alarm' and dependent.strip()=='awakeningsPerHour'))) or ((independent.strip()=='alarm' and int(days_with_alarms[user_id])<= 1) or (independent.strip() == combinations[user_id][0])):
		independent = backup_independent
		dependent = backup_dependent
		correlation = backup_correlation
		correlation_sign = backup_correlation_sign

	if ((multiple_alarms[user_id]== False and independent.strip()=='alarm')or ((user_id.strip() == 'sleeper12' and independent.strip()=='alarm')or (independent.strip() =='alarm' and dependent.strip()=='awakeningsPerHour'))) or ((independent.strip()=='alarm' and int(days_with_alarms[user_id])<= 1) or (independent.strip() == combinations[user_id][0])):
		independent =tertiary_independent
		dependent = tertiary_dependent
		correlation = tertiary_correlation
		correlation_sign = tertiary_correlation_sign

	if dependent == 'awakeningsPerHour':
		dependent = 'awakenings'
	if dependent == 'ratings':
		dependent = 'rating'

	for entry in csv.reader(open("../phase_lengths/"+user_id+".csv")):
		if entry[0] == 'A1':
			phase_a1[user_id] = entry[1]
		if entry[0] =="B1":
			few[user_id] = entry[1]

	for combination in csv.reader(open("recommendations_3.csv")):
		if user_id not in rec_text:
			fields = combination
			if fields[0].strip() == independent.strip():
				if fields[1].strip() == dependent.strip():
					if fields[2].strip() == correlation_sign.strip():
						x = randint(0,100)

						if ((x > 60) and (x<80)) and len(fields[7])>10:
							rec_text[user_id] = fields[3] + fields[4] + fields[7]#+ fields[7] + fields[8]
						elif (x > 80) and len(fields[8])>10:
							rec_text[user_id] = fields[3] + fields[4] + fields[8]
						else:
							rec_text[user_id] = fields[3] + fields[4] + fields[5]

						rec_text[user_id] = rec_text[user_id].replace("average_bedtime", (average_bedtime[user_id].split(':')[0]+":"+average_bedtime[user_id].split(':')[1]))
						rec_text[user_id] = rec_text[user_id].replace("average_waketime", (average_waketime[user_id].split(':')[0]+":"+average_waketime[user_id].split(':')[1]))
						rec_text[user_id] = rec_text[user_id].replace("average_hoursslept", "{:.2f}".format(float(average_hoursslept[user_id])))	
						rec_text[user_id] = rec_text[user_id].replace("average_alarm", "{:.2f}".format(float(average_alarm[user_id])))
						rec_text[user_id] = rec_text[user_id].replace('average_awakenings',"{:.2f}".format(float(average_awakenings[user_id])))
						rec_text[user_id] = rec_text[user_id].replace('average_onsetlatency',"{:.2f}".format(float(average_onsetlatency[user_id])))
						rec_text[user_id] = rec_text[user_id].replace('FEW', few[user_id])

						# Check if they have less than one alarm on average
						# that means that they probably get up as soon as the alarm rings 
						# so we can't recommend that they decrease alarms, because they only have one
						# so pick a different recommendation! pick the next highest correlatin?
						# if average_alarm < 1:
						rec_text[user_id] = rec_text[user_id].replace("average_noisiness", "{:.2f}".format(float(average_noisiness[user_id])))
						average_waketime_rec = float((average_waketime[user_id].split(':')[0])+"."+str(float(average_waketime[user_id].split(':')[1])/60).split('.')[1])

						if dependent == 'awakenings' or dependent == 'onsetlatency':

							optimal_bedtime_rec = str(meanGenerator.meanNumbers(filename, "bedtime", dependent.strip())[0])
							optimal_bedtime_rec =  optimal_bedtime_rec.split(':')[0]+"."+str(float(optimal_bedtime_rec.split(":")[1])/60).split('.')[1]
							if float(optimal_bedtime_rec) > 20:
								difference = float(average_waketime_rec) + float(24 - float(optimal_bedtime_rec))
							else:
								difference = float(average_waketime_rec) - float(optimal_bedtime_rec)

							if difference >= 7:
								optimal_bedtime_rec = optimal_bedtime_rec.split('.')[0]+":"+str(float(optimal_bedtime_rec.split('.')[1])*60)[0:2]
								rec_text[user_id] = rec_text[user_id].replace("optimal_bedtime", optimal_bedtime_rec)
							else:
								rec_text[user_id] = rec_text[user_id].replace("optimal_bedtime", average_bedtime[user_id].split(':')[0]+":"+average_bedtime[user_id].split(':')[1])
							rec_text[user_id] = rec_text[user_id].replace("optimal_hoursslept", "{:.2f}".format(float(meanGenerator.meanNumbers(filename, "hoursslept", dependent.strip())[0])))

	
						elif dependent == 'rating':
							if 'optimal_bedtime' in rec_text[user_id]:
								rec_text[user_id] = rec_text[user_id].replace("optimal_bedtime", str(meanGenerator.meanNumbers(filename, "bedtime", dependent.strip())[1]))
							if 'optimal_hoursslept' in rec_text[user_id]:
								rec_text[user_id] = rec_text[user_id].replace("optimal_hoursslept", "{:.2f}".format(float(meanGenerator.meanNumbers(filename, "hoursslept", dependent.strip())[1])))
						if 'optimal_waketime' in rec_text[user_id]:
							rec_text[user_id] = rec_text[user_id].replace('optimal_waketime', str(calculate_waketime(user_id)))
						rec_text[user_id] = rec_text[user_id].replace("optimal_hoursslept", "{:.2f}".format(float(meanGenerator.meanNumbers(filename, "hoursslept", dependent.strip())[1])))

# As output we have the dictionary of recommendation texts for each user. 
with open('rec_text.csv', 'wb') as csvfile:
	spamwriter = csv.writer(csvfile)
	for key in rec_text:
		spamwriter.writerow([key, rec_text[key]])

if not os.path.exists("../main_recommendations"):
    os.makedirs("../main_recommendations")

for key in rec_text:
	file_id = "../main_recommendations/"+key+".csv"
	with open(file_id, 'wb') as csvfile:
		spamwriter=csv.writer(csvfile)
		spamwriter.writerow([rec_text[key]])
