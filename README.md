# Creating A Biodiversity and Temperature Database

A subgoal of an Interactive Qualifying Project (A partial fulfillment of a Bachelors of Science Degree from Worcester Polytechnic Institute) was to create a method to extract biodiversity data from iNaturalist and temperature data from OpenWeather and send the data to a Google Sheet database. 

For an extensive guide of setting up and maintaining the database, please refer to the instruction manual and videos on our website: xxxxxxxxxxx.

Developed by Worcester Polytechnic Institute Students: Eric Schuman & Lily Bromberger

# Biodiversity Data Collection From iNaturalist
There are two Python scripts available in this repository that follow the same code, except one write errors to an error logger. If you are looking to automate the biodiversity collection, you should use the script with error logging. We automated our script on a linux server so that it would run our "refresh" function to refresh the database every day. There are also functions called "createSheet" to make an initial Google Sheet, as well as "retrieve" and "update" functions that retrieve data and update the Google Sheet. The code also requires Google Service Account credentials (to let Python edit the Google Sheet). You can also specify coordinate bound regions for the data collection using geojson files created in QGIS or another geographical information service. Before running these scripts make sure to fix all of the paths and variables that are specific to the user (often labeled "LIKE THIS"), and follow the directions in our manual. 
