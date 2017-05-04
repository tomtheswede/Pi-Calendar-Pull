from __future__ import print_function
import httplib2
import os
import time

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

#TODO: 

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'
resetTrigger=True


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 20 events')
    try:
        eventsResult = service.events().list(
            calendarId='l3mvqk399k73ehoais4bu6lc74@group.calendar.google.com', timeMin=now, maxResults=20, singleEvents=True,
            orderBy='startTime').execute()
        events = eventsResult.get('items', [])
        if not events:
            print('No upcoming events found.')
        text_file = open("scheduledActions.txt", "wb") #May want to use a check on the msg type to only overwrite calendar tasks
        # text_file.write(bytes('Updated '+now[:-8]+'\n','UTF-8'))
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start = start[:22] + start[-2:] #Trims the last colon
            start = datetime.datetime.strptime(start,'%Y-%m-%dT%H:%M:%S%z')
            start = int(time.mktime(start.timetuple()))
            end = event['end'].get('dateTime', event['end'].get('date'))
            end = end[:22] + end[-2:] #Trims the last colon
            end = datetime.datetime.strptime(end,'%Y-%m-%dT%H:%M:%S%z')
            end = int(time.mktime(end.timetuple()))
            description = event['description']
            if description.count(',')==5:
                desc1=description.split(",")[0] + "," + description.split(",")[1] + "," + description.split(",")[2]
                print(start,desc1)
                writeString=str(start)+','+desc1+"\n"
                text_file.write(bytes(writeString,'UTF-8'))
                desc2=description.split(",")[3] + "," + description.split(",")[4] + "," + description.split(",")[5]
                print(end,desc2)
                writeString=str(end)+','+desc2+"\n"
                text_file.write(bytes(writeString,'UTF-8'))
            else:
                print(start, description) #event['summary'] event['location']
                writeString=str(start)+','+description+"\n"
                text_file.write(bytes(writeString,'UTF-8'))
        text_file.close()
        print('Calendar read complete.')
    except httplib2.ServerNotFoundError:
        print("!---- Looks like there's no internet connection just now. Wait till tomorrow.")
    
triggerTime="02:39"
print("Waiting till",triggerTime, "for calendar update.")

while True:
    if time.strftime('%H:%M:%S')==triggerTime+":00":
        resetTrigger=True
    if time.strftime('%H:%M:%S')==triggerTime+":02" and resetTrigger==True:
        print("Checking at " + time.strftime('%H:%M'))
        main()
        print("--- Sleeping a bit")
        time.sleep(86395)
