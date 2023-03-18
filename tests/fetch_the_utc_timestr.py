import re

from datetime import datetime, timedelta
from dateutil import parser
"""
usage: python fetch_the_utc_timestr.py sample_xray_log_lines.log
"""



# 2023-02-27T23:45:21.387872128Z  cannot parsed by the following function. How to fix it ?
# Is this valid ?
# parse following to timestamp in python:
# 2023-02-27T23:45:21.387872128Z
# 2022-09-23T09:07:10.247Z
# 2022-09-23T09:07:10.247234Z

# def parse_time(timestamp_str):
#     try:
#         timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
#         return timestamp
#     except ValueError:
#         try:
#             timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%fZ')
#             return timestamp
#         except ValueError:
#             try:
#                 timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%f%fZ')
#                 return timestamp
#             except ValueError:
#                 return None

def parse_time(timestamp_str):
    try:
        # timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        timestamp = parser.isoparse(timestamp_str)
        return timestamp
    except ValueError:
        return None

with open('sample_xray_log_lines.log', 'r') as file:
    for line in file:
        match = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+Z', line)
        if match:
            timestamp_str = match.group(0)
            # process the line with the timestamp
            if parse_time(timestamp_str):
                print(f'{timestamp_str} in {line}' )
            else:
                print(f'{timestamp_str} not in correct format')

