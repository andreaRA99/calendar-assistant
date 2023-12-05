import datetime
import os.path
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def main():
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    # Set the timezone for Victoria, BC
    victoria_tz = pytz.timezone('America/Vancouver')

    today = datetime.datetime.utcnow()#.astimezone(victoria_tz)
    days_until_next_monday = (0 - today.weekday() + 7)
    start_from = today + datetime.timedelta(days=days_until_next_monday)
    start_from = start_from.replace(hour = 0, minute = 0,second = 0, microsecond = 0)
    end_at = start_from + datetime.timedelta(days=1)

    events_week = []
    
    for each in range(0,7):
        print('each = ', each)
        print('START FROM', start_from)
        print('ENDING AT ', end_at)
        events_result = (
            service.events()
            .list(
                calendarId="primary", # specifying calendar from which to retrieve list of events
                timeMin=start_from.isoformat() + "Z",
                timeMax = end_at.isoformat() + "Z", # Minimun start time for events to be retrieved
                #maxResults=1,  # Limits number of events to e retrieved
                singleEvents=True, # Recurring events should be exanded into individual ones
                orderBy="startTime",
            )
            .execute() # sends the constructed request to the Google Calendar API and retrieves response 
        )
        events = events_result.get("items", [])
        for each in events: 
          start = each["start"].get("dateTime", each["start"].get("date"))
          print(start, each["summary"])
        events_week.append(events)
        #print('on day' +  each +  events)
        start_from = end_at
        end_at = end_at + datetime.timedelta(days=1)
        if not events:
            print("No upcoming events found.")
            #return

    # Prints the start and name of the next 10 events
    for day in events_week:
      print('next day!')
      for event in day: 
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(start, event["summary"])

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()