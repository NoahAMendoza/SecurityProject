
from __future__ import print_function
import httplib2
import os

from apiclient import errors
from apiclient import http

from apiclient import discovery
from apiclient.discovery import build
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload

import urllib

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive.file'
CLIENT_SECRET_FILE = 'client_id.json'
APPLICATION_NAME = 'CSE7339_Project'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """


    #returns the home directory of the current user
    #in this case, C:\Users\Noah Mendoza
    home_dir = os.path.expanduser('~')
    print(home_dir)

    #joins ".credentials" to the directory string found above
    credential_dir = os.path.join(home_dir, '.credentials')
    print(credential_dir)

    #If the there is no folder bearing the path we're looking for, create it
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)

    #Create final version of the path that will be used to create the json file    
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    #creates and OAuth storage object with a lock on credential_path (i think)
    #maybe its not actually a lock. This is wierd
    store = Storage(credential_path)
    print(store)

    #store.get returns an OAuth credentials object
    credentials = store.get()
    print(credentials)

    #this is the OAuth flow that gets run if the credentials arent already stored
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def createService():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())

    #returns a resource object with methods for interacting with the service
    #parameters, servicename = drive, version = v3, http = http variable above
    service = discovery.build('drive', 'v2', http=http)

    return service


#uploads a file with the specified name. If no file with the matching name is found, create it
#RETURNS: data about the file that was uploaded
def uploadFile(filename):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())

    drive = discovery.build('drive', 'v3', http=http)
    
    file_metadata = {}
    file_metadata['name'] = filename
    file_metadata['mimeType'] = "text/plain"
    #     'name' : 'myReport',
    #     'mimeType' : 'text/plain'
    # }  
    
    media = MediaFileUpload('myReport.csv',mimetype='text/plain',resumable=True)
    file = drive.files().create(body=file_metadata,media_body=media,fields='id').execute()
    print('File ID:' + file.get('id'))


#downloads a file with the specifed filename
#RETURNS: data about the file, or file not found if no such file exists
def downloadFile(filename):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())

    drive = discovery.build('drive', 'v2', http=http)
    r = drive.files().list().execute()
    files =  r['items']
    for file in files: 
        if 'downloadUrl' in file.keys() and file['title'] == filename:
            print(file['title'] +  " : " + file['downloadUrl'])
            response, content = http.request(file['downloadUrl'])
            print(response['status'])
            print(response['content-disposition'])

            f = open(filename, 'wb')
            f.write(content)
            f.close()
            return None

    return None


#deletes a file with the specified filename
#RETURNS: data about the file, or file not found if no such file exists

def deleteFile(filename):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    drive = discovery.build('drive', 'v2', http=http)

    file_ID = findCorrespondingID(filename)

    if not file_ID:
        print("No file to delete")
        return None

    print(drive.files().get(fileId= file_ID).execute())
    try:   
        results = drive.files().delete(fileId = file_ID).execute()
        print (results)
    except errors.HttpError, error:
        print ('An error occurred: ')
        print(error)

    return None

def listFiles():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    drive = discovery.build('drive', 'v2', http=http)

    results = drive.files().list().execute()
    files = results['items']
    for file in files:
        print(file['title'])
    
    ##
    return None

def findCorrespondingID(filename):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())

    drive = discovery.build('drive', 'v2', http=http)
    r = drive.files().list().execute()
    files =  r['items']
    for file in files: 
        if file['title'] == filename:
            print("Found " + filename + " ---- File ID: " + file["id"])
            return file["id"]

    print("File not found")
    return None

if __name__ == '__main__':
    #downloadFile("oceanman.txt")
    downloadFile("oceanman.txt")
    #findCorrespondingID("oceanman.txt")
    #deleteFile("oceanman.txt")
    #createService()
    #listFiles()
    #deleteFile("testFileName.txt")
    #uploadFile("oceanman.txt")
