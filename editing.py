import json
import msvcrt
import os
import ctypes
from pprint import pprint

#Set the console window title
ctypes.windll.kernel32.SetConsoleTitleW("Editing")

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

def load_json(file_name):
    try:
        lock_file(file_name)
        with open(file_name, 'r') as f:
            return json.load(f)
    except Exception as e:
        print('Error loading JSON file: ', e)
    finally:
        lock_file(file_name)

def write_json(file_name, data):
    try:
        lock_file(file_name)
        with open(file_name, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print('Error writing JSON file: ', e)
    finally:
        lock_file(file_name)

def remove_field(obj, field):
    try:
        del obj[field]
    except KeyError:
        pass
    return obj

def move_to_scanned(item):
    scanned_data = load_json('data/scanned.json')
    scanned_data.append(item)
    write_json('data/scanned.json', scanned_data)
    ordered_data = load_json('data/ordered.json')
    index = ordered_data.index(item)
    del ordered_data[index]
    write_json('data/ordered.json', ordered_data)

def move_to_ordered(item):
    ordered_data = load_json('data/ordered.json')
    ordered_data.append(item)
    write_json('data/ordered.json', ordered_data)
    history_data = load_json('data/history.json')
    index = history_data.index(item)
    del history_data[index]
    write_json('data/history.json', history_data)

def delete_item(item, file_name):
    data = load_json(file_name)
    data.remove(item)
    write_json(file_name, data)

def edit_item(item, new_item, file_name):
    data = load_json(file_name)
    index = data.index(item)
    data[index] = new_item
    write_json(file_name, data)

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
    print_blue("Welcome to the Home Page\n")
    options = {'S': scan, 'O': order, 'H': history}
    for option in options:
        print_green(f"Enter '{option}' to navigate to the {options[option].__name__} editing page.")
    key = input().upper()
    if key in options:
        clear()
        options[key]()
    else:
        print_red("Invalid option.")
        display_menu()

def edit(file_path, move_enabled=False):
    print_blue(f"Welcome to the page to edit {file_path}\n")
    sorted_data = display_data(file_path)
    print_green("\nSelect the line number of the item you would like to edit, or enter 'x' to return to the home page.")

    key = input().upper()
    if key == 'X':
        home()
        return
    try:
        line_number = int(key) - 1
        if line_number >= len(sorted_data) or line_number < 0:
            clear()
            print_red("Invalid input. Line number out of range.")
            return edit(file_path, move_enabled)
        item = sorted_data[line_number]
        clear()
        print_yellow("Selected item:")
        pprint(item, indent=4)
        print_green("\nWould you like to (D)elete this object, (E)dit this object, e(X)it to previous screen")
        if move_enabled:
            print_green("or (M)ove this object to another file?")
        key = input().upper()
        if key == 'X':
            clear()
            return edit(file_path, move_enabled)
        elif move_enabled and key == 'M':
            if file_path == 'data/ordered.json':
                move_to_scanned(item)
                clear()
                print_green("\nItem has been moved to scanned.json")
                edit(file_path, move_enabled)
            elif file_path == 'data/history.json':
                move_to_ordered(item)
                clear()
                print_green("\nItem has been moved to ordered.json")
                edit(file_path, move_enabled)
        elif key == 'D':
            delete_item(item, file_path)
            clear()
            print_green("\nItem has been deleted.")
            edit(file_path, move_enabled)
        elif key == 'E':
            i = 1
            keys = list(item.keys())
            clear()
            print_yellow("Editing object: ")
            for k in keys:
                print(f"{i}. {k}: {item[k]}")
                i += 1
            print_green("Which line would you like to edit?")
            try:
                line_number = int(input()) - 1
                if line_number >= len(keys) or line_number < 0:
                    print_red("Invalid input. Line number out of range.")
                    return edit(file_path, move_enabled)
                key_to_edit = keys[line_number]
                current_value = item[key_to_edit]
                clear()
                print_yellow(f"Editing {key_to_edit}: {current_value}")
                new_value = input("Enter a new value: ")
                new_item = item.copy()
                new_item[keys[line_number]] = new_value
                edit_item(item, new_item, file_path)
                clear()
                print_green("\nItem has been edited.")
                edit(file_path, move_enabled)
            except:
                clear()
                print_red("Invalid input. Please enter a valid line number.")
                return edit(file_path, move_enabled)
        elif move_enabled:
            clear()
            print_red("Invalid input. Please enter 'D', 'E', or 'M', or 'X'.")
            return edit(file_path, move_enabled)
        else:
            clear()
            print_red("Invalid input. Please enter 'D' or 'E', or 'X'.")
            return edit(file_path, move_enabled)
    except:
        clear()
        print_red("Invalid input. Please enter a valid line number.")
        return edit(file_path, move_enabled)

def scan():
    edit('data/scanned.json', move_enabled=False)

def order():
    edit('data/ordered.json', move_enabled=True)

def history():
    edit('data/history.json', move_enabled=True)

def display_data(filename):
    headers = {
        "data/scanned.json": "line#ItemCodeSupplierDescriptionQtyScanDate",
        "data/ordered.json": "line#ItemCodeSupplierDescriptionQtyOrderDate",
        "data/history.json": "line#ItemCodeSupplierDescriptionQtyReceived",
    }
    line_lengths = {
        "line": 5,
        "itemCode": 18,
        "supplier": 18,
        "description": 40,
        "orderQuantity": 20,
        "date": 10,
    }

    lock_file(filename)
    with open(filename, "r") as f:
        data = json.load(f)

    if filename == "data/scanned.json":
        data = sorted(data, key=lambda x: x["timeStamp"], reverse=True)
    elif filename == "data/ordered.json":
        data = sorted(data, key=lambda x: x["orderDate"], reverse=True)
    elif filename == "data/history.json":
        data = sorted(data, key=lambda x: x["receivedDate"], reverse=True)

    data = data[:30]

    header = headers[filename]
    header = "\033[1m" + "| " + header[:5].ljust(line_lengths["line"]) + " | " + header[5:13].ljust(
        line_lengths["itemCode"]
    ) + " | " + header[13:21].ljust(line_lengths["supplier"]) + " | " + header[21:32].ljust(
        line_lengths["description"]
    ) + " | " + header[32:35].ljust(line_lengths["orderQuantity"]) + " | " + header[35:].ljust(
        line_lengths["date"]
    ) + " |" + "\033[0m"
    print(" " + Format.underline + header + Format.end + " ")

    for i, item in enumerate(data):
        itemCode = item["itemCode"][: line_lengths["itemCode"]].ljust(line_lengths["itemCode"])
        supplier = item["supplier"][: line_lengths["supplier"]].ljust(line_lengths["supplier"])
        description = item["description"][: line_lengths["description"]].ljust(line_lengths["description"])
        orderQuantity = str(item["orderQuantity"])[: line_lengths["orderQuantity"]].ljust(line_lengths["orderQuantity"])

        if filename == "data/scanned.json":
            date = item["timeStamp"][: line_lengths["date"]].ljust(line_lengths["date"])
        elif filename == "data/ordered.json":
            date = item["orderDate"][: line_lengths["date"]].ljust(line_lengths["date"])
        elif filename == "data/history.json":
            date = item["receivedDate"][: line_lengths["date"]].ljust(line_lengths["date"])

        line = "| " + str(i + 1).ljust(line_lengths["line"]) + " | " + itemCode + " | " + supplier + " | " + description + " | " + orderQuantity + " | " + date + " |"
        print(" " + line + " ")

    return data

home()
