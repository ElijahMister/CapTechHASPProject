# -*- coding: utf-8 -*-
"""
CombineFiles.py

Take in all the files and put them into one large file.
Reports the files that that were corrupted. 
"""

import os

def process_data_files():
    total_files = 0
    corrupted_files = []
    combined_data = []

    # Get the current working directory
    current_directory = os.getcwd()

    # Iterate through data files in the directory
    for filename in os.listdir(current_directory):
        if filename.startswith("TRAPSat_Data_") and not os.path.isdir(filename):
            file_path = os.path.join(current_directory, filename)

            # Check if the file has 10 lines
            if is_file_corrupted(file_path):
                corrupted_files.append(filename)
                total_files += 1
            else:
                # Read data from the file
                try:
                    with open(file_path, 'r', newline='') as current_file:
                        data_lines = [line for line in current_file]
                        combined_data.extend(data_lines)
                    
                    total_files += 1
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    # Create a new combined file
    combined_file_path = os.path.join(current_directory, "combined_data.txt")
    
    # Write combined data to the new file
    with open(combined_file_path, 'w', newline='') as combined_file:
        combined_file.writelines(combined_data)

    # Calculate the percentage of corrupted files
    percentage_corrupted = (len(corrupted_files) / total_files) * 100 if total_files != 0 else 0
    
    # Print the report
    print("Processed {} files.".format(total_files))
    print("Corrupted files: {}".format(corrupted_files))
    print("Percentage of corrupted files: {:.2f}%".format(percentage_corrupted))

def is_file_corrupted(file_path):
    try:
        with open(file_path, 'r') as file:
            # Count the number of lines in the file
            line_count = sum(1 for _ in file)
            return line_count != 20
    except Exception as e:
        print(f"Error checking {file_path} for corruption: {e}")
        return True

# Call the function to process data files in the current directory
process_data_files()