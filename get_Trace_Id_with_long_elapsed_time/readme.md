# Python Log Parser

This script can be used to parse log files and find unique trace ids that took longer than a certain duration within a specific time window. The trace ids are then saved into individual files in a specified output folder.

## Requirements
- Python 3.x
- argparse

## Usage
```commandline
python get_Trace_Id_with_long_elapsed_time_sec.py log_folder output_folder start_time end_time duration
```


### Arguments
- `log_folder`: Path to the folder containing log files
- `output_folder`: Path to the folder where the trace_id files will be created
- `start_time`: Start time of the time window in ISO 8601 format (e.g. '2023-02-28T00:00:00')
- `end_time`: End time of the time window in ISO 8601 format (e.g. '2023-02-28T23:59:59')
- `duration`: Duration threshold in seconds

## Example Usage
```commandline
python get_Trace_Id_with_long_elapsed_time_sec.py /path/to/log/folder /path/to/output/folder 2023-03-01T00:00:00 2023-03-01T23:59:59 30.0
```


This will search the log files in `/path/to/log/folder` for trace ids that took longer than 30 seconds between `2023-03-01T00:00:00` and `2023-03-01T23:59:59` and save the trace ids to individual files in `/path/to/output/folder`.

