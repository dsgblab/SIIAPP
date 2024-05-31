import os
from datetime import datetime

def get_files_info(directory, prefix="SIIAPP", start_date=None, end_date=None):
    """
    Get names and sizes (in KB) of files in the specified directory that start with the given prefix
    and were modified within the specified date range.

    :param directory: Directory to search files in.
    :param prefix: File name prefix to filter by (default is 'ssf_').
    :param start_date: Start date for the modification date filter (inclusive).
    :param end_date: End date for the modification date filter (inclusive).
    :return: List of tuples containing file names and their sizes in KB.
    """
    files_info = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.startswith(prefix):
                file_path = os.path.join(root, file)
                file_size_kb = round(os.path.getsize(file_path) / 1024)  # Size in KB
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if start_date <= file_mtime <= end_date:
                    files_info.append((file, file_size_kb, file_mtime))
    return files_info

def write_files_info_to_file(files_info, output_file):
    """
    Write the file names, sizes, and modification dates to a text file.

    :param files_info: List of tuples containing file names, their sizes in KB, and modification dates.
    :param output_file: Path to the output text file.
    """
    with open(output_file, 'w') as f:
        for file_name, file_size_kb, file_mtime in files_info:
            f.write(f"{file_name}: {file_size_kb:.2f} KB, Modified on: {file_mtime}\n")

if __name__ == "__main__":
    directory = r"\\10.10.10.251\Backup"
    output_file = r"C:\JoseDavidL\APPS\Backup_searcher"

    # Define the date range
    start_date = datetime.strptime("2024-04-01", "%Y-%m-%d")
    end_date = datetime.strptime("2024-06-30", "%Y-%m-%d")

    files_info = get_files_info(directory, start_date=start_date, end_date=end_date)
    write_files_info_to_file(files_info, output_file)

    print(f"File names, sizes, and modification dates have been written to {output_file}")
