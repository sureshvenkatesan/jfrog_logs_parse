First unzip the support bundle recursively using;

```commandline
python unzip_support_bundle_recursively/extract_support_bundle_zip.py /path/to/support_bundle.zip /path/to/unzip/folder
Example:

python unzip_support_bundle_recursively/extract_support_bundle_zip.py \
/Users/sureshv/Documents/From_Customer/xyz/240361_500_err/20230328115.zip /Users/sureshv/Documents/From_Customer/xyz/240361_500_err/xray_20230328115
```
---
In each of these artifactory-request.log files get the Timestamp of the first and last line:
```commandline
for file in $(find . -name '*-request.log' -type f); do
    echo "File: $file"
    echo "First timestamp: $(head -n1 $file | grep -o '^[^|]*')"
    echo "Last timestamp: $(tail -n1 $file | grep -o '^[^|]*')"
done
```
---
To find what files are in the support bundle,
find unique file names containing min of 1 hyphen in the filename and ending in .log recursively in the /path/to/unzip/folder
```commandline
cd /path/to/unzip/folder
find . -type f -name '*-*.log' -exec basename {} \; | grep -E '\-' | sort -u
```


Artifactory request log (artifactory-request.log) format:
https://www.jfrog.com/confluence/display/JFROG/Logging#Logging-RequestLog.1

`Timestamp | Trace ID | Remote Address | Username | Request method | Request URL | Return Status | Request Content Length | Response Content Length | Request Duration | Request User Agent`

Example:
```commandline
2023-03-28T16:45:46.402Z|2045257c3162b23d|10.10.64.120|anonymous|GET|/deploy-configs-for-dcauto-test/deployconfigs/tasks/generateoneconfig.xml|500|-1|300|2|null
```
---
Based on the  Artifactory "Request Log" format 
below command uses a regular expression to match lines with HTTP 500 response code:
```commandline
find . -name '*-request.log' -type f -exec grep -EH '^([^|]*\|){6}500\|([^|]*\|){3}[^|]*$' {} \;
```
^ matches the beginning of a line
([^|]*\|){6} matches any non-pipe characters followed by a pipe, repeated 6 times (to match the timestamp, trace ID, remote address, username, request method, and request URL)
500\| matches "500" followed by a pipe
([^|]*\|){3} matches any non-pipe characters followed by a pipe, repeated 3 times (to match the return status, request content length, and response content length)
[^|]*$ matches any non-pipe characters until the end of the line (to match the request duration and user agent)

---
Command to get all line and the filenames containing 'TimeoutException'
```commandline
find . -name '*.log' -type f -exec grep -EH 'TimeoutException' {} \;
```
---

Command to find artifactory *-request*.log, and for each file, it processes the lines with an HTTP status code
that is outside the 200-299 range, excluding 404 and 302, and containing the string "2023-03-28T16" in the 1st field. 
It prints the file name and the matching lines with their line numbers.
```commandline
find . -name '*-request*.log' -type f -exec \
awk -F'|' '($7 < 200 || $7 >= 300 ) && ($7 != 404 ) && ($7 != 302) && index($1, "2023-03-28T16") > 0 \
{ if (FILENAME != prevfile) { print "\n" FILENAME ":"; prevfile = FILENAME } print NR ":" $0 }' {} \;

```
---

Command to find files with names matching the pattern *-request*.log, and for each file, it processes the lines that
from "2023-03-28T" for "Request URL" containing string "build" and response with HTTP 503 errors
It prints the file name and the matching lines with their line numbers.
```commandline
find . -name '*-request*.log' -type f -exec \
awk -F'|' '($7 > 499) && (index($1, "2023-03-28T") > 0) && (index($6, "build") > 0) \
{ if (FILENAME != prevfile) { print "\n" FILENAME ":"; prevfile = FILENAME } print NR ":" $0 }' {} \; > http_500_on_2023-03-28_req_build.txt
```
or if you want the full file path usimg realpath run:
```commandline
find . -name '*-request*.log' -type f -execdir \
sh -c 'fullpath=$(realpath "{}"); awk -F"|" "(\$7 > 499) && (index(\$1, \"2023-03-28T\") > 0) && (index(\$6, \"build\") > 0) \
{ if (FILENAME != prevfile) { printf \"\n%s:\n\", \"${fullpath}\"; prevfile = FILENAME } printf \"%d:%s\n\", NR, \$0 }" "{}"' \; > http_500_on_2023-03-28_req_build.txt

```
If you do not want the line numbers use:
```commandline
find . -name '*-request*.log' -type f -exec \
awk -F'|' '($7 > 499) && (index($1, "2023-03-28T") > 0) && (index($6, "build") > 0) \
{ if (FILENAME != prevfile) { print "\n" FILENAME ":"; prevfile = FILENAME } print  $0 }' {} \; > http_500_on_2023-03-28_req_build.txt

or

find . -name '*-request*.log' -type f -execdir \
sh -c 'fullpath=$(realpath "{}"); awk -F"|" "(\$7 > 499) && (index(\$1, \"2023-03-28T\") > 0) && (index(\$6, \"build\") > 0) \
{ if (FILENAME != prevfile) { printf \"\n%s:\n\", \"${fullpath}\"; prevfile = FILENAME } printf \"%s\n\", \$0 }" "{}"' \; > http_500_on_2023-03-28_req_build.txt

```
---
Now  get all the "Trace ID" in comma separated format  for the requests with HTTP 503 errors:
```commandline
find . -name '*-request*.log' -type f -exec \
awk -F'|' '($7 > 499) && (index($1, "2023-03-28T") > 0) && (index($6, "build") > 0) \
{ if (FILENAME != prevfile) { print "\n" FILENAME ":"; prevfile = FILENAME } print NR ":" $0 }' {} \; \
| awk -F'|' '{if ($2 != "") print $2}' | tr '\n' ',' | sed 's/,$//'

or

awk -F'|' '{if ($2 != "") print $2}' http_500_on_2023-03-28_req_build.txt | tr '\n' ',' | sed 's/,$//'

```
Example output:
3c8f9b72dad6208f,402a4cb23857cf0,42807c5da98480f2

---
You can get  log entries from all files ( not just the '*-request*.log' ) with HTTP 503 errors like the following:
2023-03-27T07:11:27.185Z [jfrt ] [ERROR] [1ad815c6768b7ea5] [ShardingBinaryProviderImpl:402] [p-nio-8081-exec-3241] - Failed to stream binary to sub provider: java.io.IOException: Failed to send stream to remote endpoint of artifactory-0, got response: 503 : Service Unavailable
2023-03-27T04:57:28.729Z [jfrt ] [WARN ] [929088021c21f4ed] [.r.ArtifactoryResponseBase:144] [p-nio-8081-exec-3448] - Sending HTTP error code 503: 503 : Failed to read 32768 bytes stream from inputStream to buffer
2023-03-26T05:39:11.147Z [jfrt ] [WARN ] [a4ff86bcc62e2b46] [.r.ArtifactoryResponseBase:144] [p-nio-8081-exec-3057] - Sending HTTP error code 503: 503 : Failed to read 32768 bytes stream from inputStream to buffer

using:
```commandline
cd /Users/sureshv/Documents/From_Customer/xyz/245256_500_err/Artifactory500s
for file in $(find . -name '*.log' -type f); do
    if grep -q -E ': 503 :' "$file"; then
        echo "$(realpath $file)"
        grep -E ': 503 :' "$file"
    fi
done > /Users/sureshv/Documents/From_Customer/xyz/245256_500_err/Service_Unavailable_503.txt
```

Then extract the unique comma seperated tarceids ( like 1ad815c6768b7ea5,929088021c21f4ed,a4ff86bcc62e2b46 in example
above) using:
'\[[a-fA-F0-9]+\s*\]' - the regular expression pattern to search for traceid . 
It consists of an opening square bracket [, followed by one or more (+) lowercase hexadecimal characters
(ranging from a to f and 0 to 9), and then a closing square bracket ]

```commandline
grep -oE '\[[a-fA-F0-9]+\s*\]' /Users/sureshv/Documents/From_Customer/xyz/245256_500_err/Service_Unavailable_503.txt \
| awk -F '[][]' '{print $2}' | sort -u | tr '\n' ','

or
awk -F '[][]' '{if ($6 != "") print $6}' /Users/sureshv/Documents/From_Customer/xyz/245256_500_err/Service_Unavailable_503.txt | sort -u | tr '\n' ','


```

Get all log entries for each of these  traceids in separate files :
```commandline
python get_Trace_Id_with_long_elapsed_time/get_Trace_Id_with_long_elapsed_time_sec_in_RT.py \
/Users/sureshv/Documents/From_Customer/xyz/245256_500_err/Artifactory500s \
/Users/sureshv/Documents/From_Customer/xyz/245256_500_err/build_500_err \
2023-03-28T00:00:00Z 2023-03-29T23:59:59Z 0 --trace_ids  "3c8f9b72dad6208f,402a4cb23857cf0,42807c5da98480f2"

```
