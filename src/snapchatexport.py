import json
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime
import os
import re
import sys
import datetime
import zoneinfo

def download_file(url):
    parts = url.split("?", 1)
    base_url = parts[0]
    query_params = parts[1] if len(parts) > 1 else ""

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(base_url, data=query_params, headers=headers)

    if response.status_code == 200:
        content_type = response.headers.get("Content-Type", "")
        print(f"Content-Type: {content_type}")

        if "image" in content_type:
            return BytesIO(response.content)

        elif "text/plain" in content_type:
            print("Plain text response received. Content: ")
            print(response.text)  # Print out the plain text response
            aws_url_match = re.search(r'(https?://\S+amazonaws.com[^\s"\']*)', response.text)
            if aws_url_match:
                aws_url = aws_url_match.group(0)
                print(f"Found AWS URL: {aws_url}")
                
                aws_response = requests.get(aws_url)
                if aws_response.status_code == 200:
                    if "octet-stream" in aws_response.headers.get("Content-Type", ""):
                        return BytesIO(aws_response.content)
                    elif "image" in aws_response.headers.get("Content-Type", ""):
                        return BytesIO(aws_response.content)
                else:
                    print(f"Failed to download image from AWS URL. Status: {aws_response.status_code}")
                    return None
            else:
                print("AWS URL not found in plain text.")
                return None
    else:
        print(f"Failed to download file. Status: {response.status_code}")
        return None

def add_metadata_to_image_and_save(image_data, date_str, topic, timezone="UTC"):
    try:
        image = Image.open(image_data)
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    date = date.replace(tzinfo=zoneinfo.ZoneInfo("UTC")).astimezone(zoneinfo.ZoneInfo(timezone))
    date_exif = date.strftime("%Y:%m:%d %H:%M:%S")

    exif_data = image.getexif()

    datetime_tag = 306
    exif_data[datetime_tag] = date_exif
    datetime_digitized_tag = 36867
    exif_data[datetime_digitized_tag] = date_exif

    new_file_name = f"BVD_{date.strftime('%Y%m%d_%H%M%S')}"

    new_file_name += f"_{topic}"

    file_extension = ".jpg"

    count = 0
    while True:
        if os.path.exists(
                os.path.join(os.getcwd(), new_file_name + (f"_{count}" if count > 0 else "") + file_extension)):
            count += 1
        else:
            break
    if count > 0:
        new_file_name += f"_{count}"

    new_file_name += file_extension

    new_file_path = os.path.join(os.getcwd(), new_file_name)

    if os.path.exists(new_file_path):
        print(f"Datei {new_file_path} existiert bereits. Abgebrochen.")
        return

    print(f"Speichert Datei unter {new_file_path}")
    image.save(new_file_path, exif=exif_data)

def snapchatexport(topic, timezone, json_file_path, log, force):
    if not force:
        print('thema:', topic)
        print('json_file:', json_file_path)
        print('logs:', log)

        if 'y' != input('Fortfahren? (y/n): ').lower():
            print('Abgebrochen.')
            return

    if log:
        sys.stdout = open('bvd.log', 'a')
        print(f'[{datetime.datetime.now()}] BVD (snapchat) gestartet mit den Parametern: thema={topic}, json_file={json_file_path}, logs={log}')

    try:
        with open(json_file_path, 'r') as file:
            json_data = json.load(file)

        for entry in json_data:
            date = entry["Date"].replace(" UTC", "")
            download_link = entry["Download Link"]

            image_data = download_file(download_link)
            if image_data:
                add_metadata_to_image_and_save(image_data, date, topic, timezone)
            else:
                print(f"Failed to download or process image from {download_link}")
    finally:
        if log:
            print("\n\n\n")
            sys.stdout.close()
            sys.stdout = sys.__stdout__
            print(f'[{datetime.datetime.now()}] BVD abgeschlossen.')