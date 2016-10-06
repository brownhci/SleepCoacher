from __future__ import division

import time
import os
import csv
import operator
import pytz
from datetime import datetime, timedelta
import quantus

# Description:
#   input: Sleep as Android file format
#   output: sleep_csv(start_time: timestamp_utc, end_time: timestamp_utc, timezone: string, location: geocell, rating: number, noise: float, deep_sleep: float, cycles: number, alarms: list_of_timestamps, comment: string), sensors_csv(timestamp: timestamp_utc, sensor_type: string, value: float)
#
# this extractor ignores the Snore and LenAdjust fields and non-alarm events
#
# note that the movement timestamps are sometimes in a strange timezone and the From/To fields are in the timezone specified in the Tz field
#   so we should just ignore the movement timestamps and use starttime/endtime interpolation to compute the timestamps instead

# CONSTANTS
MOVEMENT_START_COLUMN = 15
# Make folders to store the output files
if not os.path.exists('../Sleep'):
    os.makedirs('../Sleep')
if not os.path.exists('../Sensors'):
    os.makedirs('../Sensors')
    
def main(source_url):

	sleep_csv, sleep_csv_path = quantus.getTempCsv()
	sensors_csv, sensors_csv_path = quantus.getTempCsv()

	sleep_name = '../Sleep/' + source_url.split('/')[2].split('.')[0] + '.csv'

	with open(sleep_name, 'wb') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter=',')
		spamwriter.writerow(['start_time_str', 'end_time_str', 'timezone', 'location', 'rating', 'noisiness', 'deep_sleep', 'cycles', 'alarm_str', 'comment', 'alarm_count'])

		first_start_time = None
		sensor_events = []
		for fields in csv.reader(open(quantus.getFile(source_url))):

			if fields[0] == 'Id':
				fieldnames = list(fields) # just make a copy
			elif fields[0] == '':
				noises = [field for field in fields if field != '']
				if len(noises) > 1:
					noise_interval = (end_time - start_time).total_seconds() / (len(noises) - 1) # -1 because we are assuming there is a noise at wakeup (the endpoint is inclusive)
					for i, noise in enumerate(noises):
						sensor_timestamp = (start_time + timedelta(seconds=i*noise_interval)).astimezone(pytz.utc).replace(microsecond=0).isoformat()[:-6] + 'Z'
						sensor_events.append([sensor_timestamp, 'noise', noise])
				start_time = end_time = None # just to be safe (so we're using the values from the row above us)
			elif fields[0].startswith('1'): # this means it's the row with data. the 1 is the first char of the timestamp/id
				field_values = {}
				movements = []
				events = []
				alarms = []
				alarm_count = 0
				for i, fieldname in enumerate(fieldnames):
					if fieldname == "":
						continue
					if i >= MOVEMENT_START_COLUMN:
						if fieldname == 'Event':
							events.append(fields[i])
						else:
							assert(fieldname.count(':') == 1)
							movements.append((fieldname, float(fields[i]))) # fieldnames are HH:MM 
					else:
						field_values[fieldname] = fields[i]
				for event in events:
					if event.startswith('ALARM_STARTED'):
						alarmtime = time.gmtime(int(event.split('-')[1]) / 1000)
						alarmtime = datetime.fromtimestamp(int(event.split('-')[1])/1000, tz=pytz.utc).replace(microsecond=0).isoformat()[:-6] + 'Z'
						alarms.append(alarmtime)
						alarm_count = alarm_count + 1
					# we could find other events here
				del events

				timezone = field_values['Tz']
				pytztimezone = pytz.timezone(timezone)
				start_time = pytztimezone.normalize(pytztimezone.localize(datetime.strptime(field_values['From'], '%d. %m. %Y %H:%M')))
				if first_start_time is None:
					first_start_time = start_time
				start_time_str = start_time.astimezone(pytz.utc).isoformat()[:-6] + 'Z'
				end_time = pytztimezone.normalize(pytztimezone.localize(datetime.strptime(field_values['To'], '%d. %m. %Y %H:%M')))
				end_time_str = end_time.astimezone(pytz.utc).isoformat()[:-6] + 'Z'
				location = field_values['Geo']
				rating = field_values['Rating']
				hoursslept = field_values['Hours']
				if rating == '0': # no rating
					rating = ''
				noisiness = float(field_values['Noise'])
				if noisiness < 0:
					noisiness = ''
				deep_sleep = float(field_values['DeepSleep']) # computed by app
				if deep_sleep < 0:
					deep_sleep = ''
				cycles = field_values['Cycles']

				alarm_str = '|'.join([str(i) for i in alarms])
				comment = field_values['Comment'].strip()

				if len(movements) > 1:
					movement_interval = (end_time - start_time).total_seconds() / (len(movements) - 1) # -1 because we are assuming there is a noise at wakeup (the endpoint is inclusive)
					for i, movement in enumerate(movements):
						sensor_timestamp = (start_time + timedelta(seconds=i*movement_interval)).astimezone(pytz.utc).replace(microsecond=0).isoformat()[:-6] + 'Z'
						sensor_events.append([sensor_timestamp, 'movement', movement[1]])
				if float(hoursslept) > 2: # int(cycles) > 0 or 
					spamwriter.writerow([start_time_str, end_time_str, timezone, location, rating, noisiness, deep_sleep, cycles, alarm_str, comment, alarm_count])
			else:
				assert(False) # unrecognized line
	sensors_name = '../Sensors/' + source_url.split('/')[2].split('.')[0] + '.csv'
	with open(sensors_name, 'wb') as csvfile1:
		spamwriter1 = csv.writer(csvfile1, delimiter=',')

		sensor_events.sort(key=operator.itemgetter(0))
		spamwriter1.writerows(sensor_events)
	return (sleep_csv_path), (sensors_csv_path)

