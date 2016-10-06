import os
import sleep_as_android

for filename in os.listdir('../UserData/'):
	if filename.endswith('.csv'):
		filename = '../UserData/'+filename
		sleep_csv, sensors_csv = sleep_as_android.main(filename)