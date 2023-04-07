[get_HTTP_503_details_from_artifactory_support_bundle.sh](./get_HTTP_503_details_from_artifactory_support_bundle.sh)

This bash script extracts the relevant log entries from the Artifactory support bundle
and outputs the trace IDs that correspond to HTTP 503 errors for "build" requests. 
It is intended to be used for troubleshooting issues with Artifactory.

# Usage

`bash find_trace_ids_of_interest_in_jfrog_logs/get_HTTP_503_details_from_artifactory_support_bundle.sh <path-to-artifactory-support-bundle-zip> <path-to-unzip-support-bundle> <path-to-output-traceid-files-for-HTTP-503>`

## Arguments

- `path-to-artifactory-support-bundle-zip`: path to the Artifactory support bundle zip file.
- `path-to-unzip-support-bundle`: path to the directory where the Artifactory support bundle will be unzipped.
- `path-to-output-traceid-files-for-HTTP-503`: path to the directory where the traceID files for HTTP 503 errors will be output.

## Example

```bash
bash find_trace_ids_of_interest_in_jfrog_logs/get_HTTP_503_details_from_artifactory_support_bundle.sh ./From_Customer/xyz/245256_500_err/Artifactory500s.zip /tmp/Artifactory500s /tmp/http_503
```

## Dependencies
The script requires the following dependencies to be installed:

- Python 3.x

## Script Flow
1. The script first deletes and recreates the traceid_output_dir to ensure that any existing files in that directory do not interfere with the script execution.

2. If the sup_bundle_unzip_dir directory is empty or does not exist, the script extracts the Artifactory support bundle zip file to that directory.

3. The script finds the first and last timestamps overall for all artifactory-request*.log files in the sup_bundle_unzip_dir directory.

4. The script extracts log entries for HTTP 503 errors for "build" requests and writes them to a file called Service_Unavailable_503.txt in the traceid_output_dir directory.

5. The script extracts the trace IDs from the log entries in Service_Unavailable_503.txt and appends them to the traceids_csv variable.

6. The script extracts log entries for HTTP 503 errors for "build" requests from all *-request*.log files and writes them to a file called http_50x_errors.txt in the traceid_output_dir directory.

7. The script extracts the trace IDs from the log entries in http_50x_errors.txt and appends them to the traceids_csv variable.

8. The script uses the [get_Trace_Id_with_long_elapsed_time_sec_in_RT.py](../get_Trace_Id_with_long_elapsed_time/get_Trace_Id_with_long_elapsed_time_sec_in_RT.py) Python script to extract log entries for each trace ID with long elapsed time and writes them to a file in the traceid_output_dir directory.

## Output
The script outputs the following:

- The first and last timestamps overall for all artifactory-request*.log files in the sup_bundle_unzip_dir directory.
- The trace IDs extracted from the log entries in Service_Unavailable_503.txt.
- The trace IDs extracted from the log entries in http_50x_errors.txt.
- a separate traceid file for each traceid in the `path-to-output-traceid-files-for-HTTP-503` folder