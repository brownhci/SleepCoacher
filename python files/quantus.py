import os
import operator
import tempfile
import csv

# if the source_path is a Dropbox folder, it gets the latest file in that folder (assuming that it's timestamped)
#   otherwise, it gets the exact file specified in the filepath
#

def getTempFile():
	fd, file_path = tempfile.mkstemp()
	fp = os.fdopen(fd, 'w')
	return fp, file_path

def getTempCsv():
	fd, file_path = tempfile.mkstemp()
	fp = os.fdopen(fd, 'w')
	csvwriter = csv.writer(fp)
	return csvwriter, file_path

# source_path is the path in Dropbox
def getFileFromDropbox(source_path):
	import quconfig
	import dropbox
	
	client = dropbox.client.DropboxClient(quconfig.DROPBOX_ACCESS_TOKEN)
	fd, filepath = tempfile.mkstemp()
	fp = os.fdopen(fd, 'wb')
	metadata = client.metadata(source_path)
	if metadata['is_dir']:
		most_recent_file = sorted(metadata['contents'], key=operator.itemgetter('path'))[-1] # lambda f: f['path'])[-1]
		filecontent = client.get_file(most_recent_file['path']).read()
	else:
		filecontent = client.get_file(source_path).read()
	fp.write(filecontent)
	fp.close()
	
	return filepath

def getFile(source_url):
	if source_url.count('://') == 0:
		source_location = 'local'
		source_path = source_url
	else:
		source_location, source_path = source_url.split('://')
	if source_location == 'dropbox':
		return getFileFromDropbox(source_path)
	elif source_location == 'local':
		return source_path