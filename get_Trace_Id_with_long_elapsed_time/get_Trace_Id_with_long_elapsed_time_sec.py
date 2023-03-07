"""
DISCLAIMER:
Your use of this code is governed by the following license:JFrog hereby grants you a non-
exclusive, non-transferable, non-distributable right to use this code solely in connection with
your use of a JFrog product or service. This code is provided 'as-is' and without any warranties or
conditions, either express or implied including, without limitation, any warranties or conditions
of title, non-infringement, merchantability or fitness for a particular cause. Nothing herein shall
convey to you any right or title in the code, other than for the limited use right set forth
herein. For the purposes hereof "you" shall mean you as an individual as well as the organization
on behalf of which you are using the software and the JFrog product or service.
"""

"""
Usage: print all traceid and duration greater than 10 seconds

python get_Trace_Id_with_long_elapsed_time_sec.py ./iss1_impact_anal_missing/chrisDaw_test/202302281747-jfxr_jfxr_jfxr@01fn44xyc9bjn01ebfnj6thp9t ./iss1_impact_anal_missing/chrisDaw_test/tmp3 2023-02-27T23:30:00 2023-02-28T00:30:59 10
"""
import argparse
import os
import re
from datetime import datetime, timedelta

def parse_args():
    parser = argparse.ArgumentParser(description="Parse log files for long elapsed times in  a specific time window")
    parser.add_argument("log_folder", type=str, help="path to the folder containing log files")
    parser.add_argument("output_folder", type=str, help="path to the folder where the trace_id files will be created")
    parser.add_argument("start_time", type=str, help="start time of the time window in ISO 8601 format (e.g. '2023-02-28T00:00:00')")
    parser.add_argument("end_time", type=str, help="end time of the time window in ISO 8601 format (e.g. '2023-02-28T23:59:59')")
    parser.add_argument('duration', type=float, help='Duration threshold in seconds')
    return parser.parse_args()

def parse_time(timestamp_str):
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return timestamp
    except ValueError:
        return None

def find_unique_trace_ids(log_folder, start_time, end_time, duration):
    # regular expression pattern to match durations in various formats
    pattern = re.compile(r".*elapsed: ((\d+)h)?((\d+)m)?([\d\.]+)(s|ms|µs)")
    unique_trace_ids = {}
    for root, dirs, files in os.walk(log_folder):
        for file in files:
            if file.startswith("xray")  and file.endswith(".log"):
                log_file = os.path.join(root, file)
                with open(log_file) as f:
                    for line in f:
                        timestamp_str = line[:26]
                        timestamp = parse_time(timestamp_str)
                        if timestamp and start_time <= timestamp <= end_time  and "(elapsed:" in line:
                            match = pattern.findall(line)
                            if match:
                                elapsed_in_seconds = 0
                                for m in match:
                                    if m[1]:
                                        elapsed_in_seconds += int(m[1]) * 3600
                                    if m[3]:
                                        elapsed_in_seconds += int(m[3]) * 60
                                    if m[4]:
                                        if m[5] == 's':
                                            elapsed_in_seconds += float(m[4])
                                        elif m[5] == 'ms':
                                            elapsed_in_seconds += float(m[4]) / 1000
                                        elif m[5] == 'µs':
                                            elapsed_in_seconds += float(m[4]) / 1000000
                                if elapsed_in_seconds > duration:
                                    match = re.search(r"\[([a-f\d]{16})\]", line)
                                    if match:
                                        trace_id = re.search(r"\[([a-f\d]{16})\]", line).group(1)
                                        if trace_id not in unique_trace_ids:
                                            unique_trace_ids[trace_id] = (timestamp , elapsed_in_seconds)

    sorted_unique_trace_ids = [(i, k, v[0], v[1]) for i, (k, v) in
                               enumerate(sorted(unique_trace_ids.items(), key=lambda x: x[1]))]

    return sorted_unique_trace_ids

def display_unique_trace_ids(sorted_unique_trace_ids):
    # Print the unique trace ids sorted by the timestamp in ascending order
    for pos, trace_id, timestamp, elapsed_in_seconds  in sorted_unique_trace_ids:
        print(f'{pos + 1} - {trace_id} at {timestamp} took {elapsed_in_seconds}s')

def open_trace_id_files(output_folder, sorted_unique_trace_ids):
    trace_id_files = {}
    for pos, trace_id, timestamp , elapsed_in_seconds in sorted_unique_trace_ids:
        trace_id_file = os.path.join(output_folder, f'{pos+1}-{trace_id}-{str(timestamp).replace(" ", "-")}.txt')
        trace_id_files[trace_id] = open(trace_id_file, "a")
    return trace_id_files

def process_log_files(log_folder, sorted_unique_trace_ids, trace_id_files):
    for root, dirs, files in os.walk(log_folder):
        for file in files:
            if file.startswith("xray")  and file.endswith(".log"):
                log_file = os.path.join(root, file)
                logged_log_file_details_in_trace_ids = []
                with open(log_file) as f:
                    previous_matched_trace_id = None
                    for line in f:
                        matched_trace_id = None
                        if any(item[1] in line for item in sorted_unique_trace_ids):
                            pos, matched_trace_id, timestamp , elapsed_in_seconds = next(
                                item for item in sorted_unique_trace_ids if item[1] in line)
                            trace_id_file = trace_id_files[matched_trace_id]
                            if matched_trace_id not in logged_log_file_details_in_trace_ids:
                                logged_log_file_details_in_trace_ids.append(matched_trace_id)
                                trace_id_file.write(
                                    f'=========================={os.linesep}{root}{os.linesep}{file}{os.linesep}')
                            trace_id_file.write(line)
                            previous_matched_trace_id = matched_trace_id
                        elif previous_matched_trace_id is not None:
                            timestamp_str = line[:26]
                            timestamp = parse_time(timestamp_str)
                            if timestamp:
                                previous_matched_trace_id = None
                            else:
                                if not (file.startswith("router") and file.endswith(".log")):
                                    trace_id_file = trace_id_files[previous_matched_trace_id]
                                    trace_id_file.write(line)

def close_trace_id_files(open_trace_id_files):
    for f in open_trace_id_files.values():
        f.close()

def main():
    args = parse_args()
    start_time = datetime.fromisoformat(args.start_time)
    end_time = datetime.fromisoformat(args.end_time)
    sorted_unique_trace_ids = find_unique_trace_ids(args.log_folder, start_time, end_time, args.duration)
    display_unique_trace_ids(sorted_unique_trace_ids)
    trace_id_files = open_trace_id_files(args.output_folder, sorted_unique_trace_ids)
    process_log_files(args.log_folder, sorted_unique_trace_ids, trace_id_files)
    close_trace_id_files(trace_id_files)

if __name__ == '__main__':
    main()