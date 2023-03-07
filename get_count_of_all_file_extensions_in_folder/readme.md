# Count the number of files with each extension in a folder

This Python script counts the number of files with each extension in a folder and its subfolders. It uses the `os` module to traverse the folder and its subfolders and the `argparse` module to accept the folder path as an argument.

## Prerequisites

- Python 3.x
- `argparse` module

## Usage

1. Clone the repository.
2. Open a command prompt or terminal window and navigate to the folder containing the `get_count_of_all_file_extensions_in_folder.py` file.
3. Run the script with the following command:



```commandline
python get_count_of_all_file_extensions_in_folder.py <FOLDER_PATH>
```

Replace `<FOLDER_PATH>` with the path to the folder you want to search.

## Example

To count the number of files with each extension in the `C:\Users\UserName\Documents` folder, run the following command:

```commandline
python get_count_of_all_file_extensions_in_folder.py C:\Users\UserName\Documents
```


## Output

The script will output the number of files with each extension in the folder and its subfolders. For example:

```commandline
pdf: 12
docx: 8
xlsx: 4
jpg: 35
png: 22
```
This means there are 12 PDF files, 8 DOCX files, 4 XLSX files, 35 JPG files, and 22 PNG files in the folder and its subfolders.

