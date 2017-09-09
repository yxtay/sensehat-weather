from argparse import ArgumentParser
import datetime
import sys
import time

from sense_hat import SenseHat
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from logger import get_logger

# logging
logger = get_logger(__name__)


def get_readings(hat):
    """Get sensor readings and collate them in a dictionary."""
    readings = dict()
    readings["datetime"] = datetime.datetime.now()
    readings["temperature"] = hat.temperature
    readings["humidity"] = hat.humidity
    readings["pressure"] = hat.pressure

    # round to 2 decimal places for all readings
    for key in readings.copy():
        if key in {"temperature", "humidity", "pressure"}:
            readings[key] = round(readings[key], 2)
    logger.debug("readings obtained.")
    return readings


def login_open_sheet(oauth_key_file, spreadsheet_name, worksheet_name):
    """Connect to Google Docs spreadsheet and return the first worksheet."""
    try:
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(oauth_key_file, scope)
        gc = gspread.authorize(credentials)
        logger.debug("google account authorised.")
        worksheet = gc.open(spreadsheet_name).worksheet(worksheet_name)
        logger.debug("google sheet obtained: %s.", worksheet_name)
        return worksheet

    except Exception as e:
        logger.warning("google sheet login failed. "
                       "check OAuth credentials, spreadsheet name, sheet name"
                       "and make sure spreadsheet is shared to the "
                       "client_email address in the OAuth .json file!")
        raise e


def append_readings(worksheet, readings):
    """Append the data in the spreadsheet, including a timestamp."""
    try:
        columns = ["datetime", "temperature", "humidity", "pressure"]
        worksheet.append_row([readings.get(col, '') for col in columns])
        logger.debug("readings appended to %s.", worksheet.title)

    except Exception as e:
        # Error appending data, most likely because credentials are stale.
        # Null out the worksheet so a login is performed.
        logger.warning("appending error. credentials are probably stale. "
                       "logging in again.")
        raise e


if __name__ == "__main__":
    arg_parser = ArgumentParser(description="Take readings from SenseHat and add to Google Spreadsheet.")
    arg_parser.add_argument("--oauth-json", default="credentials.json",
                            help="path to Google OAuth credentials json file")
    arg_parser.add_argument("--spreadsheet", default="sensehat-weather",
                            help="name of Google Spreadsheet to save SenseHat readings")
    arg_parser.add_argument("--worksheet", default="data",
                            help="name of worksheet to save SenseHat readings")
    arg_parser.add_argument("--log", default="main.log",
                            help="path of log file")
    args = arg_parser.parse_args()

    logger = get_logger(__name__, args.log)
    logger.debug("call: %s.", " ".join(sys.argv))
    logger.debug("ArgumentParser: %s.", args)

    # connect sense hat
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
            worksheet = login_open_sheet(args.oauth_json, args.spreadsheet, args.worksheet)
            append_readings(worksheet, readings)
            break
        except Exception as e:
            logger.exception(e)
            time.sleep(240)
            continue
