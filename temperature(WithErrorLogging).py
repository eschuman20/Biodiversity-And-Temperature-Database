# A python script used to extract temperatures from OpenWeather and send them to a Google Sheet
# Weather data provided by OpenWeather
# https://openweathermap.org/
# Code Developed By Worcester Polytechnic Students: Eric Schuman & Lily Bromberger
# For an extensive guide on how to edit this code, please refer to the "Maintaining Biodiversity
# and Temperature Database Manual"

# %%
############ Error Logging ###############
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Creating a file handler to write the error logs to a file
# PATH OF ERROR LOGGER TEXT FILE
handler = logging.FileHandler(r'PATH TO ERROR LOGGER TEXT FILE')
handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
try:
    ############# Modifiers ###############
    # File Path of Google Drive API Credentials (JSON file)
    credential_path = r'PATH TO GOOGLE CREDENTIALS'

    # Specific Google Sheet
    google_sheet_name = 'GOOGLE SHEET NAME'
    google_worksheet_name = "GOOGLE WORKSHEET NAME"

    # Coordinates
    latitude = 0000000
    longitude = 0000000

    # OpenWeather API Key
    open_weather_key = 'OPENWEATHER API KEY'


    ############# Create Google Sheet ################
    # %%
    def createSheet():
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        from gspread_dataframe import set_with_dataframe
        import pandas as pd

        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

        credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_path, scope)
        client = gspread.authorize(credentials)

        # Open a Google Sheet
        spreadsheet = client.open(google_sheet_name)

        # Open a new worksheet
        worksheet = spreadsheet.add_worksheet(title=google_worksheet_name, rows=10, cols=10)

        # Create Dataframe
        cols = ['date', 'hour','temp', 'humidity']
        df = pd.DataFrame(columns=cols)

        # Add data to worksheet
        set_with_dataframe(worksheet=worksheet, dataframe=df, include_index=False, include_column_header=True, resize=True)
        print("New Sheet Created")


    ############ Update Google Sheet ###########################
    # %%
    def add_data():
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials

        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

        credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_path, scope)
        client = gspread.authorize(credentials)

        # Open a Google Sheet
        spreadsheet = client.open(google_sheet_name)

        from pyowm import OWM
        import pandas as pd
        import datetime as datetime
        import json

        # Get the weather data at specific coordinates
        owm = OWM(open_weather_key)
        mgr = owm.weather_manager()
        w = mgr.weather_at_coords(latitude, longitude).weather

        # Record weather data
        humidity = w.humidity
        temp = w.temperature('celsius')
        current_temp = temp['temp']

        # Find current date and hour of the day
        date = json.dumps(datetime.date.today(), default=str).replace('"', '')
        hour = json.dumps(datetime.datetime.now().hour, default=str).replace('"', '')

        # Create a new row of weather data
        dict = {"date": date,
                "hour": hour,
                "temp": current_temp,
                "humidity": humidity,
                }
        df = pd.DataFrame(dict, index=[1])
        row = df.values.tolist()
        spreadsheet.values_append(google_worksheet_name, {'valueInputOption': 'USER_ENTERED'}, {'values': row})
        print("Sheet Updated")

    ########## Manually Collecting Data ###########
    # %%
    # Create Inital Sheet
    #createSheet()

    # Refresh
    #add_data()

    ######### Automatic Refresh ###############
    # %%
    add_data()

# Write all errors to the error logger
except Exception as e:
    print("error")
    print(e)
    logger.error('An error occurred', exc_info=True)
