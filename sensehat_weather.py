from __future__ import print_function

import datetime
import sys
import time

from sense_hat import SenseHat
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# configurations to be set accordingly
GDOCS_OAUTH_JSON = "raspberry-pi-0f26df464c6e.json"
GDOCS_SPREADSHEET_NAME = "sensehat-weather"
GDOCS_WORKSHEET_NAME = "data"


def get_readings(hat):
    """Get sensor readings and collate them in a dictionary."""
    readings = {}
    readings["datetime"] = datetime.datetime.now()
    readings["temperature"] = hat.temperature
    readings["humidity"] = hat.humidity
    readings["pressure"] = hat.pressure

    # round to 2 decimal places for all readings
    for key, value in readings.copy().items():
        if key != "datetime":
            readings[key] = round(value, 2)
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
        print('Google sheet login failed with error.')
        raise e


def append_readings(worksheet, readings):
    """Append the data in the spreadsheet, including a timestamp."""
    try:
        columns = ["datetime", "temperature", "humidity", "pressure"]
        worksheet.append_row([readings.get(col, '') for col in columns])
        print("Wrote a row to {0}".format(GDOCS_SPREADSHEET_NAME))

    except Exception as e:
        # Error appending data, most likely because credentials are stale.
        # Null out the worksheet so a login is performed.
        print("Append error, logging in again")
        raise e


def main():
    hat = SenseHat()
    hat.clear()

    # get sensor readings
    readings = get_readings(hat)

    # print readings
    print("Time:\t{}".format(readings["datetime"]))
    print("Temperature:\t{}".format(readings["temperature"]))
    print("Humidty:\t{}".format(readings["humidity"]))
    print("Pressure:\t{}".format(readings["pressure"]))

    # upload to google sheet
    for _ in range(30):
        try:
            worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME, GDOCS_WORKSHEET_NAME)
            append_readings(worksheet, readings)
            break
        except Exception as e:
            print(e)
            time.sleep(60)
            continue

    print()


if __name__ == "__main__":
    main()
