import imaplib
import smtplib
import os
import csv
import json
import msvcrt
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def lock_file(file_name):
    with open(file_name, 'r+') as f:
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
        except IOError as e:
            print('Error locking file: ', e)
        finally:
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)

def read_json(file_name):
    lock_file(file_name)
    with open(file_name, 'r') as f:
        return json.load(f)

def get_data():
    scanned_data = read_json("data/scanned.json")
    ordered_data = read_json("data/ordered.json")
    return scanned_data + ordered_data

def save_csv(data, file_name):
    with open(file_name, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Item Code", "Supplier", "Description", "Quantity", "Scanned Date", "Ordered Date"])
        for item in data:
            scanned_date = item.get('timeStamp', '')
            ordered_date = item.get('orderDate', '')
            writer.writerow([item['itemCode'], item['supplier'], item['description'], item['orderQuantity'], scanned_date, ordered_date])

def send_email(subject, body, to, file_path, gmail_user, gmail_password):
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body))
    
    with open(file_path, "rb") as f:
        attachment = MIMEBase("application", "octet-stream")
        attachment.set_payload(f.read())
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
    msg.attach(attachment)
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, to, msg.as_string())
        server.close()
        print(f"Email sent to {to}!")
    except Exception as e:
        print(f"Something went wrong: {e}")

if __name__ == '__main__':
    data = get_data()
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    file_name = f"data/emailed/ordering - {current_date}.csv"
    save_csv(data, file_name)

    with open("data/credentials.json", "r") as f:
        credentials = json.load(f)

    gmail_user = credentials["email"]
    gmail_password = credentials["password"]
    to = credentials["to"]

    subject = f"Ordering Data - {current_date}"
    body = "Attached is the ordering data for today."

    send_email(subject, body, to, file_name, gmail_user, gmail_password)
