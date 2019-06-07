# Weather Station with Sense HAT on Raspberry Pi

Records temperature, humidity and pressure data periodically into Google Spreadsheet with a scheduled cron task.

Based on 
[Mini Weather Station](https://www.hackster.io/idreams/make-a-mini-weather-station-with-a-raspberry-pi-447866) 
on hackster.io and modified to run as a cron task.

## Setup

```bash
# clone the repo
git clone https://github.com/yxtay/sensehat-weather.git && cd sensehat-weather

# install dependencies
pip install -r requirements.txt --user
```

## Download OAuth credentials file for Google API

Follow the `gspread` documentation instructions to obtain OAuth credentials from Google Developers Console.

http://gspread.readthedocs.io/en/latest/oauth2.html

Download the credentials json file and copy it into the project directory in your Raspberry Pi.

```bash
# assuming credentials file is in the current directory
scp credentials.json pi@192.168.1.5:sensehat-weather/
```

## Create Google Sheet

Create a Google Spreadsheet and name it as you desire.

Rename the default worksheet as you desire.

Open up the credentials json file in the previous step 
and note the email address under the `client_email` field. 
Share the spreadsheet with that email address.

## Schedule cron task

Open crontab in the Raspberry Pi.

```bash
crontab -e
```

Copy the following line into crontab.
This schedules the task to run every 5 mins.

```bash
*/5 * * * * cd $HOME/sensehat-weather && python sensehat_weather.py
```

## Usage

Use optional arguments if your configurations are different from defaults.

```
usage: sensehat_weather.py [-h] [--credentials-json CREDENTIALS_JSON]
                           [--spreadsheet SPREADSHEET] [--worksheet WORKSHEET]
                           [--log LOG]

Take readings from SenseHat and add to Google Spreadsheet.

optional arguments:
  -h, --help            show this help message and exit
  --credentials-json CREDENTIALS_JSON
                        path to Google OAuth credentials json file (default: credentials.json)
  --spreadsheet SPREADSHEET
                        name of Google Spreadsheet to save SenseHat readings (default: sensehat-weather)
  --worksheet WORKSHEET
                        name of worksheet to save SenseHat readings (default: data)
  --log LOG             path of log file (default: main.log)
```

## Logs

By default logs are written to `main.log` in the project directory.
