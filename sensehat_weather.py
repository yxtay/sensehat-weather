from __future__ import print_function

import datetime
import sys
import time

from sense_hat import SenseHat
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# configurations to be set accordingly
GDOCS_OAUTH_JSON = "raspberry-pi-sensortag-97386df66227.json"
GDOCS_SPREADSHEET_NAME = "sensehat-weather"
GDOCS_WORKSHEET_NAME = "data"
FREQUENCY_SECONDS = 295


def get_readings(hat):
    """Get sensor readings and collate them in a dictionary."""
    readings = {}
    readings["temperature"] = hat.temperature
    readings["humidity"] = hat.humidity
    readings["pressure"] = hat.pressure

    # round to 2 decimal places for all readings
    readings = {key: round(value, 2) for key, value in readings.items()}
    return readings


def login_open_sheet(oauth_key_file, spreadsheet_name, worksheet_name):
    """Connect to Google Docs spreadsheet and return the first worksheet."""
    try:
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(oauth_key_file, scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open(spreadsheet_name).worksheet(worksheet_name)
        return worksheet

    except Exception as e:
        print('Unable to login and get spreadsheet. '
              'Check OAuth credentials, spreadsheet name, '
              'and make sure spreadsheet is shared to the '
              'client_email address in the OAuth .json file!')
        print('Google sheet login failed with error:', e)
        sys.exit(1)


def append_readings(worksheet, readings):
    """Append the data in the spreadsheet, including a timestamp."""
    try:
        columns = ["temperature", "humidity", "pressure"]
        worksheet.append_row([datetime.datetime.now()] + [readings.get(col, '') for col in columns])
        print("Wrote a row to {0}".format(GDOCS_SPREADSHEET_NAME))
        return worksheet

    except Exception as e:
        # Error appending data, most likely because credentials are stale.
        # Null out the worksheet so a login is performed.
        print("Append error, logging in again")
        print(e)
        return None


def main():
    hat = SenseHat()
    hat.clear()
    worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME, GDOCS_WORKSHEET_NAME)

    print('Logging sensor measurements to {0} every {1} seconds.'.format(GDOCS_SPREADSHEET_NAME, FREQUENCY_SECONDS))
    print('Press Ctrl-C to quit.')
    while True:
        # get sensor readings
        readings = get_readings(hat)

        # print readings
        print("Time:\t{}".format(datetime.datetime.now()))
        print("Temperature:\t{}".format(readings["temperature"]))
        print("Humidty:\t{}".format(readings["humidity"]))
        print("Pressure:\t{}".format(readings["pressure"]))

        worksheet = append_readings(worksheet, readings)
        # login if necessary.
        if worksheet is None:
            worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME, GDOCS_WORKSHEET_NAME)
            continue

        print()
        time.sleep(FREQUENCY_SECONDS)


if __name__ == "__main__":
    main()
