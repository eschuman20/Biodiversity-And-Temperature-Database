# A python script used to extract biodiversity data from iNaturalist and send it to a Google Sheet
# Biodiversity data provided by iNaturalist
# https://inaturalist.org/
# Code Developed By Worcester Polytechnic Students: Eric Schuman & Lily Bromberger
# For an extensive guide on how to edit this code, please refer to the "Maintaining Biodiversity
# and Temperature Database Manual"

########## Import Pyinaturalist ##########################
from pyinaturalist import *
from pyinaturalist_convert import *
import datetime as datetime
import os

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

    # %%
    ############# Modifiers ###############
    # ID of INaturalist Project
    project_id = 0000000

    # File Path of Google Drive API Credentials (JSON file)
    credential_path = r'PATH TO GOOGLE DRIVE API CREDENTIALS'

    # Text file that holds date of last update
    last_date_file_path = "PATH TO LAST UPDATE TEXT FILE"

    # File Paths of Geographical Regions
    whole_property_path = r'PATH TO GEOJSON REGION'
    grasslands_path = r'PATH TO GEOJSON REGION'
    heat_haven_path = r'PATH TO GEOJSON REGION'
    open_field_path = r'PATH TO GEOJSON REGION'
    food_forest_path = r'PATH TO GEOJSON REGION'
    community_garden_path = r'PATH TO GEOJSON REGION'
    play_bush_tucker_path = r'PATH TO GEOJSON REGION'
    real_bush_tucker_path = r'PATH TO GEOJSON REGION'
    far_garden_path = r'PATH TO GEOJSON REGION'
    # Lists of regions and filepaths (geo_regions are the names of the columns corresponding to their paths)
    geo_regions = ['Grasslands', 'Heat Haven', 'Open Field', 'Food Forest', 'Community Garden', 'Play Bush Tucker',
                   'Real Bush Tucker', 'Far Garden']
    geo_paths = [grasslands_path, heat_haven_path, open_field_path, food_forest_path, community_garden_path,
                 play_bush_tucker_path, real_bush_tucker_path, far_garden_path]

    # Specific google sheet
    google_sheet_name = 'GOOGLE SHEET NAME'
    google_worksheet_name = "GOOGLE WORKSHEET NAME"

    # Column Structure - only modify if the Google Sheet structure is being altered by adding or deleting columns
    # This will cause the column numbers to shift which may break the code
    # Unless the positions of these specific columns in the dataframe are also updated.
    column_structure = ['quality_grade', 'observed_on_details.date', 'observed_on_details.month',
                        'observed_on_details.hour', 'observed_on_details.year', 'observed_on_details.day',
                        'id', 'identifications_most_agree', 'species_guess', 'identifications_most_disagree',
                        'reviewed_by', 'description', 'updated_at', 'taxon.endemic', 'taxon.threatened',
                        'taxon.introduced','taxon.native', 'taxon.name', 'taxon.rank', 'taxon.extinct', 'taxon.id',
                        'taxon.wikipedia_url', 'taxon.default_photo.medium_url', 'taxon.iconic_taxon_name',
                        'taxon.preferred_common_name', 'num_identification_agreements', 'comments', 'uri',
                        'geojson.coordinates', 'user.login', 'photo_url']

    id_col_num = 7  # Used for Google sheet column number since it counts from 1 and not 0
    id_col_in_google_sheet = "G2:G"   # ID column is column G in google sheets
    google_sheet_col_range = "A2:AM"  # Start in A2 to avoid first row (header), AM is the last column in the sheet

    # Retrieve date of last update (don't modify this unless running code manually)
    if os.path.exists(last_date_file_path):
        with open(last_date_file_path, "r") as file:
            last_update = file.read().strip()
            print("Updating From: " + last_update)
    else:
        print("Cannot find the text file")
        last_update = "2023-01-01"   # Manually write the date you want to update from (yyyy-mm-dd)

    # %%
    ############## Retrieve Data ##############################
    def retrieve():
        observations = []
        page_results = [1]
        p = 1
        while len(page_results) > 0:
            # Get all observations occurring after the previous update
            page = get_observations(project_id=project_id, updated_since=last_update, date_field="observed", page=p,
                                     per_page=60, identified=True)
            page_results = page["results"]
            observations += page_results
            p += 1
            print("Number of New Observations: " + str(len(observations)))
        # Send observations to DataFrame
        df = to_dataframe(observations)

        # Set number of observations to a global variable
        global num_observations
        num_observations = len(observations)

        # If we have new data since previous update
        if num_observations != 0:
            potential_empty_labels = ['species_guess', 'description', 'taxon.wikipedia_url',
                                      'taxon.preferred_common_name', ]
            # Add these columns even if they are empty
            for label in potential_empty_labels:
                if label not in df.columns:
                    df.insert(loc=0, column=label, value='')

            df_new = df.drop(df.columns, axis=1)
            df_new = df[column_structure]
            df = df_new

            # Create new columns
            df['number_of_reviews'] = df['reviewed_by'].apply(lambda x: len(x))
            australian_season_map = {1: 'Summer', 2: 'Summer', 3: 'Autumn', 4: 'Autumn',
                                     5: 'Autumn', 6: 'Winter',7: 'Winter', 8: 'Winter',
                                     9: 'Spring', 10: 'Spring', 11: 'Spring', 12: 'Summer'}
            df['australian_season'] = df['observed_on_details.month'].apply(lambda x: australian_season_map[x])
            aboriginal_season_map = {1: 'Birak', 2: 'Bunuru', 3: 'Bunuru', 4: 'Djeran',
                                     5: 'Djeran', 6: 'Makuru', 7: 'Makuru',8: 'Djilba',
                                     9: 'Djilba',10: 'Kambarang', 11: 'Kambarang', 12: 'Birak'}
            df['aboriginal_season'] = df['observed_on_details.month'].apply(lambda x: aboriginal_season_map[x])
            hour_map = {1: 'Night', 2: 'Night', 3: 'Night', 4: 'Night', 5: 'Night', 6: 'Morning',
                        7: 'Morning', 8: 'Morning', 9: 'Morning', 10: 'Morning', 11: 'Morning',
                        12: 'Afternoon', 13: 'Afternoon', 14: 'Afternoon', 15: 'Afternoon', 16:
                            'Afternoon', 17: 'Afternoon', 18: 'Evening', 19: 'Evening', 20: 'Evening',
                        21: 'Evening', 22: 'Evening', 23: 'Evening', 0: 'Night'}
            df['time_of_day'] = df['observed_on_details.hour'].apply(lambda x: hour_map[x])
            df['longitude'] = df['geojson.coordinates'].str[0]
            df['latitude'] = df['geojson.coordinates'].str[1]

            # Determine what geographical region the observation is in
            from shapely.geometry import Point, Polygon
            import json
            regions = {}
            for i in range(len(geo_paths)):
                with open(geo_paths[i]) as f:
                    geo_data = json.load(f)
                polygon = Polygon(geo_data['features'][0]['geometry']['coordinates'][0][0])
                regions[geo_regions[i]] = polygon
            # Create a new column 'region' and assign the region that the point is in
            df['region'] = df.apply(lambda row: next(
                (region for region, polygon in regions.items() if point_in_poly((row['longitude'], row['latitude']), polygon)),
                'None'), axis=1)

            # Create a new column that states whether the observation was observed on the property
            with open(whole_property_path) as f:
                geo_data = json.load(f)
                polygon = Polygon(geo_data['features'][0]['geometry']['coordinates'][0][0])
                df['on_property?'] = df.apply(lambda row: Point(row['longitude'], row['latitude']).within(polygon), axis=1)

            # return the dataframe of retrieved results
            return df
        # If no new data return empty dataframe
        else:
            return df


    # %%
    ############ Helper Function to check if a point is within a polygon ############
    from shapely.geometry import Point, Polygon
    def point_in_poly(point, polygon):
        x, y = point
        poly = Polygon(polygon)
        return poly.contains(Point(x, y))

    # %%
    ############# Create Google Sheet ##################
    def createSheet(df):
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        from gspread_dataframe import set_with_dataframe

        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

        credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_path, scope)
        client = gspread.authorize(credentials)

        # Open a Google Sheet
        spreadsheet = client.open(google_sheet_name)

        # Open a new worksheet
        worksheet = spreadsheet.add_worksheet(title=google_worksheet_name, rows=10, cols=10)

        # Add data to worksheet
        set_with_dataframe(worksheet=worksheet, dataframe=df, include_index=False, include_column_header=True, resize=True)
        print ("New Sheet Created")


    # %%
    ############ Update Google Sheet ################################
    def update(df):
        # Only update if there are new observations or updated observations
        if num_observations != 0:
            import gspread
            from oauth2client.service_account import ServiceAccountCredentials
            import pandas as pd

            scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                     "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

            credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_path, scope)
            client = gspread.authorize(credentials)

            # Open a Google Sheet
            spreadsheet = client.open(google_sheet_name)

            # Create a new dataframe filling null values with empty strings and dropping the index column
            df.to_csv("new.csv")
            new_data = pd.read_csv("new.csv")
            new_data = new_data.fillna('')
            new_data.drop(columns=new_data.columns[0], axis=1, inplace=True)

            # Save the new dataframe values as a list
            df_values = new_data.values.tolist()

            # Select a worksheet
            worksheet1 = spreadsheet.worksheet(google_worksheet_name)

            # Get all the ID's of past and new observations
            old_values = worksheet1.get(id_col_in_google_sheet)
            new_values = new_data.get('id')

            # Append all the ID's of past and new observations to lists
            lst_old = []
            lst_old.append(0)
            for ID in old_values:
                lst_old.append(*ID)
            lst_old = [int(i) for i in lst_old]
            lst_new = []
            lst_new.append(0)
            for ID in new_values:
                lst_new.append(ID)

            # Remove old rows that have been updated (have same ID as new rows)
            count = 0 # Count of deleted rows
            for ID in new_values:
                # If the ID was already in the spreadsheet
                if ID in lst_old:
                    old_row_num = lst_old.index(ID)  # find which row it is in current spreadsheet
                    # Delete the row (its row number is its old row number + 1 (since first row in spreadsheet is the
                    # header) and - the count of the rows deleted before it
                    worksheet1.delete_rows(old_row_num + 1 - count, old_row_num + 1 - count)
                    count += 1
            # Add all new and updated rows to the spreadsheet
            spreadsheet.values_append(google_worksheet_name, {'valueInputOption': 'USER_ENTERED'}, {'values': df_values})
            num_rows = len(worksheet1.get_all_values())
            # Sort the observations by ID
            worksheet1.sort((id_col_num, 'des'), range=google_sheet_col_range + str(num_rows))
            print("Successful Update")
        else:
            print("There Are No Updates")


    # %%
    ########## Refresh ##############
    def refresh():
        print("Refreshing....")
        update(retrieve())
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        # Update text file with current date
        try:
            with open(last_date_file_path, "w") as file:
                file.write(current_date)
            print("Automatic Refresh Complete")
        except:
            print("Manual Refresh Complete")


    ########## Manually Collecting Data ###########
    # %%
    # Create initial sheet
    #x = retrieve()
    #createSheet(x)

    # Refresh
    #refresh()

    ######### Automatic Refresh #########
    # %%
    refresh()

# Write all errors to the error logger
except Exception as e:
    print("error")
    print(e)
    logger.error('An error occurred', exc_info=True)