import json
import os
import msvcrt
import datetime

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

def display_items():
    lock_file("data/scanned.json")
    with open("data/scanned.json", "r") as f:
        data = json.load(f)
    data = sorted(data, key=lambda x: (x["supplier"], x["itemCode"]))
    header = "line#ItemCodeSupplierDescriptionQtyScanDate"
    header = "\033[1m" + "| " + header[:5].ljust(5) + " | " + header[5:13].ljust(18) + " | " + header[13:21].ljust(18) + " | " + header[21:32].ljust(40) + " | " + header[32:35].ljust(20) + " | " + header[35:].ljust(10) + " |" + "\033[0m"
    print_blue("Welcome to the Order Page.\n")
    print(" " + Format.underline + header + Format.end + " ")
    for i, item in enumerate(data):
        itemCode = item["itemCode"][:18].ljust(18)
        supplier = item["supplier"][:18].ljust(18)
        description = item["description"][:40].ljust(40)
        orderQuantity = str(item["orderQuantity"])[:20].ljust(20)
        timeStamp = item["timeStamp"][:10].ljust(10)
        line = "| " + str(i+1).ljust(5) + " | " + itemCode + " | " + supplier + " | " + description + " | " + orderQuantity + " | " + timeStamp + " |"
        print(" " + line + " ")
    return data

def process_order(line_number, data):
    lock_file("data/ordered.json")
    lock_file("data/scanned.json")
    item = data[line_number - 1]
    item["orderDate"] = datetime.datetime.now().isoformat()
    with open("data/ordered.json", "r") as f:
        ordered_data = json.load(f)
    ordered_data.append(item)
    with open("data/ordered.json", "w") as f:
        json.dump(ordered_data, f, indent=4)
    del data[line_number - 1]
    with open("data/scanned.json", "w") as f:
        json.dump(data, f)
    clear()
    print_green("Item has been ordered.")
    display_items()
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
        except ValueError:
            clear()
            print_red("Invalid input, please enter a valid line number.")
            order()

def order():
    data = display_items()
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
            display_items()
            order()
        except ValueError:
            clear()
            print_red("Invalid input, please enter a valid line number.")
            order()

def receive():
    data = get_ordered_items()
    print_green("\nEnter the line number of the item you want to process, or press Escape to return to the Home page.")
    first_char = msvcrt.getche().decode("utf-8")
    if first_char == '\x1b':
        home()
    else:
        try:
            line_number = int(first_char + input())
            if line_number < 1 or line_number > len(data):
                raise ValueError("Invalid line number.")
            process_receive(line_number, data)
        except ValueError:
            clear()
            print_red("Invalid input, please enter a valid line number.")
            receive()

def process_receive(line_number, data):
    lock_file("data/history.json")
    lock_file("data/ordered.json")
    item = data[line_number - 1]
    item["receivedDate"] = datetime.datetime.now().isoformat()
    with open("data/history.json", "r") as f:
        history_data = json.load(f)
    history_data.append(item)
    with open("data/history.json", "w") as f:
        json.dump(history_data, f, indent=4)
    del data[line_number - 1]
    with open("data/ordered.json", "w") as f:
        json.dump(data, f)
    clear()
    print_green("Item has been received and has been archived.")
    receive()

def get_ordered_items():
    lock_file("data/ordered.json")
    with open("data/ordered.json", "r") as f:
        data = json.load(f)
    sortedData = sorted(data, key=lambda x: (x["supplier"], x["itemCode"]))
    header = "line#ItemCodeSupplierDescriptionQtyOrderDate"
    header = "\033[1m" + "| " + header[:5].ljust(5) + " | " + header[5:13].ljust(18) + " | " + header[13:21].ljust(18) + " | " + header[21:32].ljust(40) + " | " + header[32:35].ljust(20) + " | " + header[35:].ljust(10) + " |" + "\033[0m"
    print_blue("Welcome to the Receive Page.\n")
    print(" " + Format.underline + header + Format.end + " ")
    for i, item in enumerate(sortedData):
        itemCode = item["itemCode"][:18].ljust(18)
        supplier = item["supplier"][:18].ljust(18)
        description = item["description"][:40].ljust(40)
        orderQuantity = str(item["orderQuantity"])[:20].ljust(20)
        orderDate = item["orderDate"][:10].ljust(10)
        line = "| " + str(i+1).ljust(5) + " | " + itemCode + " | " + supplier + " | " + description + " | " + orderQuantity + " | " + orderDate + " |"
        print(" " + line + " ")
    return sortedData

home()
