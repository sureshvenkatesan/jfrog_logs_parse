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

python get_Trace_Id_with_long_elapsed_time/get_Trace_Id_with_long_elapsed_time_sec_in_RT.py \
/Users/sureshv/Documents/From_Customer/xyz/245256_500_err/Artifactory500s \
/Users/sureshv/Documents/From_Customer/xyz/245256_500_err/build_500_err \
2023-03-28T00:00:00Z 2023-03-29T23:59:59Z 0 --trace_ids  "3c8f9b72dad6208f,402a4cb23857cf0,42807c5da98480f2"

or
--trace_ids "6874e79577a3907 ,402a4cb23857cf0 "
"""
import argparse
import os
import re
from datetime import datetime, timedelta
from dateutil import parser
import glob

def parse_args():
    parser = argparse.ArgumentParser(description="Parse log files for long elapsed times in  a specific time window")
    parser.add_argument("log_folder", type=str, help="path to the folder containing log files")
    parser.add_argument("output_folder", type=str, help="path to the folder where the trace_id files will be created")
    parser.add_argument("start_time", type=str, help="start time of the time window in ISO 8601 format "
                                                     "(e.g. '2023-02-28T00:00:00Z')")
    parser.add_argument("end_time", type=str, help="end time of the time window in ISO 8601 format "
                                                   "(e.g. '2023-02-28T23:59:59Z')")
    parser.add_argument('duration', type=float, help='Duration threshold in seconds')
    parser.add_argument('--trace_ids', type=str, help='comma-separated list of trace IDs to process')
    return parser.parse_args()


def parse_time(timestamp_str):
    """
    Parses a timestamp string in ISO 8601 format and returns a corresponding datetime object.

    Args:
        timestamp_str (str): A string containing a timestamp in ISO 8601 format.

    Returns:
        datetime: A datetime object representing the parsed timestamp, or None if the timestamp string
            could not be parsed.
    """
    try:
        # timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        timestamp = parser.isoparse(timestamp_str)
        return timestamp
    except ValueError:
        return None


def find_elapsed_time(line):
    """Parse a line of log file to extract elapsed time in seconds.

    Args:
        line (str): A line of log file containing elapsed time information.

    Returns:
        float: The elapsed time in seconds parsed from the log line. Returns 0 if elapsed time is not found in the line.

    """
    # regular expression pattern to match durations in various formats
    pattern_to_get_elapsed_time = re.compile(r".*elapsed: ((\d+)h)?((\d+)m)?([\d\.]+)(s|ms|µs)")

    elapsed_time_match_found = pattern_to_get_elapsed_time.findall(line)
    if elapsed_time_match_found:
        elapsed_in_seconds = 0
        for m in elapsed_time_match_found:
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

        return elapsed_in_seconds
    else:
        return 0


def find_unique_trace_ids(log_folder, start_time, end_time, threshold_in_sec, selected_trace_ids=None):
    """
    Searches for unique trace IDs in the log files within the specified time window.

    Args:
        log_folder (str): The path to the folder containing the log files.
        start_time (str): The start time of the time window in ISO 8601 format.
        end_time (str): The end time of the time window in ISO 8601 format.
        threshold_in_sec (float): The duration threshold in seconds.
        selected_trace_ids (list): A list of trace IDs to search for. Defaults to None. When specified only traces
                                   containing one or more of these trace IDs will be considered.

    Returns:
        list: A list of tuples containing the unique trace IDs, sorted by the timestamp in ascending order.
              Each tuple contains the following elements:
              - Position of the trace ID in the sorted list.
              - Trace ID (16-digit hex string or 15-digit with last char as space).
              - Timestamp when the trace ID was first seen.
              - Timestamp when the trace ID first exceeded the duration threshold in the specified time window.
              - Elapsed time (in seconds) for the first occurrence when the trace ID exceeded the threshold.
              - Timestamp when the trace ID last exceeded the duration threshold in the specified time window.
              - Elapsed time (in seconds) for the last occurrence when the trace ID exceeded the threshold.
    """
    unique_trace_ids = {}

    """
    Define the order of files to be searched. Files omitted in this list are:
    'access-audit',
    'access-request',
    'access-security-audit',
    'access-service',
    'artifactory-metrics',
    'artifactory-metrics_events',
    'event-request',
    'event-service',
    'frontend-metrics',
    'frontend-request',
    'frontend-service',
    'integration-request',
    'integration-service',
    'metadata-',
    'observability-'
    'router-service'      
    """
    file_order = [
        'artifactory-request',
        'artifactory-service',
        'artifactory-access',
        'artifactory-binarystore',
        'artifactory-request-out',
        'router-request'
    ]

    # Search for the unique trace IDs in the log files
    for file_prefix in file_order:
        # search the specified folder and its subdirectories recursively and return
        # a list of file paths that match the given pattern
        log_files = glob.glob(os.path.join(log_folder, '**', f'{file_prefix}*.log'), recursive=True)
        # sort the list of files based on their modification time in ascending order (i.e., oldest to most recent)
        log_files.sort(key=os.path.getmtime)

        # Read the log files and parse the lines
        for log_file in log_files:
            with open(log_file) as f:
                for line in f:
                    # Filter the trace IDs if selected_trace_ids is not None
                    if selected_trace_ids:
                        if not any(item in line for item in selected_trace_ids):
                            continue
                    # Find the timestamp in the line
                    time_match = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+Z', line)
                    if time_match:
                        timestamp_str = time_match.group(0)
                        timestamp = parse_time(timestamp_str)

                        # Check if the timestamp is within the specified time range
                        if timestamp and start_time <= timestamp <= end_time:
                            # Find the trace ID in the line which may be 15 or 16 chars [402a4cb23857cf0 ] or [3c8f9b72dad6208f]
                            # trace_id_match_found = re.search(r"\[([a-f\d]{16})\]", line)
                            trace_id_match_found = re.search(r"\[([a-fA-F\d]{15,16})\s*\]", line)
                            if trace_id_match_found:
                                trace_id = trace_id_match_found.group(1)

                                # Store the trace ID and associated values
                                if trace_id not in unique_trace_ids:
                                    # tracking the traceid for the first time
                                    unique_trace_ids[trace_id] = (timestamp, 0, 0, 0, 0)

                                elapsed_in_seconds = find_elapsed_time(line)
                                if elapsed_in_seconds >= threshold_in_sec:
                                    time_trace_id_first_seen, time_trace_id_first_exceeds_threshold, \
                                    elapsed_duration_first_exceeds_threshold, \
                                    time_trace_id_max_exceeds_threshold, \
                                    elapsed_duration_max_exceeds_threshold = unique_trace_ids[trace_id]

                                    if elapsed_duration_first_exceeds_threshold == 0:
                                        # Store the elapsed duration when this trace ID first exceeded the given threshold
                                        unique_trace_ids[trace_id] = (time_trace_id_first_seen, timestamp,
                                                                      elapsed_in_seconds, 0, 0)
                                    else:
                                        if elapsed_in_seconds > elapsed_duration_first_exceeds_threshold:
                                            if elapsed_in_seconds > elapsed_duration_max_exceeds_threshold:
                                                # Store the new max "(elapsed:" duration when this trace ID exceeded
                                                # the given threshold
                                                unique_trace_ids[trace_id] = (time_trace_id_first_seen,
                                                                                  time_trace_id_first_exceeds_threshold,
                                                                                  elapsed_duration_first_exceeds_threshold,
                                                                                  timestamp, elapsed_in_seconds)

    filtered_unique_trace_ids = {}
    for trace_id, trace_values in unique_trace_ids.items():
        time_trace_id_first_seen, time_trace_id_first_exceeds_threshold, elapsed_duration_first_exceeds_threshold, \
        time_trace_id_max_exceeds_threshold, elapsed_duration_max_exceeds_threshold = trace_values
        # Filter only the  trace IDs the exceeded  threshold
        if time_trace_id_first_exceeds_threshold != 0:
            # add the trace ID and associated values to the filtered_trace_ids dictionary
            filtered_unique_trace_ids[trace_id] = (time_trace_id_first_seen, time_trace_id_first_exceeds_threshold, \
                                                   elapsed_duration_first_exceeds_threshold, \
                                                   time_trace_id_max_exceeds_threshold, \
                                                   elapsed_duration_max_exceeds_threshold)

    # assign the filtered_trace_ids dictionary to unique_trace_ids
    unique_trace_ids = filtered_unique_trace_ids

    sorted_unique_trace_ids = [(i, k, v[0], v[1], v[2], v[3], v[4]) for i, (k, v) in
                               enumerate(sorted(unique_trace_ids.items(), key=lambda x: x[1]))]

    return sorted_unique_trace_ids


def display_unique_trace_ids(sorted_unique_trace_ids):
    """
    Prints the unique trace ids sorted by the timestamp in ascending order.

    Parameters:
    sorted_unique_trace_ids (list): A list of tuples, where each tuple contains the following elements:
        1. An integer representing the position of the trace ID in the sorted list.
        2. A string representing the unique trace ID.
        3. A datetime object representing the time the trace ID was first seen.
        4. A datetime object representing the time the trace ID first exceeded the duration threshold.
        5. A float representing the duration of the trace ID's first duration threshold exceedance.
        6. A datetime object representing the time the trace ID exceeded the duration threshold for the maximum time.
        7. A float representing the maximum duration the trace ID exceeded the threshold.

    Returns:
    None
    """
    for pos, trace_id, time_trace_id_first_seen, time_trace_id_first_exceeds_threshold, \
        elapsed_duration_first_exceeds_threshold, \
        time_trace_id_max_exceeds_threshold, \
        elapsed_duration_max_exceeds_threshold in sorted_unique_trace_ids:
        print(f'{pos + 1} - {trace_id} first logged at {time_trace_id_first_seen} , '
              f'first exceeds the duration at {time_trace_id_first_exceeds_threshold} '
              f'took {elapsed_duration_first_exceeds_threshold} sec. '
              f'Max exceeds the duration at {time_trace_id_max_exceeds_threshold} '
              f'took {elapsed_duration_max_exceeds_threshold} sec')


def open_trace_id_files(output_folder, sorted_unique_trace_ids):
    """Opens trace ID files for writing.

    Creates a trace ID file for each unique trace ID found in the log files, based on the `sorted_unique_trace_ids`
    parameter. The file path includes the trace ID, the position of the trace ID in the sorted list, and the
    timestamp of the first occurrence of the trace ID. Each file is opened in "append" mode to avoid overwriting
    existing data.

    Args:
        output_folder (str): The path to the folder where the trace ID files will be created.
        sorted_unique_trace_ids (list): A sorted list of tuples containing unique trace IDs, the position of
            the trace ID in the sorted list, and timestamps of key events.

    Returns:
        dict: A dictionary containing trace IDs as keys and file objects as values.

    """
    trace_id_files = {}
    for pos, trace_id, timestamp, timestamp_first_exceeds_duration, elapsed_in_seconds_gt_duration, \
        timestamp_max_exceeds_duration, max_elapsed_in_seconds_gt_duration in sorted_unique_trace_ids:
        trace_id_file = os.path.join(output_folder, f'{pos + 1}-{trace_id}-{str(timestamp).replace(" ", "-")}.txt')
        os.makedirs(os.path.dirname(trace_id_file), exist_ok=True)
        trace_id_files[trace_id] = open(trace_id_file, "a")
    return trace_id_files


def process_log_file(log_file, sorted_unique_trace_ids, trace_id_files):
    """
    This function reads through a log file, identifies trace IDs that match those in the sorted_unique_trace_ids list,
    and writes those lines to the corresponding trace ID files in the trace_id_files dictionary.  If the trace ID has
    not been logged before, the method also writes a header to the file indicating the log file and directory where the
    trace ID was found.
    If the line does not contain a trace ID that exceeded the duration threshold but a previous line did,
    the method checks if the line contains a timestamp, and if it does, sets previous_matched_trace_id to None.
    If the line does not contain a timestamp, the method assumes it belongs to the same trace ID as the previous line,
    and writes the line to the corresponding file in trace_id_files.

    Args:
        log_file (str): The path to the log file to process.
        sorted_unique_trace_ids (list): A sorted list of tuples, where each tuple contains information about a unique
            trace ID that exceeded a specified threshold during the specified time range.
        trace_id_files (dict): A dictionary where keys are trace IDs and values are file objects, used to write lines
            from the log files that match each trace ID.

    Returns:
        None
    """
    logged_log_file_details_for_trace_ids = []
    with open(log_file) as f:
        previous_matched_trace_id = None
        for line in f:
            if any(item[1] in line for item in sorted_unique_trace_ids):
                pos, matched_trace_id, timestamp, timestamp_first_exceeds_duration, \
                elapsed_in_seconds_gt_duration, timestamp_max_exceeds_duration, \
                max_elapsed_in_seconds_gt_duration = next(
                    item for item in sorted_unique_trace_ids if item[1] in line)
                trace_id_file = trace_id_files[matched_trace_id]
                if matched_trace_id not in logged_log_file_details_for_trace_ids:
                    logged_log_file_details_for_trace_ids.append(matched_trace_id)
                    log_dir, log_file_basename = os.path.split(log_file)
                    trace_id_file.write(
                        f'=========================={os.linesep}{log_dir}{os.linesep}{log_file_basename}{os.linesep}')
                trace_id_file.write(line)
                previous_matched_trace_id = matched_trace_id
            elif previous_matched_trace_id is not None:
                time_match = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+Z', line)
                if time_match:
                    timestamp_str = time_match.group(0)
                    timestamp = parse_time(timestamp_str)
                    if timestamp:
                        # this must be a 'xray-request' or 'router-request' log entry for a different Trace ID.
                        # So we don't have to write it
                        previous_matched_trace_id = None
                else:
                    #if not log_file.startswith("router") and log_file.endswith(".log"):
                    # this must be an error trace belonging to the previous_matched_trace_id
                    trace_id_file = trace_id_files[previous_matched_trace_id]
                    trace_id_file.write(line)


def process_log_files(log_folder, sorted_unique_trace_ids, trace_id_files):
    """
    Searches for log files in the specified folder and its subdirectories that match the given pattern,
    then processes the files to extract the data associated with the selected trace IDs and writes it to
    the corresponding trace ID files.

    Args:
        log_folder (str): The path to the folder containing the log files.
        sorted_unique_trace_ids (list): A list of tuples containing the unique trace IDs to be processed,
            sorted by the timestamp in ascending order. Each tuple contains the following elements:
            - Position of the trace ID in the sorted list.
            - Trace ID (16-digit hex string).
            - Timestamp when the trace ID was first seen.
            - Timestamp when the trace ID first exceeded the duration threshold in the specified time window.
            - Elapsed time (in seconds) for the first occurrence when the trace ID exceeded the threshold.
            - Timestamp when the trace ID last exceeded the duration threshold in the specified time window.
            - Elapsed time (in seconds) for the last occurrence when the trace ID exceeded the threshold.
        trace_id_files (dict): A dictionary containing the file handles for each trace ID file.

    Returns:
        None
    """
    file_order = [
        'artifactory-request',
        'artifactory-service',
        'artifactory-access',
        'artifactory-binarystore',
        'artifactory-request-out',
        'router-request'
    ]

    for file_prefix in file_order:
        # search the specified folder and its subdirectories recursively and return
        # a list of file paths that match the given pattern
        files = glob.glob(os.path.join(log_folder, '**', f'{file_prefix}*.log'), recursive=True)
        # sort the list of files based on their modification time in ascending order (i.e., oldest to most recent)
        files.sort(key=os.path.getmtime)
        for log_file in files:
            process_log_file(log_file, sorted_unique_trace_ids, trace_id_files)


def close_trace_id_files(open_trace_id_files):
    """Close all open trace ID files.

    Args:
        open_trace_id_files (dict): A dictionary containing open trace ID files as values.

    Returns:
        None
    """
    for f in open_trace_id_files.values():
        f.close()


def main():
    args = parse_args()
    # start_time = datetime.fromisoformat(args.start_time)
    # end_time = datetime.fromisoformat(args.end_time)
    start_time = parser.isoparse(args.start_time)
    end_time = parser.isoparse(args.end_time)
    if args.trace_ids:
        selected_trace_ids = args.trace_ids.split(",")
        sorted_unique_trace_ids = find_unique_trace_ids(args.log_folder, start_time, end_time, args.duration, selected_trace_ids)
    else:
        sorted_unique_trace_ids = find_unique_trace_ids(args.log_folder, start_time, end_time, args.duration)

    # prompt user for option
    option = input("Enter an option (1 for display trace IDs, 2 for process trace IDs): ")

    if option == "1":
        # display all trace IDs
        display_unique_trace_ids(sorted_unique_trace_ids)
    elif option == "2":
        # prompt user for trace IDs to process
        print("Here are the available trace IDs:")
        display_unique_trace_ids(sorted_unique_trace_ids)
        selection = input("Enter comma-separated list of trace IDs to process (or leave blank for all): ")

        # convert input to list of trace IDs
        selected_trace_ids = selection.split(",") if selection else [t[1] for t in sorted_unique_trace_ids]

        # filter trace IDs based on selection
        selected_trace_ids = [t for t in sorted_unique_trace_ids if t[1] in selected_trace_ids]

        trace_id_files = open_trace_id_files(args.output_folder, selected_trace_ids)
        process_log_files(args.log_folder, selected_trace_ids, trace_id_files)
        close_trace_id_files(trace_id_files)
    else:
        print("Invalid option.")


if __name__ == '__main__':
    main()
