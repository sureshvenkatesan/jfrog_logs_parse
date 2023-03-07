"""
In python how to parse a xray-analysis-service.log file lines logged in UTC and get lines witin a time window that have [ERROR] . From this extract the trace id   61d9270fe5a5e349

2023-02-28T00:01:03.654235512Z [33m[jfxan][0m [1m[31m[ERROR][0m [61d9270fe5a5e349] [user_components_dao:1735      ] [main                ] Failed to get user component table id for component 'pe://Microsoft® .NET:6.0.422.16404'. err: failed to fetch user component table id

To parse a xray-analysis-service.log file in Python and extract lines within a specific time window that have an [ERROR] message, you can use the datetime and re modules.

Usage: python get_Trace_Id_with_ERROR_from_jfxana.py support-bundele-unzip-folder output_folder 2023-02-27T23:30:00 2023-02-28T00:30:59
Example:
python get_Trace_Id_with_ERROR_from_jfxana.py ./iss1_impact_anal_missing/chrisDaw_test/202302281747-jfxr_jfxr_jfxr@01fn44xyc9bjn01ebfnj6thp9t ./iss1_impact_anal_missing/chrisDaw_test/tmp2 2023-02-27T23:30:00 2023-02-28T00:30:59

"""
import argparse
import os
import re
from datetime import datetime, timedelta

def parse_args():
    # Define the argparse arguments
    parser = argparse.ArgumentParser(description="Parse log files for errors within a specific time window")
    parser.add_argument("log_folder", type=str, help="path to the folder containing log files")
    parser.add_argument("output_folder", type=str, help="path to the folder where the trace_id files will be created")
    parser.add_argument("start_time", type=str, help="start time of the time window in ISO 8601 format (e.g. '2023-02-28T00:00:00')")
    parser.add_argument("end_time", type=str, help="end time of the time window in ISO 8601 format (e.g. '2023-02-28T23:59:59')")
    return parser.parse_args()

def parse_time(timestamp_str):
    try:
        # Parse the timestamp from the log line
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return timestamp
    except ValueError:
        # To Skip lines that don't start with a valid timestamp return None
        return None

def find_unique_trace_ids(log_folder, start_time, end_time):
    # Set the regex pattern to match lines with [ERROR] and extract the trace id
    pattern = r"\[ERROR\].*\[(?P<trace_id>[a-f0-9]{16})\]"
    # Initialize a dictionary to store unique trace ids and their timestamps
    unique_trace_ids = {}
    # Loop over each directory and its subdirectories recursively
    for root, dirs, files in os.walk(log_folder):
        # Loop over each file in the current directory
        for file in files:
            # Check if the file matches the pattern "xray-analysis-service*.log"
            if file.startswith("xray-analysis-service") and file.endswith(".log"):
                # Build the full path to the log file
                log_file = os.path.join(root, file)
                
                # Open the log file and read line by line
                with open(log_file) as f:

                    for line in f:
                        timestamp_str = line[:26]
                        timestamp = parse_time(timestamp_str)
                        # Check if the line is within the time window and matches the regex pattern and has "[ERROR]"
                        if timestamp and start_time <= timestamp <= end_time and "[ERROR]" in line:
                            match = re.search(pattern, line)
                            if match:
                                trace_id = match.group("trace_id")
                                if trace_id not in unique_trace_ids:
                                    unique_trace_ids[trace_id] = timestamp
    
    # Sort the dictionary by value (timestamp) in ascending order and store as tuple in a list
    # example: [(0, 'f02b59ef1fbc357b', datetime.datetime(2023, 2, 27, 23, 30, 50, 380110)), (1, '2e66de966533dd54', datetime.datetime(2023, 2, 27, 23, 32, 52, 990673))]
    sorted_unique_trace_ids = [(i, v[0], v[1]) for i, v in enumerate(sorted(unique_trace_ids.items(), key=lambda x: x[1]))]
    return sorted_unique_trace_ids

def display_unique_trace_ids(sorted_unique_trace_ids):
    # Print the unique trace ids sorted by the timestamp in ascending order
    for pos, trace_id, timestamp in sorted_unique_trace_ids:
        print(f'{pos + 1} - {trace_id} at {timestamp}')


def open_trace_id_files(output_folder, sorted_unique_trace_ids):
    # Create a dictionary to hold the open file objects
    trace_id_files = {}
    # Loop over each trace ID and open the corresponding file
    for pos, trace_id, timestamp in sorted_unique_trace_ids:
        # the trace_id_file name starts with 1 based pos index ( by using pos+1) which serves as the total number of trace_id's with ERROR as well.
        trace_id_file = os.path.join(output_folder, f'{pos+1}-{trace_id}-{str(timestamp).replace(" ", "-")}.txt')
        trace_id_files[trace_id] = open(trace_id_file, "a")
    return trace_id_files

def process_log_files(log_folder, sorted_unique_trace_ids, trace_id_files):
    # Loop over each file in the log_folder and its subdirectories
    for root, dirs, files in os.walk(log_folder):
        # Loop over each file in the current directory
        for file in files:
            # Check if the file matches the pattern "xray-*.log or router*.log"
            if (file.startswith("xray") or file.startswith("router")) and file.endswith(".log"):
                # Build the full path to the log file
                log_file = os.path.join(root, file)
                # keep track of the {trace_id}.txt file(s) where we logged this log_file details
                logged_log_file_details_in_trace_ids = []
                # Open the log file and read line by line
                with open(log_file) as f:
                    # if the line does not start with a timestamp then it must be some error or stacktrace from the
                    # previous_matched_trace_id line
                    previous_matched_trace_id = None
                    for line in f:
                        matched_trace_id = None
                        # check if any of the trace_id from sorted_unique_trace_ids tuple list are in the line
                        if any(item[1] in line for item in sorted_unique_trace_ids):
                            pos, matched_trace_id, timestamp = next(
                                item for item in sorted_unique_trace_ids if item[1] in line)
                            trace_id_file = trace_id_files[matched_trace_id]

                            # write the log_file details in the trace_id_file only once
                            if matched_trace_id not in logged_log_file_details_in_trace_ids:
                                logged_log_file_details_in_trace_ids.append(matched_trace_id)
                                trace_id_file.write(
                                    f'=========================={os.linesep}{root}{os.linesep}{file}{os.linesep}')
                            # Write the current line to the corresponding trace id file
                            trace_id_file.write(line)
                            previous_matched_trace_id = matched_trace_id
                        elif previous_matched_trace_id is not None:
                            # Parse the timestamp from the log line
                            timestamp_str = line[:26]
                            timestamp = parse_time(timestamp_str)
                            if timestamp:
                                # this line starts with a timestamp. So it may have a blank trace_id or a trace_id for which there is no ERROR
                                previous_matched_trace_id = None
                            else:
                                # this line does not start with a timestamp . It is is not a router-request.log this line must be part of a stacktrace from the
                                # previous_matched_trace_id line
                                if not (file.startswith("router") and file.endswith(".log")):
                                    trace_id_file = trace_id_files[previous_matched_trace_id]
                                    trace_id_file.write(line)

def close_trace_id_files(open_trace_id_files):
    # Close all the trace ID files
    for f in open_trace_id_files.values():
        f.close()

def main():
    # Parse the command-line arguments
    args = parse_args()
    # Parse the start and end times from the command-line arguments
    # Note that this assumes that the input strings are in ISO 8601 format ( example: 2023-02-27T23:30:00 ).
    start_time = datetime.fromisoformat(args.start_time)
    end_time = datetime.fromisoformat(args.end_time)

    sorted_unique_trace_ids = find_unique_trace_ids(args.log_folder, start_time, end_time)
    display_unique_trace_ids(sorted_unique_trace_ids)

    trace_id_files = open_trace_id_files(args.output_folder, sorted_unique_trace_ids)
    
    process_log_files(args.log_folder, sorted_unique_trace_ids, trace_id_files)
    # Close all the trace ID files
    close_trace_id_files(trace_id_files)

if __name__ == '__main__':
    main()

