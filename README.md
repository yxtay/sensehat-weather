# Weather Station with Sense HAT on Raspberry Pi

Records temperature, humidity and pressure data periodically into Google Spreadsheet with a scheduled cron task.

Based on 
[Mini Weather Station](https://www.hackster.io/idreams/make-a-mini-weather-station-with-a-raspberry-pi-447866) 
on hackster.io and modified to run as a cron task.

## Setup

```sh
# clone the repo
git clone https://github.com/yxtay/sensehat-weather.git && cd sensehat-weather

# install dependencies
pip install -r requirements.txt --user
```

## Download OAuth credentials file for Google API

Follow the `gspread` documentation instructions to obtain OAuth credentials from Google Developers Console.

http://gspread.readthedocs.io/en/latest/oauth2.html

Download the credentials json file and copy it into the project directory in your Raspberry Pi.

```sh
# assuming credentials file is in the current directory
scp credentials.json pi@192.168.1.5:sensehat-weather/
```

## Create Google Sheet

Create a Google Spreadsheet and name it as you desire.

Rename the default worksheet as you desire.

Open up the credentials json file in the previous step 
and note the email address under the `client_email` field. 
Share the spreadsheet with that email address.

## Configure variables

Set the variables at the top of `sensehat-weather.py` file accordingly.
They are pretty self-explanatory.

## Schedule cron task

Open crontab in the Raspberry Pi.

```sh
crontab -e
```

Copy the following line into crontab.
This schedules the task to run every 5 mins.

```sh
*/5 * * * * cd $HOME/sensehat-weather && python sensehat_weather.py
```

## Logs

Logs are written into the `LOG_FILE` specified in `sensehat-weather.py`. By default the file is `out.log` in the project directory.
