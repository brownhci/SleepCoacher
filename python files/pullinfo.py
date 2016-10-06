import os
import csv
import datetime
import numpy as np

DATA_PATH = '../UserData/'
MOVEMENT_START_COLUMN = 15

allvariables = []
lastLine = 21

if not os.path.exists('../SimpleData'):
    os.makedirs('../SimpleData')

mylist = []
today = datetime.date.today()
mylist.append(today)
# print mylist[0] # print the date object, not the container 
mylist[0] = str(mylist[0])
day = mylist[0].split('-')[2]
month = mylist[0].split('-')[1]
year = mylist[0].split('-')[0]

formatted_today = day+"."+month+'.'+year

def processMovements(movements):
	if sum([m[1] for m in movements]) <= 0.1: # something wrong with the accelerometer
		return None, None

	#print ','.join([str(i[1]) for i in movements])

	# assumes hhmmss2 is earlier than hhmmss1
	def hourSubtract(hhmmss1, hhmmss2): # returns seconds
		hh1, mm1, ss1 = [int(num) for num in hhmmss1.split(':')]
		hh2, mm2, ss2 = [int(num) for num in hhmmss2.split(':')]
		if hh1 < hh2:
			hh1 += 24
		return (hh1 * 60 * 60 + mm1 * 60 + ss1) - (hh2 * 60 * 60 + mm2 * 60 + ss2)

	awakenings = []
	onsetlatency = None
	lastActivity = movements[0][0] + ':00'
	isAwake = True
	lasthhmm = None
	lastss = 0
	for m in movements:
		movementLevel = m[1]
		if m[0] == lasthhmm:
			lastss += 10
			# assert(lastss < 60) # assert fails due to data polling uneveness
			if lastss > 59:
				lastss = 59
			hhmmss = lasthhmm + ':' + str(lastss)
		else:
			hhmmss = m[0] + ':00'
			lastss = 0
		lasthhmm = m[0]
		if movementLevel >= 0.98:
			if hourSubtract(hhmmss, lastActivity) < 2 * 60:
				if not isAwake:
					awakenings.append(lastActivity)
				isAwake = True
			lastActivity = hhmmss
		else:
			continuousInactivity = hourSubtract(hhmmss, lastActivity)
			if continuousInactivity >= 2 * 60:
				isAwake = False
			if continuousInactivity >= 20 * 60 and onsetlatency is None:
				onsetlatency = hourSubtract(lastActivity, movements[0][0] + ':00') # in seconds
				assert(onsetlatency >= 0)

	return onsetlatency, awakenings

for filename in os.listdir(DATA_PATH):
	skip = False

	name = '../SimpleData/'+filename
	with open(name, 'wb') as csvfile:	
		datawriter = csv.writer(csvfile, delimiter = ',')
		datawriter.writerow(['date', 'rating', 'hoursslept', 'onsetlatency', 'awakenings', 'awakeningsPerHour', 'fromTime', 'wakeTime'])
		for fields in csv.reader(open(DATA_PATH + filename), delimiter=',', quotechar='"'):
			if fields[0] == 'Id':
				fieldnames = list(fields)
			elif fields[0] == '':
				if skip:
					continue
			elif fields[0].startswith('14'): 
				tempfieldstore = {}
				movements = []
				events = []

				for i, fieldname in enumerate(fieldnames):

					if i >= MOVEMENT_START_COLUMN:
						if fieldname == 'Event':
							events.append(fields[i])
						else:
							movements.append((fieldname, float(fields[i])))
					else:
						tempfieldstore[fieldname] = fields[i]

				fromTime = tempfieldstore['From'].split()

				wakeTime = tempfieldstore['To'] #.split()
				# print wakeTime

				hour = fromTime[3].split(':')[0]

				date = fromTime[0][:-1]
				date = str(fromTime[0])+str(fromTime[1])+str(fromTime[2])
				full_date = date

				month = fromTime[1][:-1]
				
				hoursslept = tempfieldstore['Hours']
				cycles = tempfieldstore['Cycles']	
				onsetlatency, awakenings = processMovements(movements)
				if awakenings is None:
					numawakenings = None
				else:
					numawakenings = len(awakenings)
				
				rating = float(tempfieldstore['Rating'])
				if rating == 0:
					rating = 'none'
				toTime = tempfieldstore['To']

				### awakenings per hour ####
				if awakenings is not None:
					try:
						awakeningsPerHour = float(numawakenings)/float(hoursslept)
					except:
						awakeningsPerHour = float('Inf')
				else:
					awakeningsPerHour = 'none'

				if float(hoursslept) <= 2: #or int(cycles) < 1:
							skip
				else:
					allvariables.append(rating)
					datawriter.writerow([full_date, rating, hoursslept, onsetlatency, numawakenings, awakeningsPerHour, fromTime[3], wakeTime])#[3]])

											

username = filename.split('.')[0]


