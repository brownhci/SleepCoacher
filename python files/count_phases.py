import csv
import os

start_B1 = {}
start_A2 = {}
start_B2 = {}

A1_length = {}
B1_length = {}
A2_length = {}
B2_length = {}
counter = 1

for line in csv.reader(open("phases_2.csv")):
	index = 0
	for char in line:
		while str(char)[index] == 'A':
			index  = index + 1
		start_B1[counter] = index

		while str(char)[index] == 'B':
			index = index + 1
		start_A2[counter] = index

		while str(char)[index] == 'A':
			index = index + 1
		start_B2[counter] = index

	# print line	
	A1_length[counter] = start_B1[counter]
	A2_length[counter] = start_B2[counter]-start_A2[counter]
	B1_length[counter] = start_A2[counter]-start_B1[counter]
	B2_length[counter] = len(char)-start_A2[counter]-A2_length[counter]
	
	counter = counter + 1
print "A1_length", A1_length
print "B1_length", B1_length
print "A2_length", A2_length
print "B2_length", B2_length
print

# for key in A1_length:
# 	start_date_B1[counter]=8+A1_length[counter]
# 	start_date_A2[counter]=8+B1_length+A1_length
	# start_date_B2[counter]=8+start_date_A2

# print start_date_B1
# print start_date_A2
# print start_date_B2

if not os.path.exists("../phase_lengths_2"):
    os.makedirs("../phase_lengths_2")

for key in A1_length:
	if key < 20:
		file_id = "../phase_lengths_2/"+"sleeper"+str(key)+".csv"
	elif key == 20:
		file_id = "../phase_lengths_2/"+"sleeper24.csv"
	elif key == 21:
		file_id = "../phase_lengths_2/"+"sleeper25.csv"
	with open(file_id, 'wb') as csvfile:
		spamwriter=csv.writer(csvfile)
		spamwriter.writerow(['A1', A1_length[key]])
		spamwriter.writerow(['B1', B1_length[key]])
		spamwriter.writerow(['A2', A2_length[key]])
		spamwriter.writerow(['B2', B2_length[key]])
