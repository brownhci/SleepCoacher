import os
import csv
import re
import sys
import random 

counter = 0
options = {}

for line in csv.reader(open("output.csv"), delimiter=','):
	if counter != 0:
		if '     [' in line:
			total_number_of_options = counter-1 
		else:
			line[1] = line[1].replace('"', '').strip()
			line[1] = line[1].replace(' ', '').strip()
			option_id = int(line[0].split('[')[1])
			if option_id not in options:
				options[option_id] = [line[1].split(']')[1]]
			else:
				options[option_id].append(line[1].split(']')[1])

	counter = counter + 1
flattened = {}
for option_id in options:
	flattened[option_id] = [val for sublist in options[option_id] for val in sublist]
	flattened[option_id] = ''.join(flattened[option_id])
# given some number of participants, pick a random phase sequence for each of them
sequence = {}
total_users = int(sys.argv[1])
for user in range(1,total_users+1):
	random_sequence= random.randint(1,total_number_of_options)
	sequence[user] = flattened[random_sequence]

#RANDOM SEQUENCE FOR EACH USER ON A NEW LINE
for item in sequence:
	print sequence[item] 


