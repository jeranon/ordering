import os
import json
import csv
import uuid
from datetime import datetime
from tkinter import Tk, filedialog
import msvcrt
import ctypes

#Set the console window title
ctypes.windll.kernel32.SetConsoleTitleW("Field Scan 'Dump'")

class LockedFile:
    def __init__(self, file, mode='r'):
        self.file = file
        self.mode = mode
        self.locked = False

    def __enter__(self):
        if self.mode == 'r':
            msvcrt.locking(self.file.fileno(), msvcrt.LK_LOCK, 1)
        else:
            msvcrt.locking(self.file.fileno(), msvcrt.LK_LOCK, os.path.getsize(self.file.name))
        self.locked = True
        return self.file
        
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if self.locked:
                msvcrt.locking(self.file.fileno(), msvcrt.LK_UNLCK, os.path.getsize(self.file.name))
                self.locked = False
        except:
            pass

def get_long_file_name(path):
    """Return the long path name of a given file path."""
    # Ensure the input is a valid path
    if not os.path.exists(path):
        return path

    # Use Win32 API to get the long path
    try:
        from ctypes import create_unicode_buffer, windll
        from ctypes.wintypes import MAX_PATH
        buf = create_unicode_buffer(MAX_PATH)
        if windll.kernel32.GetLongPathNameW(path, buf, MAX_PATH) > 0:
            return buf.value
    except ImportError:
        pass

    # Fallback to os.path.abspath if the API is not available
    return os.path.abspath(path)

# ask the user if they want to paste a path or select a file
while True:
    choice = input("Do you want to (P)aste a path or (S)elect a CSV file? ")
    if choice.upper() == 'P':
        path = input("Paste the absolute path of the CSV file: ")
        # convert short file name to long file name
        path = get_long_file_name(path)
        if os.path.isfile(path) and path.endswith('.csv'):
            break
        else:
            print("Invalid file path or file format. Please try again.")
    elif choice.upper() == 'S':
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        root.destroy()
        if file_path:
            path = file_path
            break
        else:
            print("Invalid file path or file format. Please try again.")
    else:
        print("Invalid choice. Please try again.")

# read the current index number from data/current.txt
with LockedFile(open('data/current.txt', 'r+')) as f:
    current_index = int(f.read().strip(), 16)

scanned_data = []
with LockedFile(open('data/scanned.json', 'r')) as f:
    try:
        scanned_data = json.load(f)
    except ValueError:
        print('Error reading data/scanned.json. Creating new file...')
        scanned_data = []

# read the data from the CSV file and append to the scanned list
scanned = []
with open(path, 'r', encoding='utf-8-sig') as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        if len(row) == 4:
            item_code, supplier, description, order_quantity = [cell.strip() for cell in row]
            timestamp = datetime.utcnow().isoformat()
            scanned.append({
                'indexNumber': hex(current_index + 1)[2:].zfill(8),
                'itemCode': item_code,
                'supplier': supplier,
                'description': description,
                'orderQuantity': order_quantity,
                'timeStamp': timestamp
            })
            current_index += 1

# write the updated current index number to data/current.txt
with LockedFile(open('data/current.txt', 'w')) as f:
    f.write(hex(current_index)[2:].zfill(8))

# append the new scanned data to the existing data and write it to data/scanned.json
scanned_data += scanned
with LockedFile(open('data/scanned.json', 'w')) as f:
    if scanned_data:
        json.dump(scanned_data, f, indent=4)
    else:
        f.write('[]')
