# SleepCoacher
How to run SleepCoacher

0)  SELECT AB PHASE DISTRIBUTION

Before anything else, first we generate the sequence of phases for the SleepCoacher experiment. We use a pre-defined script from CITE that we modified for our purposes.  It let us select an AB phase distribution for each participant.
$ Rscript generate_phases.txt
$ python read_phases.py 2 > phases.csv

NOTE: 2 can be replace with any number of participants
output: phases.csv is a csv file in which each line is a random sequence for each participant. Each letter in the sequence represents a day of our 21 day study. 

1) We have pre-loaded some fake sample data already, so you can go on to Step 3. However, in Step 2 we giving instructins on how to download the data in the first place (once you have setup the Google Drive API access, as described in "new_service_account.txt")

2) PULL USER DATA FROM SERVER

$ python download_data.py"

$ rm ../UserData/.DS_Store

output: it creates a folder "UserData" and downloads all the csv files in there, saving them under the sleeperid.  

3) SEPARATE DATA INTO SENSORS AND SLEEP

sleep_as_android.py takes as input one raw user data csv file. This script handles a lot of trickiness with timezones, date and time handling, etc.
To run sleep_as_android.py, just run:

$ python run_sleep_as_android.py

output: 2 files: sleep.csv and sensors.csv. The the output files are saved in two different folders - Sleep and Sensors - under the name of the user. So in folder Sleep, there is currently 1 file, named "sleeper1.csv". Same for the Sensors folder. 

4) FORMAT DATA IN A VIEWER-FRIENDLY WAY AND CALCULATE SLEEP ONSET LATENCY + NUMBER OF AWAKENINGS
input: the files in the UserData folder. 
$ python pullinfo.py

output: a folder "SimpleData"; in that folder there is one file per user with the date, rating, hoursslept, onset latency, total nubmer of awakenings, and number of awakenings per hour for every night. 

5) CALCULATE CORRELATIONS AND SUMMARY STATS
# AND CREATE CORRELATION + summary TABLES FOR EACH USER
input: 

$ python postSleepAnalyzer.py

output: three folders: "UserCorrelations", "UserMaxCorrelations", and "UserSummaryStats". Each folder contains one csv per user. "UserSummaryStats" contains the means and averages for various metrics such as average hours slept, average time the user wakes up and goes to bed, etc. 
Each file in "UserMaxCorrelations" contains the two top highest positive and negative correlations for each user. 
Each file in "UserCorrelations" contains all the correlation coefficients between all the indepedent variables and the dependent variables. 

6) PICK A RECOMMENDATION BASED ON HIGHEST CORRELATION.
We pick the highest correlation for each user based on the ouput from step 4. 

$ python pick_recs.py

output: a folder, "main_recommendatins" which contains one csv for each user. in each csv, there is a single line with the text of the recommendation fo this user.

7) To send the main recommendations, we used a scheduled cron job and mailx.
(in crontab): mailx -s "sleep recommendation" phonenumber@carrier.com < ../main_recommendations/sleeperID.csv

8) GENERATE AND SEND DAILY SLEEP FEEDBACK
$ python get_daily_updates.py
output: a folder called "" that contains a csv file for each user with their daily update. 
We used crontab again to send the daily feedback. 
mailx -s "daily sleep feedback" phonenumber@carrier.com < ../daily_updates/sleeperID.csv

get_daily_updates must be run each day. It gives the daily feedback in relation to today's actual date. If you want to test it, you can change today's date in get_daiy_updates.py to one of the study days and see what it gives you. The sample a random one. 

9) At the end of the experiment, we calculate p-values and differences of means for each participant. 

10) Generate the conclusion messages for each user and send them via crontab. 
mailx -s "sleep recommendation" phonenumber@carrier.com < ../main_recommendations/sleeperID.csv

11) Repeat this cycle, starting from the beginning to generate phases again for the new round.

--- 
Overall, the commands that had to be run every day were saved in "daily.sh" which was a script executed every day.
"cron.txt" contains a sample of the cron jobs used to send messages. 