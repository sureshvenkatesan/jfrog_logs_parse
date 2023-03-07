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
This does something similar to Powershell:
Get-Childitem -Recurse | where { -not $_.PSIsContainer } | group Extension -NoElement | sort count -desc
"""
import os
import argparse

parser = argparse.ArgumentParser(description='Count the number of files with each extension in a folder')
parser.add_argument('folder_path', metavar='FOLDER_PATH', type=str,
                    help='the path to the folder to search')

args = parser.parse_args()

folder_path = args.folder_path

file_extensions = {}

# Recursively traverse the folder and its subfolders
for root, dirs, files in os.walk(folder_path):
    for file in files:
        # Get the file extension
        file_extension = os.path.splitext(file)[1][1:]
        # Increment the count for the file extension
        file_extensions[file_extension] = file_extensions.get(file_extension, 0) + 1

# Print the results
for extension, count in file_extensions.items():
    print(f'{extension}: {count}')
