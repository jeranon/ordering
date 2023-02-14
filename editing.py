import json
import msvcrt
import os
import ctypes

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

def scan():
    print_blue("Welcome to the page to edit scanned.json\n")
    sorted_data = display_scanned()
    print_green("\nEnter the line number of the item you would like to edit, or enter 'x' to return to the home page.")
    key = input().upper()
    if key == 'X':
        home()
        return
    try:
        line_number = int(key) - 1
        if line_number >= len(sorted_data) or line_number < 0:
            clear()
            print_red("Invalid input. Line number out of range.")
            return scan()
        item = sorted_data[line_number]
        clear()
        print_yellow(f"\nSelected item: {item}")
        print_green("\nWould you like to (D)elete this object or (E)dit this object?")
        key = input().upper()
        if key == 'D':
            delete_item(item, 'data/scanned.json')
            clear()
            print_green("\nItem has been deleted.")
            scan()
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
                    return scan()
                clear()
                print_yellow(f"Editing key: {keys[line_number]}")
                new_value = input("Enter a new value: ")
                new_item = item.copy()
                new_item[keys[line_number]] = new_value
                edit_item(item, new_item, 'data/scanned.json')
                clear()
                print_green("\nItem has been edited.")
                scan()
            except:
                clear()
                print_red("Invalid input. Please enter a valid line number.")
                return scan()
        else:
            clear()
            print_red("Invalid input. Please enter 'D' or 'E'.")
            return scan()
    except:
        clear()
        print_red("Invalid input. Please enter a valid line number.")
        return scan()

def order():
    print_blue("Welcome to the page to edit ordered.json\n")
    sorted_data = display_ordered()
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
            return order()
        item = sorted_data[line_number]
        clear()
        print_yellow(f"\nSelected item: {item}")
        print_green("\nWould you like to (D)elete this object, (M)ove this object, or (E)dit this object?")
        key = input().upper()
        if key == 'M':
            move_to_scanned(item)
            clear()
            print_green("\nItem has been moved to scanned.json")
            order()
        elif key == 'D':
            delete_item(item, 'data/ordered.json')
            clear()
            print_green("\nItem has been deleted.")
            order()
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
                    return order()
                clear()
                print_yellow(f"Editing key: {keys[line_number]}")
                new_value = input("Enter a new value: ")
                new_item = item.copy()
                new_item[keys[line_number]] = new_value
                edit_item(item, new_item, 'data/ordered.json')
                clear()
                print_green("\nItem has been edited.")
                order()
            except:
                clear()
                print_red("Invalid input. Please enter a valid line number.")
                return order()
        else:
            clear()
            print_red("Invalid input. Please enter 'D', 'M', or 'E'.")
            return order()
    except:
        clear()
        print_red("Invalid input. Please enter a valid line number.")
        return order()

def history():
    print_blue("Welcome to the page to edit history.json\n")
    sorted_data = display_history()
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
            return history()
        item = sorted_data[line_number]
        clear()
        print_yellow(f"\nSelected item: {item}")
        print_green("\nWould you like to (D)elete this object, (M)ove this object, or (E)dit this object?")
        key = input().upper()
        if key == 'M':
            move_to_ordered(item)
            clear()
            print_green("\nItem has been moved to ordered.json")
            history()
        elif key == 'D':
            delete_item(item, 'data/history.json')
            clear()
            print_green("\nItem has been deleted.")
            history()
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
                    return history()
                clear()
                print_yellow(f"Editing key: {keys[line_number]}")
                new_value = input("Enter a new value: ")
                new_item = item.copy()
                new_item[keys[line_number]] = new_value
                edit_item(item, new_item, 'data/history.json')
                clear()
                print_green("\nItem has been edited.")
                history()
            except:
                clear()
                print_red("Invalid input. Please enter a valid line number.")
                return history()
        else:
            clear()
            print_red("Invalid input. Please enter 'D', 'M', or 'E'.")
            return history()
    except:
        clear()
        print_red("Invalid input. Please enter a valid line number.")
        return history()

def display_scanned():
    lock_file("data/scanned.json")
    with open("data/scanned.json", "r") as f:
        data = json.load(f)
    data = sorted(data, key=lambda x: x["timeStamp"], reverse=True)
    data = data[:30]
    header = "line#ItemCodeSupplierDescriptionQtyScanDate"
    header = "\033[1m" + "| " + header[:5].ljust(5) + " | " + header[5:13].ljust(18) + " | " + header[13:21].ljust(18) + " | " + header[21:32].ljust(40) + " | " + header[32:35].ljust(20) + " | " + header[35:].ljust(10) + " |" + "\033[0m"
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

def display_ordered():
    lock_file("data/ordered.json")
    with open("data/ordered.json", "r") as f:
        data = json.load(f)
    data = sorted(data, key=lambda x: x["orderDate"], reverse=True)
    data = data[:30]
    header = "line#ItemCodeSupplierDescriptionQtyOrderDate"
    header = "\033[1m" + "| " + header[:5].ljust(5) + " | " + header[5:13].ljust(18) + " | " + header[13:21].ljust(18) + " | " + header[21:32].ljust(40) + " | " + header[32:35].ljust(20) + " | " + header[35:].ljust(10) + " |" + "\033[0m"
    print(" " + Format.underline + header + Format.end + " ")
    for i, item in enumerate(data):
        itemCode = item["itemCode"][:18].ljust(18)
        supplier = item["supplier"][:18].ljust(18)
        description = item["description"][:40].ljust(40)
        orderQuantity = str(item["orderQuantity"])[:20].ljust(20)
        orderDate = item["orderDate"][:10].ljust(10)
        line = "| " + str(i+1).ljust(5) + " | " + itemCode + " | " + supplier + " | " + description + " | " + orderQuantity + " | " + orderDate + " |"
        print(" " + line + " ")
    return data

def display_history():
    lock_file("data/history.json")
    with open("data/history.json", "r") as f:
        data = json.load(f)
    sorted_data = sorted(data, key=lambda x: x["receivedDate"], reverse=True)
    sorted_data = sorted_data[:30]
    header = "line#ItemCodeSupplierDescriptionQtyReceived"
    header = "\033[1m" + "| " + header[:5].ljust(5) + " | " + header[5:13].ljust(18) + " | " + header[13:21].ljust(18) + " | " + header[21:32].ljust(40) + " | " + header[32:35].ljust(20) + " | " + header[35:].ljust(10) + " |" + "\033[0m"
    print(" " + Format.underline + header + Format.end + " ")
    for i, item in enumerate(sorted_data):
        itemCode = item["itemCode"][:18].ljust(18)
        supplier = item["supplier"][:18].ljust(18)
        description = item["description"][:40].ljust(40)
        orderQuantity = str(item["orderQuantity"])[:20].ljust(20)
        receivedDate = item["receivedDate"][:10].ljust(10)
        line = "| " + str(i+1).ljust(5) + " | " + itemCode + " | " + supplier + " | " + description + " | " + orderQuantity + " | " + receivedDate + " |"
        print(" " + line + " ")
    return sorted_data

home()
