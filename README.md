# 2020 Summer Internship [![Code Quality](https://github.com/zcanfes/2020_internship/workflows/Code%20Quality/badge.svg)](https://github.com/zcanfes/2020_internship/actions?query=workflow%3A%22Code+Quality%22) [![Unit Tests](https://github.com/zcanfes/2020_internship/workflows/Unit%20Tests/badge.svg)](https://github.com/lifemote/2020_summer_internship/actions?query=workflow%3A%22Unit+Tests%22)

| QA Criteria  | Status | Info |
|:------------- |:-------------:|:-------------:|
|Documented Integrations|
|Documented Variables|:white_check_mark:|[See below.](#environment-variables)|
|Documented API|
|Project Structure|
|Unit Tests (Dev)|:white_check_mark:|[See below.](#running-unit-tests)|
|System Tests (Dev)|
|Unit Tests (CICD Pipeline)|
|System Tests (CICD Pipeline)|
|Building Containers|:white_check_mark:|
|Deployment|

## About the Project

The project is based on analyzing the raw data from modem’s in the field. The raw data consist
of the daily updates each minute. They contain the device id, update type, neighbors, connected devices,
rssi and so on. 

I was responsible for counting the slow and regular update per hour, counting the
neighbor and station number per hour and calculate the average update duration. Moreover, I was responsible for designing 
a method to detect the dropped updates and analyze the reasons for a dropped update. 

Analyzing the average update duration gives an important conclusion about the dropped updates. From time to time, problems 
with updates from the devices occur. This means less information about the customer
experience and it affects the monitoring outcome; the graphs would be incomplete. Since there are more reasons for an update 
to drop e.g. hardware problems in the field, physical conditions, other software problems etc. this project only focuses on 
the ones that are because of slow update. 

To find reasons why an update is dropped and analyzing every dropped update is necessary
for the improvement of update analysis of devices that are in the field. This way, the customer experience
increases and debugging errors becomes easier.  

## Environment Variables

|            Name         |     Notes      |  
|:-----------------------:|:--------------:|
|       DATA_FOLDER       |Mandatory| 
|       ANALYSIS_FOLDER   |Optional. Default value is `./`|
|       BOUNDARY          |Optional. Used to determine the dropped regular updates. This is a threshold for an update to be considered dropped (time in seconds)| 
|       INSPECT_DROPPED   |Optional. Default value is `True`. If both INSPECT_DROPPED and INSPECT_DATA are false the application won't run. |
|       INSPECT_DATA      |Optional. Default value is `True`. If both INSPECT_DROPPED and INSPECT_DATA are false the application won't run. |
|       SENTRY_DSN        |Optional. |

## Development

### Local Development with Containers 

Use [docker-compose](./docker-compose.yml) after setting $DATA_FOLDER to the directory where the raw data files are in.

```
docker-compose build
docker-compose up
```

### Running Unit Tests

- Local Python Setup: `PYTHONPATH=. pytest`

## Sample Analysis Output

When in INSPECT_DROPPED mode, the application works on time differences of updates. 

Looking at the time difference, the application estimates the number of dropped updates in the interval which lasts longer than $BOUNDARY and which is caused by slow updates.
The time difference between the regular updates around slow updates is calculated and is used to find dropped updates.

The application also returns the count of regular updates and slow updates.

After the analysis is done, an analysis file is created where the user can find the following output:

```
/dataFiles/rawdata.jsonl

regular time greater than 65s: {(1599537380.001, 1599537500.001): 120.0, (1599537681.001, 1599537802.001): 121.0, (1599537981.001, 1599538101.001): 120.0, (1599538282.001, 1599538402.001): 120.0, (1599538581.001, 1599538701.001): 120.0, (1599538882.001, 1599539003.001): 121.0, (1599539182.001, 1599539302.001): 120.0, (1599539784.001, 1599539905.001): 121.0}

(1599538282.001, 1599538402.001): (120.0, 4), 1 possible missing regulars

slow at: 1599527597.001
before slow: (1599527586.001, 1599527597.001) = 11.0
after slow: (1599527597.001, 1599527645.001) = 48.0

slow at: 1599538391.001
before slow: (1599538282.001, 1599538391.001) = 109.0
after slow: (1599538391.001, 1599538402.001) = 11.0

slow at: 1599549191.001
before slow: (1599549151.001, 1599549191.001) = 40.0
after slow: (1599549191.001, 1599549210.001) = 19.0

slow at: 1599559991.001
before slow: (1599559967.001, 1599559991.001) = 24.0
after slow: (1599559991.001, 1599560025.001) = 34.0

slow at: 1599570791.001
before slow: (1599570781.001, 1599570791.001) = 10.0
after slow: (1599570791.001, 1599570839.001) = 48.0

slow at: 1599581595.001
before slow: (1599581535.001, 1599581595.001) = 60.0
after slow: (1599581595.001, 1599581597.001) = 2.0

slow at: 1599592391.001
before slow: (1599592350.001, 1599592391.001) = 41.0
after slow: (1599592391.001, 1599592412.001) = 21.0

slow at: 1599603192.001
before slow: (1599603166.001, 1599603192.001) = 26.0
after slow: (1599603192.001, 1599603227.001) = 35.0

```
The line `(1599538282.001, 1599538402.001): (120.0, 4), 1 possible missing regulars` means the time difference between updates `1599538282.001` and `1599538402.001` is 120.0 seconds.
The updates are in the 4th hour of the day and there is 1 possible dropped regular in that interval. 

The lines 
```
slow at: 1599603192.001
before slow: (1599603166.001, 1599603192.001) = 26.0
after slow: (1599603192.001, 1599603227.001) = 35.0
```
show the timestamp of the slow update and the updates before and after that slow update.
Here the time difference before slow is 26.0 seconds and after slow is 35.0 seconds. In total, the time difference between regular updates is 61.0 seconds.

## Sample Inspect Data Output

When in INSPECT_DATA mode, the application works on the raw data files in the directory DATA_FOLDER and inspects each file one by one. 

```
2020-09-18 00:55:39.404 | INFO     | __main__:main:54 - filename: /dataFiles/rawdata.jsonl
2020-09-18 00:55:39.657 | INFO     | inspect_data:latest_ver:44 - version: [11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, None, None, None, None]
2020-09-18 00:55:39.777 | INFO     | inspect_data:latest_dr_ver:66 - no driver version in hours: [0, 1, 3, 4, 6, 7, 9, 10, 12, 13, 15, 16, 18, 19]
2020-09-18 00:55:39.778 | INFO     | inspect_data:latest_dr_ver:67 - driver version: [None, None, '2.76.12.2.671', None, None, '2.76.12.2.671', None, None, '2.76.12.2.671', None, None, '2.76.12.2.671', None, None, '2.76.12.2.671', None, None, '2.76.12.2.671', None, None, None, None, None, None]
2020-09-18 00:55:39.779 | INFO     | inspect_data:neighbor_count:110 - neighbors: [0, 0, 21, 21, 21, 20, 20, 20, 20, 20, 20, 23, 23, 23, 19, 19, 19, 22, 22, 22, 0, 0, 0, 0]
2020-09-18 00:55:39.902 | INFO     | inspect_data:station_count:85 - stations: [0, 0, 13, 0, 0, 14, 0, 0, 14, 0, 0, 16, 0, 0, 23, 0, 0, 26, 0, 0, 0, 0, 0, 0]
2020-09-18 00:55:39.905 | INFO     | inspect_data:avg_upd_not_dropped:131 - average upd duration if not dropped:59.74s
2020-09-18 00:55:39.906 | INFO     | inspect_data:get_device_type:148 - {'F4:17:B8:7F:A4:BC': 18}
2020-09-18 00:55:39.906 | SUCCESS  | __main__:main:64 - file /dataFiles/rawdata.jsonl completed
```

You can see the filename in the first line. This is the raw data to be inspected. 

The next lines contains the information about the raw data such as version, driver version, number of neighbors, number of stations in each hour. 

After that, the average update duration is given. This average is calculated for updates that does not imply a dropped update.

The device id and device type can be found in `{'F4:17:B8:7F:A4:BC': 18}` 

If the application completes the process without any errors, a SUCCESS message will be displayed.



