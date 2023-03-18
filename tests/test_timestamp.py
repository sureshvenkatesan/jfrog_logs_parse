import datetime
# from dateutil import parser
from dateutil import parser

# pip install python-dateutil
# Parse timestamp string with 9 decimal places
timestamp_str_1 = '2023-02-27T23:45:21.387872128Z'
timestamp_1 = parser.isoparse(timestamp_str_1)
print(timestamp_1)

# Parse timestamp string with 3 decimal places
timestamp_str_2 = '2022-09-23T09:07:10.247Z'
# following works
timestamp_2 = datetime.datetime.strptime(timestamp_str_2, '%Y-%m-%dT%H:%M:%S.%fZ')
timestamp_2 = parser.isoparse(timestamp_str_2)
print(timestamp_2)

# Parse timestamp string with 6 decimal places
timestamp_str_3 = '2022-09-23T09:07:10.247234Z'
# timestamp_3 = datetime.datetime.strptime(timestamp_str_3, '%Y-%m-%dT%H:%M:%S.%fZ')
timestamp_3 = parser.isoparse(timestamp_str_3)
print(timestamp_3)

timestamp_str_4 = '2022-09-23T09:07:10Z'
# timestamp_3 = datetime.datetime.strptime(timestamp_str_3, '%Y-%m-%dT%H:%M:%S.%fZ')
timestamp_4 = parser.isoparse(timestamp_str_4)
print(timestamp_4)