#!/usr/bin/python

# # # # # #
# to run: "python download_data.py"
# input: none
# output: a new folder, "User Data", which contains a csv for each of the users

# download data from google drive using the Drive API and pydrive as a wrapper
# in order for this to work, the Sleep As Android folders of each users must be shared with the client email ("id" variable) below. 
# Output files are stored in a newly-created UserData

from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import httplib2 
import os

# create a config.py file in the same folder, where you save your id and key for the google drive api (see below for more details)
import config

# if a folder called "UserData" does not exist yet, make one
if not os.path.exists('../UserData'):
				os.makedirs('../UserData')

# from http://stackoverflow.com/questions/22555433/pydrive-and-google-drive-automate-verification-process
# from google API console 
# In a config.py file, replace id with "client_email" and key with "private_key" from the downloaded json file with the key/value pair
id = config.id
key = config.key
credentials = SignedJwtAssertionCredentials(id, key, scope='https://www.googleapis.com/auth/drive')
credentials.authorize(httplib2.Http())

gauth = GoogleAuth()
gauth.credentials = credentials

http = httplib2.Http()
http = gauth.credentials.authorize(http)

drive_service = build('drive', 'v2', http=http)


r = drive_service.files().list(q = "title = 'Sleep as Android Data'").execute()

def download_file(service, drive_file):
	  """Download a file's content.
	  Args:
	    service: De API service instance.
	    drive_file: Drive File instance.
	  Returns:
	    File's content if successful, None otherwise.
	  """
	  # len(r['items']) is the number of Sleep As Android folders we have shared with this account
	  for i in range(1, len(r['items'])+1):
		  f = service.files().get(fileId = r["items"][i-1]["id"]).execute() 	
		  
		  username = r["items"][i-1]['owners'][0]['emailAddress'].split('@')[0]
		  download_url = f.get('downloadUrl')
		  	# basically download all the files that say sleep as android
		    # but pull the email address as well 
		    # and then save them as email address as identifier
		   	# would need to share that folder with this service account!

		  dataName = "../UserData/"+username+".csv"
		  fo = open(dataName, "wb")
		  if download_url:
		    resp, content = service._http.request(download_url)
		    if resp.status == 200:
		      print 'Success', username
		      fo.write(content)
		      fo.close()
		    else:
		      print 'An error occurred: %s' % resp
		  else:
		    # The file doesn't have any content stored on Drive.
		    print "no content on drive"
	  return None
download_file(drive_service, None)




