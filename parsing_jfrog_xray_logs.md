Based on the  Xray "Request Log"  ( xray-request.log) format 
below command uses a regular expression to match lines with HTTP 500 response code:
```commandline
find . -name '*-request.log' -type f -exec grep -EH '^([^|]*\|){6}500\|([^|]*\|){3}[^|]*$' {} \;
```
Example:
```commandline
2023-03-27T16:56:15.837Z|3ef02583e1677d91|127.0.0.1, 127.0.0.1, 10.10.186.73|_svc-artif-devops|GET|/api/v1/metrics|500|-1|0|394.346000|python-requests/2.28.1
```

To print the file name once and all matching lines for each file matching the pattern *-request.log which do not have a "Return Status" in
the 20x range (i.e., 200-299) 
and have a "Request URL" that contains the substring "scan", you can use the following command:

Command to find files with names matching the pattern *-request*.log, and for each file, it processes the lines that
contain the string "scan" in the 6th field and have an HTTP status code of less than 200 or greater than or equal to 300.
i.e all the "scan" requests which does not have a 20x "Return Status" .
It prints the file name and the matching lines with their line numbers.
```commandline

find . -name '*-request*.log' -type f -exec \
awk -F'|' '($7 < 200 || $7 >= 300) && index($6, "scan") > 0 \
 { if (FILENAME != prevfile) { print "\n" FILENAME ":\n"; prevfile = FILENAME } print NR ":" $0 }' {} \;
```
or if you want the full file path usimg realpath run:
```
find . -name '*-request*.log' -type f -execdir \
sh -c 'fullpath=$(realpath "{}"); awk -F"|" "(\$7 < 200 || \$7 >= 300) && index(\$6, \"scan\") > 0 \
{ if (FILENAME != prevfile) { printf \"\n%s:\n\", \"${fullpath}\"; prevfile = FILENAME } printf \"%d:%s\n\", NR, \$0 }" "{}"' \;

```
If you do not want the line numbers use:
```commandline

find . -name '*-request*.log' -type f -exec \
awk -F'|' '($7 < 200 || $7 >= 300) && index($6, "scan") > 0 \
 { if (FILENAME != prevfile) { print "\n" FILENAME ":\n"; prevfile = FILENAME } print  $0 }' {} \;

or

find . -name '*-request*.log' -type f -execdir \
sh -c 'fullpath=$(realpath "{}"); awk -F"|" "(\$7 < 200 || \$7 >= 300) && index(\$6, \"scan\") > 0 \
{ if (FILENAME != prevfile) { printf \"\n%s:\n\", \"${fullpath}\"; prevfile = FILENAME } printf \"%s\n\",  \$0 }" "{}"' \;

```

---

How to find the `scanBuild` details in xray-server-service.log ?
Unzip the xray-server-service.log from the support bundle. All log entries are in UTC.

```
grep -r "scanBuild" | grep  2023-02-27T23
```

You will find the trace ID for the scanBuild i.e "POST requests for /api/v1/scanBuild" log a log entry like:

`2023-02-27T23:43:46.565042446Z [jfxr ] [INFO ] [4246ffb450dde750] [http_handler_ext:106          ] [main                ] Handler about to call scanBuild for default_cd-test-image_1`

Next grep recursively for a pattern and print the filename only once along with the matching lines in that file:
```
grep -rl "cd-test-image_1" /path/to/directory | while read filename; do echo "$filename"; grep -h "cd-test-image_1" "$filename"; echo "====================================="; done

For example: 

grep -rl "61d9270fe5a5e349" . | while read filename; do echo "$filename"; grep -h "61d9270fe5a5e349" "$filename"; echo "====================================="; done  >  trace_61d9270fe5a5e349.txt
```
