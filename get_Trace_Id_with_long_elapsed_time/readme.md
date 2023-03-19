# Python Log Parser

This program analyzes xray log files and finds trace IDs with elapsed times exceeding a specified threshold within a
specified time window. 

The program prompts the user to choose an option: either display all trace IDs or process specific trace IDs.
For processing specific trace IDs, the user can select the trace IDs to process or leave the prompt blank to process 
all trace IDs. The trace ids are then saved into individual files in a specified output folder.

## Requirements
- Python 3.x
- dateutil ( It can be installed using pip with the command "pip install python-dateutil".)

## Usage
```commandline
python get_Trace_Id_with_long_elapsed_time_sec.py <log_folder> <output_folder> <start_time> <end_time> <duration> [--trace_ids]
```


### Arguments
- `log_folder`: Path to the folder containing log files
- `output_folder`: Path to the folder where the trace_id files will be created
- `start_time`: Start time of the time window in ISO 8601 format (e.g. '2023-02-28T00:00:00Z') . Z denotes UTC.
- `end_time`: End time of the time window in ISO 8601 format (e.g. '2023-02-28T23:59:59Z'). Z denotes UTC.
- `duration`: Duration threshold in seconds
- `--trace_ids`: (optional) is a comma-separated list of trace IDs to process.

## Example Usage
```commandline
python get_Trace_Id_with_long_elapsed_time_sec.py /path/to/log/folder /path/to/output/folder 2023-03-01T00:00:00Z 2023-03-01T23:59:59Z 30
```

To process specific trace IDs, add the --trace_ids option followed by a comma-separated list of trace IDs to process.
For example, to process trace IDs 5700c3a699405ab3 and 175b05a436088101 , use the following command:
```commandline
python get_Trace_Id_with_long_elapsed_time_sec.py /path/to/log/folder /path/to/output/folder 2023-03-01T00:00:00Z 2023-03-01T23:59:59Z 30 --trace_ids 5700c3a699405ab3,175b05a436088101
```

This will search the log files in `/path/to/log/folder` for trace ids that took longer than 30 seconds 
between `2023-03-01T00:00:00Z` and `2023-03-01T23:59:59Z` 
The program will prompt the user to choose an option: either display all trace IDs or process specific trace IDs.
If the user selects to process specific trace IDs, the program will prompt the user to enter a comma-separated list 
of trace IDs to process. The user can leave the prompt blank to process all trace IDs and save the trace ids to 
individual files in the output_folder `/path/to/output/folder`. The output_folder is created if it does not exist