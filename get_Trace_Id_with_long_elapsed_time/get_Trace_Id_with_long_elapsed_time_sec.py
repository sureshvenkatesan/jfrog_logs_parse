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

python get_Trace_Id_with_long_elapsed_time_sec.py ./iss1_impact_anal_missing/chrisDaw_test/202302281747-jfxr_jfxr_jfxr@01fn44xyc9bjn01ebfnj6thp9t ./iss1_impact_anal_missing/chrisDaw_test/tmp3 2023-02-27T23:30:00Z 2023-02-28T00:30:59Z 10
"""
import argparse
import os
import re
from datetime import datetime, timedelta
from dateutil import parser


def parse_args():
    parser = argparse.ArgumentParser(description="Parse log files for long elapsed times in  a specific time window")
    parser.add_argument("log_folder", type=str, help="path to the folder containing log files")
    parser.add_argument("output_folder", type=str, help="path to the folder where the trace_id files will be created")
    parser.add_argument("start_time", type=str, help="start time of the time window in ISO 8601 format "
                                                     "(e.g. '2023-02-28T00:00:00')")
    parser.add_argument("end_time", type=str, help="end time of the time window in ISO 8601 format "
                                                   "(e.g. '2023-02-28T23:59:59')")
    parser.add_argument('duration', type=float, help='Duration threshold in seconds')
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


def find_unique_trace_ids(log_folder, start_time, end_time, threshold_in_sec):
    """
    Searches for unique trace IDs in the log files within the specified time window.

    Args:
        log_folder (str): The path to the folder containing the log files.
        start_time (str): The start time of the time window in ISO 8601 format.
        end_time (str): The end time of the time window in ISO 8601 format.
        threshold_in_sec (float): The duration threshold in seconds.

    Returns:
        list: A list of tuples containing the unique trace IDs, sorted by the timestamp in ascending order.
              Each tuple contains the following elements:
              - Position of the trace ID in the sorted list.
              - Trace ID (16-digit hex string).
              - Timestamp when the trace ID was first seen.
              - Timestamp when the trace ID first exceeded the duration threshold in the specified time window.
              - Elapsed time (in seconds) for the first occurrence when the trace ID exceeded the threshold.
              - Timestamp when the trace ID last exceeded the duration threshold in the specified time window.
              - Elapsed time (in seconds) for the last occurrence when the trace ID exceeded the threshold.
    """
    unique_trace_ids = {}

    for root, dirs, files in os.walk(log_folder):
        for file in files:
            if file.startswith("xray") and file.endswith(".log"):
                log_file = os.path.join(root, file)
                with open(log_file) as f:
                    for line in f:
                        time_match = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+Z', line)
                        if time_match:
                            timestamp_str = time_match.group(0)
                            timestamp = parse_time(timestamp_str)
                            if timestamp and start_time <= timestamp <= end_time:
                                trace_id_match_found = re.search(r"\[([a-f\d]{16})\]", line)
                                if trace_id_match_found:
                                    trace_id = re.search(r"\[([a-f\d]{16})\]", line).group(1)
                                    if trace_id not in unique_trace_ids:
                                        # tracking the traceid for the first time
                                        unique_trace_ids[trace_id] = (timestamp, 0, 0, 0, 0)

                                    elapsed_in_seconds = find_elapsed_time(line)
                                    if elapsed_in_seconds > threshold_in_sec:
                                        time_trace_id_first_seen, time_trace_id_first_exceeds_threshold, \
                                        elapsed_duration_first_exceeds_threshold, \
                                        time_trace_id_max_exceeds_threshold, \
                                        elapsed_duration_max_exceeds_threshold = unique_trace_ids[trace_id]

                                        if elapsed_duration_first_exceeds_threshold == 0:
                                            # we are storing the elapsed duration when this trace ID first exceeded
                                            # given threshold_in_sec within the specified time range
                                            unique_trace_ids[trace_id] = (time_trace_id_first_seen, timestamp,
                                                                          elapsed_in_seconds, 0, 0)
                                        else:
                                            if elapsed_in_seconds > elapsed_duration_first_exceeds_threshold:
                                                if elapsed_in_seconds > elapsed_duration_max_exceeds_threshold:
                                                    # we found another line for this trace_id with a new max "(elapsed:"
                                                    # Keep track of this time .
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
    logged_log_file_details_in_trace_ids = []
    with open(log_file) as f:
        previous_matched_trace_id = None
        for line in f:
            if any(item[1] in line for item in sorted_unique_trace_ids):
                pos, matched_trace_id, timestamp, timestamp_first_exceeds_duration, \
                elapsed_in_seconds_gt_duration, timestamp_max_exceeds_duration, \
                max_elapsed_in_seconds_gt_duration = next(
                    item for item in sorted_unique_trace_ids if item[1] in line)
                trace_id_file = trace_id_files[matched_trace_id]
                if matched_trace_id not in logged_log_file_details_in_trace_ids:
                    logged_log_file_details_in_trace_ids.append(matched_trace_id)
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
                        # this must be a new request log entry from a request log file. So we don't have to write it
                        previous_matched_trace_id = None
                    else:
                        if not log_file.startswith("router") and log_file.endswith(".log"):
                            # this line is not from the router log file
                            trace_id_file = trace_id_files[previous_matched_trace_id]
                            trace_id_file.write(line)


def process_log_files(log_folder, sorted_unique_trace_ids, trace_id_files):
    """
    Processes all log files found in the specified folder and its subfolders, searching for traces that
    exceed the threshold duration and writes each line containing the trace to a separate file for further
    analysis.

    Args:
        log_folder (str): The path to the folder containing log files.
        sorted_unique_trace_ids (list): A list of unique trace IDs sorted by timestamp in ascending order.
        trace_id_files (dict): A dictionary where the keys are trace IDs and the values are file objects.

    Returns:
        None
    """
    for root, dirs, files in os.walk(log_folder):
        for file in files:
            if file.startswith("xray") and file.endswith(".log"):
                log_file = os.path.join(root, file)
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
    sorted_unique_trace_ids = find_unique_trace_ids(args.log_folder, start_time, end_time, args.duration)
    display_unique_trace_ids(sorted_unique_trace_ids)
    trace_id_files = open_trace_id_files(args.output_folder, sorted_unique_trace_ids)
    process_log_files(args.log_folder, sorted_unique_trace_ids, trace_id_files)
    close_trace_id_files(trace_id_files)


if __name__ == '__main__':
    main()
