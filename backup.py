import os
import py7zr
import datetime

# Set the name of the folder to backup
folder_name = 'data'

# Create the backup folder if it doesn't exist
backup_folder = 'backup'
if not os.path.exists(backup_folder):
    os.makedirs(backup_folder)

# Set the name of the archive file based on the current date
today = datetime.date.today().strftime('%Y-%m-%d')
archive_name = f'{backup_folder}/{today}.7z'

# Check if the archive already exists and set the folder name in the archive accordingly
if os.path.exists(archive_name):
    with py7zr.SevenZipFile(archive_name, 'a') as archive:
        folder_list = archive.getnames()
        folder_name_in_archive = f"data-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        while folder_name_in_archive in folder_list:
            folder_name_in_archive += "_1"
        archive.writeall(folder_name, arcname=folder_name_in_archive)
else:
    folder_name_in_archive = f"data-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    with py7zr.SevenZipFile(archive_name, 'w') as archive:
        archive.writeall(folder_name, arcname=folder_name_in_archive)

print(f'Backup created: {archive_name}')
