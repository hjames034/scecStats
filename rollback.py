#rollback files
import csv

# specify the file name, date column index, and target date
file_name = 'outputData-agg.csv'
date_column_index = 4  # assuming the date column is the 3rd column (0-based indexing)
target_date = '2023-04-10'

# read the original CSV file into a list of lists
with open(file_name, 'r') as file:
    reader = csv.reader(file)
    rows = [row for row in reader]

# filter out rows with the target date in the date column
filtered_rows = [row for row in rows if row[date_column_index] != target_date]

# overwrite the original CSV file with the filtered rows
with open(file_name, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(filtered_rows)
