# Extract Nested Zip Files

This script extracts a nested zip file that may contain .gz files. It extracts all the files from the nested zip file to the specified output directory. If any of the extracted files are themselves zip files, it extracts them recursively.

## Requirements
- Python 3.x
- `argparse` module

## Usage
```commandline
python extract_nested_zip.py zip_file output_dir
```

## Arguments
- `zip_file` (required): Path to the nested zip file.
- `output_dir` (required): Path to the output directory.

## Example
```commandline
python extract_support_bundle_zip.py nested_zip_file.zip extracted_files/
```


## Code Explanation
- First, we import necessary modules: `os`, `zipfile`, `gzip`, and `argparse`.
- We define a function `extract_zip_file` which extracts a zip file recursively and extracts any .gz files in it.
- The `extract_zip_file` function takes two arguments: `zip_file_path` and `output_dir`.
- The function creates the output directory if it doesn't exist.
- It opens the zip file using `zipfile.ZipFile` and extracts all the files to the output directory.
- It then iterates over all the extracted files using `os.walk`.
- If the file is a zip file, it calls the `extract_zip_file` function recursively to extract it.
- If the file is a .gz file, it reads the contents of the file and writes it to disk after removing the .gz extension.
- Finally, it deletes the original .zip or .gz file.
- The `if __name__ == '__main__':` block parses the command-line arguments using `argparse.ArgumentParser` and calls the `extract_zip_file` function with the specified arguments.
