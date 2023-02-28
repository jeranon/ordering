import json
import os
import msvcrt
import datetime
import ctypes

#Set the console window title
ctypes.windll.kernel32.SetConsoleTitleW("Ordering TEST ENV")

class Format:
    end = '\033[0m'
    underline = '\033[4m'

os.system("mode con bufsize=3000")

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def lock_file(file_name):
    with open(file_name, 'r+') as f:
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
        except IOError as e:
            print('Error locking file: ', e)
        finally:
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)

def print_yellow(text):
    print("\033[38;2;255;255;175m" + text + "\033[0m")

def print_green(text):
    print("\033[38;2;175;255;175m" + text + "\033[0m")

def print_red(text):
    print("\033[38;2;255;105;105m" + text + "\033[0m")

def print_blue(text):
    print("\033[38;2;175;175;255m" + text + "\033[0m")

def home(): 
    display_menu()

def display_menu(): 
    clear() 
    print_blue("Welcome to the Home page.\n") 
    options = {'S': scan, 'O': order, 'R': receive}
    for option in options: 
        print_green(f"Press '{option}' to navigate to the {options[option].__name__} page.")
    key = msvcrt.getch().decode("utf-8").upper()
    if key in options: 
        clear() 
        options[key]()
    else:
        print_red("Invalid option.")
        display_menu()

def scan():
    print_blue("Welcome to the Scan page.\n")
    print_green("Scan a barcode or Press Escape to return to the Home page.")
    first_char = msvcrt.getche().decode("utf-8")
    if first_char == '\x1b':
        home()
    else:
        scanned_text = first_char + input()
        process_scan(scanned_text)

def process(data_path):
    data = display_items(data_path)
    print_green("\nEnter the line number of the item you want to process, or press Escape to return to the Home page.")
    first_char = msvcrt.getche().decode("utf-8")
    if first_char == '\x1b':
        home()
    else:
        try:
            line_number = int(first_char + input())
            if line_number < 1 or line_number > len(data):
                raise ValueError("Invalid line number.")
            process_order(line_number, data)
            clear()
            display_items(data_path)
            order()
        except ValueError:
            clear()
            print_red("Invalid input, please enter a valid line number.")
            order()

def order():
    process("data/scanned.json")

def receive():
    process("data/ordered.json")

def process_scan(scanned_text):
    lock_file("data/current.txt")
    lock_file("data/scanned.json")
    lock_file("data/ordered.json")
    # read the current.txt file to get the current index number
    with open("data/current.txt", "r") as f:
        current_index = f.read()
    try:
        # parse the scanned text
        item_code, supplier, description, order_quantity = scanned_text.split("{")[0], scanned_text.split("{")[1].split("|")[0], scanned_text.split("|")[1].split("}")[0], scanned_text.split("}")[1]
        # check if the item already exists in the scanned.json file
        with open("data/scanned.json", "r") as f:
            scanned_data = json.load(f)
        with open("data/ordered.json", "r") as f:
            ordered_data = json.load(f)
        for item in scanned_data:
            if item["itemCode"] == item_code:
                clear()
                print_yellow(f"{item_code} - {description} has already been scanned.")
                scan()
                return
        for item in ordered_data:
            if item["itemCode"] == item_code:
                clear()
                print_yellow(f"{item_code} - {description} has already been ordered.")
                scan()
                return
        clear()
        print_green(f"{item_code} - {description} has been added to the order list.")
        # get the current time
        time_stamp = datetime.datetime.now().isoformat()
        # append the scanned data to the scanned.json
        scanned_data.append({"indexNumber": current_index, "itemCode": item_code, "supplier": supplier, "description": description, "orderQuantity": order_quantity, "timeStamp": time_stamp})
        with open("data/scanned.json", "w") as f:
            json.dump(scanned_data, f)
        # increment the current index number
        with open("data/current.txt", "w") as f:
            new_index = hex(int(current_index, 16) + 1)[2:].zfill(8)
            f.write(new_index)
    except:
        clear()
        print_red("Invalid scan, ignoring input.")
    scan()

def process_common(line_number, source_file_path, dest_file_path, key, value):
    lock_file(source_file_path)
    lock_file(dest_file_path)
    with open(source_file_path, 'r') as f:
        data = json.load(f)
    if line_number <1 or line_number > len(data):
        print_red("Invalid input, please enter a valid line number.")
        display_items(source_file_path)
        return
    item = data[line_number - 1]
    item[key] = value
    with open(dest_file_path, 'r') as f:
        dest_data = json.load(f)
    dest_data.append(item)
    with open(dest_file_path, 'w') as f:
        json.dump(dest_data, f, indent=4)
    del data[line_number - 1]
    with open(source_file_path, 'w') as f:
        json.dump(data, f)
    clear()
    print_green("Item has been processed.")
    process(source_file_path)
    
def process_order(line_number, data):
    key = "orderDate"
    value = datetime.datetime.now().isoformat()
    process_common(line_number, "data/scanned.json", "data/ordered.json", key, value)

def process_receive(line_number, data):
    key = "receivedDate"
    value = datetime.datetime.now().isoformat()
    process_common(line_number, "data/ordered.json", "data/history.json", key, value)

def display_items(file_path):
    lock_file(file_path)
    with open(file_path, "r") as f:
        data = json.load(f)
    if file_path == "data/scanned.json":
        data = sorted(data, key=lambda x: (x["supplier"], x["itemCode"]))
        header = "line#ItemCodeSupplierDescriptionQtyScanDate"
    elif file_path == "data/ordered.json":
        data = sorted(data, key=lambda x: (x["supplier"], x["itemCode"]))
        header = "line#ItemCodeSupplierDescriptionQtyOrderDate"
    else:
        raise ValueError("Invalid file path.")

    header = "\033[1m" + "| " + header[:5].ljust(5) + " | " + header[5:13].ljust(18) + " | " + header[13:21].ljust(18) + " | " + header[21:32].ljust(40) + " | " + header[32:35].ljust(20) + " | " + header[35:].ljust(10) + " |" + "\033[0m"
    print_blue("Welcome to the Order Page.\n")
    print(" " + Format.underline + header + Format.end + " ")
    for i, item in enumerate(data):
        itemCode = item["itemCode"][:18].ljust(18)
        supplier = item["supplier"][:18].ljust(18)
        description = item["description"][:40].ljust(40)
        if file_path == "data/scanned.json":
            orderQuantity = str(item["orderQuantity"])[:20].ljust(20)
            timeStamp = item["timeStamp"][:10].ljust(10)
            line = "| " + str(i+1).ljust(5) + " | " + itemCode + " | " + supplier + " | " + description + " | " + orderQuantity + " | " + timeStamp + " |"
        elif file_path == "data/ordered.json":
            orderQuantity = str(item["orderQuantity"])[:20].ljust(20)
            orderDate = item["orderDate"][:10].ljust(10)
            line = "| " + str(i+1).ljust(5) + " | " + itemCode + " | " + supplier + " | " + description + " | " + orderQuantity + " | " + orderDate + " |"
        print(" " + line + " ")
    return data

home()
