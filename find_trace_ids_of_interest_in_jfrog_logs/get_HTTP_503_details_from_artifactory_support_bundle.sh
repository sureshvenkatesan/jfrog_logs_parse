#!/bin/bash
# usage: bash find_trace_ids_of_interest_in_jfrog_logs/get_HTTP_503_details_from_artifactory_support_bundle.sh \
# /Users/sureshv/Documents/From_Customer/xyz/245256_500_err/Artifactory500s.zip \
# /tmp/Artifactory500s \
# /tmp/http_503

# Ask for input file paths
#read -p "Enter path to Artifactory Support bundle zip: " artifactory_sup_bundle_zip
#read -p "Enter path to unzip the Support bundle: " sup_bundle_unzip_dir
#read -p "Enter path to output traceID files for HTTP 503 : " traceid_output_dir

# Parse command-line arguments
artifactory_sup_bundle_zip="$1"
sup_bundle_unzip_dir="$2"
traceid_output_dir="$3"

# Delete and recreate traceid_output_dir
rm -rf "$traceid_output_dir"
mkdir -p "$traceid_output_dir"

# Extract support bundle zip file if sup_bundle_unzip_dir directory is empty or does not exist
if [ ! -d "$sup_bundle_unzip_dir" ] || [ -z "$(ls -A "$sup_bundle_unzip_dir")" ]; then
    cd /Users/sureshv/myCode/github-sv/jfrog_logs_parse
    python unzip_support_bundle_recursively/extract_support_bundle_zip.py "$artifactory_sup_bundle_zip" "$sup_bundle_unzip_dir"
fi

# Find first and last timestamps overall for all artifactory-request*.log files in Artifactory500s directory
cd "$sup_bundle_unzip_dir"
timestamps=()
for file in $(find . -name 'artifactory-request*.log' -type f); do
    timestamps+=($(grep -o '^[^|]*' $file))
done
echo "First timestamp overall: $(echo ${timestamps[*]} | tr ' ' '\n' | sort | head -n1)"
echo "Last timestamp overall: $(echo ${timestamps[*]} | tr ' ' '\n' | sort | tail -n1)"


# Extract log entries for HTTP 503 errors for "build" requests and get Trace IDs

for file in $(find . -name '*.log' -type f); do
    if grep -q -E ': 503 :' "$file"; then
        echo "$(realpath $file)"
        grep -E ': 503 :' "$file"
    fi
done >"$traceid_output_dir/Service_Unavailable_503.txt"

traceids_csv=$(awk -F '[][]' '{if ($6 != "") print $6}' "$traceid_output_dir/Service_Unavailable_503.txt" | sort -u | tr '\n' ',')
echo "Trace IDs: $traceids_csv"

find . -name '*-request*.log' -type f -execdir \
sh -c 'fullpath=$(realpath "{}"); awk -F"|" "(\$7 > 499) && (index(\$6, \"build\") > 0)  \
{ if (FILENAME != prevfile) { printf \"\n%s:\n\", \"${fullpath}\"; prevfile = FILENAME } printf \"%s\n\", \$0 }" "{}"' \; > "$traceid_output_dir/http_50x_errors.txt"

traceids_csv+=$(awk -F'|' '{if ($2 != "") print $2}' "$traceid_output_dir/http_50x_errors.txt" | tr '\n' ',' | sed 's/,$//')
echo "Trace IDs: $traceids_csv"

# Get log entries for each Trace ID with long elapsed time
cd /Users/sureshv/myCode/github-sv/jfrog_logs_parse
python get_Trace_Id_with_long_elapsed_time/get_Trace_Id_with_long_elapsed_time_sec_in_RT.py \
"$sup_bundle_unzip_dir" \
"$traceid_output_dir" \
"$(echo ${timestamps[*]} | tr ' ' '\n' | sort | head -n1 | cut -c1-11)00:00:00Z" \
"$(echo ${timestamps[*]} | tr ' ' '\n' | sort | tail -n1 | cut -c1-11)23:59:59Z" \
0 --trace_ids "$traceids_csv"
