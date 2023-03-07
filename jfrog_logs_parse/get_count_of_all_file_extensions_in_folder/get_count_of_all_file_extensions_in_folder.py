import os
import argparse
# similar to Powershell:
# Get-Childitem -Recurse | where { -not $_.PSIsContainer } | group Extension -NoElement | sort count -desc
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
