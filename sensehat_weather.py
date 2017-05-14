from __future__ import print_function

import datetime
import logging
import logging.handlers
import time

from sense_hat import SenseHat
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# configurations to be set accordingly
GDOCS_OAUTH_JSON = "raspberry-pi-0f26df464c6e.json"
GDOCS_SPREADSHEET_NAME = "sensehat-weather"
GDOCS_WORKSHEET_NAME = "data"
LOG_FILE = "out.log"

# logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=2 ** 20, backupCount=2)
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


def get_readings(hat):
    """Get sensor readings and collate them in a dictionary."""
    logger.debug("getting readings.")
    readings = dict()
    readings["datetime"] = datetime.datetime.now()
    readings["temperature"] = hat.temperature
    readings["humidity"] = hat.humidity
    readings["pressure"] = hat.pressure

    # round to 2 decimal places for all readings
    for key, value in readings.copy().items():
        if key != "datetime":
            readings[key] = round(value, 2)
    logger.debug("completed getting readings.")
    return readings


def login_open_sheet(oauth_key_file, spreadsheet_name, worksheet_name):
    """Connect to Google Docs spreadsheet and return the first worksheet."""
    try:
        logger.debug("authenticating google account.")
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(oauth_key_file, scope)
        gc = gspread.authorize(credentials)
        logger.debug("google account authorised.")
        worksheet = gc.open(spreadsheet_name).worksheet(worksheet_name)
        logger.debug("google sheet {} obtained.".format(worksheet_name))
        return worksheet

    except Exception as e:
        logger.exception(e)
        logger.warning("google sheet login failed. "
                       "check OAuth credentials, spreadsheet name, sheet name"
                       "and make sure spreadsheet is shared to the "
                       "client_email address in the OAuth .json file!")
        raise e


def append_readings(worksheet, readings):
    """Append the data in the spreadsheet, including a timestamp."""
    try:
        logger.debug("appending readings to {}.".format(worksheet.title))
        columns = ["datetime", "temperature", "humidity", "pressure"]
        worksheet.append_row([readings.get(col, '') for col in columns])
        logger.debug("appended readings to {}.".format(worksheet.title))

    except Exception as e:
        # Error appending data, most likely because credentials are stale.
        # Null out the worksheet so a login is performed.
        logger.exception(e)
        logging.warning("appending error. credentials are probably stale. "
                        "logging in again.")
        raise e


def main():
    logger.debug("start of main function.")
    hat = SenseHat()
    hat.clear()
    logger.debug("sense hat connected.")

    # get sensor readings
    readings = get_readings(hat)

    # print readings
    logger.info("time: {}, temperature: {:.2f}, humidity: {:.2f}, pressure: {:.2f}"
                .format(*[readings[key] for key in ["datetime", "temperature", "humidity", "pressure"]]))

    # upload to google sheet
    for _ in range(30):
        try:
            worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME, GDOCS_WORKSHEET_NAME)
            append_readings(worksheet, readings)
            break
        except Exception as e:
            logger.warning(e)
            time.sleep(120)
            continue

    logger.debug("end of main function.")


if __name__ == "__main__":
    main()
