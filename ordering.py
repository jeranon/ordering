import json
import os
import msvcrt
import datetime
import math

os.system("mode con cols=160 lines=40")

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

def home(): 
    _display_menu() 

def exitApp():
    exit

def _display_menu(): 
    clear() 
    print("Welcome to the Home page.") 
    options = {'S': scan, 'O': order, 'R': receive, 'H': history, 'X': exitApp}
    for option in options: 
        print(f"Press '{option}' to navigate to the {options[option].__name__} page.")
    key = msvcrt.getch().decode("utf-8").upper()
    if key in options: 
        clear() 
        options[key]()
    else:
        print("Invalid option.")
        _display_menu()

def scan():
    print("Welcome to the Scan page.")
    print("Scan the text string or Press Escape to return to the Home page.")
    first_char = msvcrt.getche().decode("utf-8")
    if first_char == '\x1b':
        home()
    else:
        scanned_text = first_char + input()
        process_scan(scanned_text)

def process_scan(scanned_text):
    lock_file("current.txt")
    lock_file("scanned.json")
    lock_file("ordered.json")
    # read the current.txt file to get the current index number
    with open("current.txt", "r") as f:
        current_index = f.read()
    try:
        # parse the scanned text
        item_code, supplier, description, order_quantity = scanned_text.split("{")[0], scanned_text.split("{")[1].split("|")[0], scanned_text.split("|")[1].split("}")[0], scanned_text.split("}")[1]
        # check if the item already exists in the scanned.json file
        with open("scanned.json", "r") as f:
            scanned_data = json.load(f)
        with open("ordered.json", "r") as f:
            ordered_data = json.load(f)
        for item in scanned_data:
            if item["itemCode"] == item_code:
                clear()
                print(f"{item_code} - {description} has already been scanned.")
                scan()
                return
        for item in ordered_data:
            if item["itemCode"] == item_code:
                clear()
                print(f"{item_code} - {description} has already been ordered.")
                scan()
                return
        clear()
        print(f"{item_code} - {description} has been added to the order list.")
        # get the current time
        time_stamp = datetime.datetime.now().isoformat()
        # append the scanned data to the scanned.json
        scanned_data.append({"indexNumber": current_index, "itemCode": item_code, "supplier": supplier, "description": description, "orderQuantity": order_quantity, "timeStamp": time_stamp})
        with open("scanned.json", "w") as f:
            json.dump(scanned_data, f)
        # increment the current index number
        with open("current.txt", "w") as f:
            new_index = hex(int(current_index, 16) + 1)[2:].zfill(8)
            f.write(new_index)
    except:
        clear()
        print("Invalid scan, ignoring input.")
    scan()

def display_items():
    lock_file("scanned.json")
    with open("scanned.json", "r") as f:
        data = json.load(f)
    data = sorted(data, key=lambda x: x["supplier"])
    print("line# - itemCode - supplier - description - orderQuantity - timeStamp")
    for i, item in enumerate(data):
        print("{} - {} - {} - {} - {} - {}".format(i+1, item["itemCode"], item["supplier"], item["description"], item["orderQuantity"], item["timeStamp"][:10]))
    return data

def process_order(line_number, data):
    lock_file("ordered.json")
    lock_file("scanned.json")
    item = data[line_number - 1]
    item["orderDate"] = datetime.datetime.now().isoformat()
    with open("ordered.json", "r") as f:
        ordered_data = json.load(f)
    ordered_data.append(item)
    with open("ordered.json", "w") as f:
        json.dump(ordered_data, f, indent=4)
    del data[line_number - 1]
    with open("scanned.json", "w") as f:
        json.dump(data, f)
    clear()
    print("Item has been ordered and removed from scanned items.")
    clear()
    display_items()
    print("Enter the line number of the item you want to process, or press Escape to return to the Home page.")
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
            print("Invalid input, please enter a valid line number.")
            order()

def order():
    data = display_items()
    print("Enter the line number of the item you want to process, or press Escape to return to the Home page.")
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
            print("Invalid input, please enter a valid line number.")
            order()

def receive():
    data = get_ordered_items()
    print("Enter the line number of the item you want to process, or press Escape to return to the Home page.")
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
            print("Invalid input, please enter a valid line number.")
            receive()

def process_receive(line_number, data):
    lock_file("history.json")
    lock_file("ordered.json")
    item = data[line_number - 1]
    item["receivedDate"] = datetime.datetime.now().isoformat()
    with open("history.json", "r") as f:
        history_data = json.load(f)
    history_data.append(item)
    with open("history.json", "w") as f:
        json.dump(history_data, f, indent=4)
    del data[line_number - 1]
    with open("ordered.json", "w") as f:
        json.dump(data, f)
    clear()
    print("Item has been received and has been archived.")
    receive()

def get_ordered_items():
    lock_file("ordered.json")
    with open("ordered.json", "r") as f:
        data = json.load(f)
    sortedData = sorted(data, key=lambda x: x["supplier"])
    print("line# - itemCode - supplier - description - orderQuantity - orderDate")
    for i, item in enumerate(sortedData):
        print("{} - {} - {} - {} - {} - {}".format(i+1, item["itemCode"], item["supplier"], item["description"], item["orderQuantity"], item["orderDate"][:10]))
    return data

def combine():
    combined_data = []
    lock_file("scanned.json")
    lock_file("ordered.json")
    lock_file("history.json")
    with open("scanned.json", "r") as f:
        scanned_data = json.load(f)
        for item in scanned_data:
            if "orderDate" not in item:
                item["orderDate"] = "no data"
            if "receivedDate" not in item:
                item["receivedDate"] = "no data"
        combined_data.extend(scanned_data)
    with open("ordered.json", "r") as f:
        ordered_data = json.load(f)
        for item in ordered_data:
            if "receivedDate" not in item:
                item["receivedDate"] = "no data"
        combined_data.extend(ordered_data)
    with open("history.json", "r") as f:
        history_data = json.load(f)
        combined_data.extend(history_data)
    combined_data = sorted(combined_data, key=lambda x: x["timeStamp"], reverse=True)
    for item in combined_data:
        item["itemCode"] = item["itemCode"][:20]
        item["description"] = item["description"][:40]
        if "timeStamp" in item:
            item["timeStamp"] = item["timeStamp"][:10]
        if "orderDate" in item:
            item["orderDate"] = item["orderDate"][:10]
        if "receivedDate" in item:
            item["receivedDate"] = item["receivedDate"][:10]
    return combined_data

def history():
    combined_data = combine()
    page_number = 1
    while True:
        key = msvcrt.getwch()
        clear()
        filtered_data = combined_data
        print("History page.")
        print("Press 'Enter' to view all items or scan an item tag to filter the list.")
        print("Use 'Page Up' and 'Page Down' to navigate between pages.")
        print("Press 'Escape' to return to the home page.")
        first_char = msvcrt.getche().decode("utf-8")
        if first_char == chr(27): # Escape key
            home()
        elif first_char == chr(13): # Enter key
            pass
        else:
            scanned_text = first_char + input()
            filtered_data = [item for item in combined_data if item["itemCode"] == scanned_text]
        total_pages = math.ceil(len(filtered_data) / 30)
        start_index = (page_number - 1) * 30
        end_index = start_index + 30
        current_page_data = filtered_data[start_index:end_index]
        if len(current_page_data) == 0:
            print("No data found.")
        else:
            print("{:<20}  {:<40}  {:<10}  {:<10}  {:<10}".format("Item", "Description", "Scanned", "Ordered", "Received"))
            for item in current_page_data:
                print("{itemCode:<20}  {description:<40}  {timeStamp:<10}  {orderDate:<10}  {receivedDate:<10}".format(**item))
            if page_number > 1:
                print("Press 'Page Up' to view previous page.")
            if page_number < total_pages:
                print("Press 'Page Down' to view next page.")
        if key == '\xE0':
            key = msvcrt.getwch()
            if key == '\x48' and page_number > 1: # Page Up key
                page_number -= 1
            elif key == '\x51' and page_number < total_pages: # Page Down key
                page_number += 1

home()