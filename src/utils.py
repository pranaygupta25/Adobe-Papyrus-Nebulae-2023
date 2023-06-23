import csv
import os



def setup_output_csv(output_file_path):
    """
    Sets up a new CSV file for output.

    Args:
    - output_file_path: The path to the output CSV file.
    """

    #Checking and removing if an older output file exists
    if os.path.isfile(output_file_path):
        print('Existing file found.\nRemoving existing file...')
        os.remove(output_file_path)

    #Headers for the CSV as required by the challenge guidelines
    headers = [
        'Bussiness__City',
        'Bussiness__Country',
        'Bussiness__Description',
        'Bussiness__Name',
        'Bussiness__StreetAddress',
        'Bussiness__Zipcode',
        'Customer__Address__line1',
        'Customer__Address__line2',
        'Customer__Email',
        'Customer__Name',
        'Customer__PhoneNumber',
        'Invoice__BillDetails__Name',
        'Invoice__BillDetails__Quantity',
        'Invoice__BillDetails__Rate',
        'Invoice__Description',
        'Invoice__DueDate',
        'Invoice__IssueDate',
        'Invoice__Number',
        'Invoice__Tax'
    ]

    #Writing the headers to the output CSV
    with open(output_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
    print('CSV initialized...')


def delete_directory(directory_path):
    """
    Deletes a directory and its contents.

    Args:
    - directory_path: The path to the directory to be deleted.
    """
    for root, dirs, files in os.walk(directory_path, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            os.rmdir(dir_path)
    os.rmdir(directory_path)