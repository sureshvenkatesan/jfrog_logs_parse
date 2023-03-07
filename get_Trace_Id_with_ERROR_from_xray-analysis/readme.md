# Log Parser Script

This Python script parses log files for errors within a specific time window and creates trace ID files for the errors found. The script uses `argparse` to parse command-line arguments and `os`, `re`, and `datetime` modules to perform the parsing and file operations.

## Usage

To use this script, provide four command-line arguments:

1. `log_folder`: the path to the folder containing the log files to be parsed.
2. `output_folder`: the path to the folder where the trace ID files will be created.
3. `start_time`: the start time of the time window in ISO 8601 format (e.g., '2023-02-28T00:00:00').
4. `end_time`: the end time of the time window in ISO 8601 format (e.g., '2023-02-28T23:59:59').

Once the command-line arguments are provided, the script will find all unique trace IDs with errors within the specified time window and create a trace ID file for each unique trace ID found in the `output_folder` with the format `"{position}-{trace_id}-{timestamp}.txt"`. The script will then write the log lines for each unique trace ID to its corresponding trace ID file. The script will also display the sorted list of unique trace IDs and their timestamps to the console.

## Functions

The script defines several functions:

1. `parse_args()`: parses the command-line arguments using `argparse` and returns the parsed arguments.
2. `parse_time(timestamp_str)`: takes a timestamp string and returns a datetime object. If the string is not a valid timestamp, it returns `None`.
3. `find_unique_trace_ids(log_folder, start_time, end_time)`: finds all unique trace IDs with errors within the specified time window in the log files in the specified folder and returns a sorted list of tuples containing the trace ID, its corresponding timestamp, and its position in the sorted list.
4. `display_unique_trace_ids(sorted_unique_trace_ids)`: prints the sorted list of unique trace IDs and their timestamps.
5. `open_trace_id_files(output_folder, sorted_unique_trace_ids)`: creates a dictionary of trace ID file objects for each unique trace ID found in `sorted_unique_trace_ids`.
6. `process_log_files(log_folder, sorted_unique_trace_ids, trace_id_files)`: processes the log files in the specified folder and writes the log lines for each unique trace ID to its corresponding trace ID file.
7. `close_trace_id_files(open_trace_id_files)`: closes all the trace ID files in the dictionary.

## Example

To run the script, use the following command:

```commandline
python get_Trace_Id_with_ERROR_from_jfxana.py log_folder output_folder start_time end_time

```
For example:
```commandline
python get_Trace_Id_with_ERROR_from_jfxana.py /path/to/log/folder /path/to/output/folder 2023-02-28T00:00:00 2023-02-28T23:59:59

```

This will parse the log files in `/path/to/log/folder` for errors between `2023-02-28T00:00:00` and `2023-02-28T23:59:59`, create trace ID files for each unique trace ID found in `/path/to/output/folder`, and write the log lines for each unique trace ID to its corresponding trace ID file.
