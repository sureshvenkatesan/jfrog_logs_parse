# python extract_support_bundle_zip.py path/to/nested.zip path/to/output
# find "./202302281747-jfxr_jfxr_jfxr@01fn44xyc9bjn01ebfnj6thp9t" -type f \( -name '*.zip' -o -name '*.gz' \) -print | wc -l
#  find the total number of files within a folder recursively
# find ./202302281747-jfxr_jfxr_jfxr@01fn44xyc9bjn01ebfnj6thp9t -type f | wc -l

import os
import zipfile
import gzip
import argparse

def extract_zip_file(zip_file_path, output_dir):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
        # Extract all the files to the output directory
        zip_file.extractall(output_dir)

        # Iterate over all the extracted files
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)

                # If the file is a .zip file, extract it recursively
                if file.endswith('.zip'):
                    extract_zip_file(file_path, os.path.join(root, os.path.splitext(file)[0]))
                    # Delete the original .zip file
                    os.remove(file_path)
                # If the file is a .gz file, extract it
                elif file.endswith('.gz'):
                    with gzip.open(file_path, 'rb') as gz_file:
                        # Read the contents of the .gz file
                        file_contents = gz_file.read()

                    # Write the extracted file to disk
                    extracted_file_path = os.path.splitext(file_path)[0]  # Remove the .gz extension
                    with open(extracted_file_path, 'wb') as extracted_file:
                        extracted_file.write(file_contents)

                    # Delete the original .gz file
                    os.remove(file_path)

if __name__ == '__main__':
    # Create an argument parser
    parser = argparse.ArgumentParser(description='Extract a nested zip file that may contain .gz files')
    parser.add_argument('zip_file', type=str, help='path to the nested zip file')
    parser.add_argument('output_dir', type=str, help='path to the output directory')

    # Parse the command line arguments
    args = parser.parse_args()

    # Extract the zip file
    extract_zip_file(args.zip_file, args.output_dir)

