import json
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime
import os
import re
import sys
import datetime

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

def add_metadata_to_image(image_data, date_str):
    try:
        image = Image.open(image_data)
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    date_exif = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").strftime("%Y:%m:%d %H:%M:%S")

    exif_data = image.getexif()

    datetime_tag = 306
    exif_data[datetime_tag] = date_exif
    datetime_digitized_tag = 36867
    exif_data[datetime_digitized_tag] = date_exif

    save_directory = "snapchat"
    os.makedirs(save_directory, exist_ok=True)
    save_path = f"{save_directory}/{date_str.replace(':', '-')}.jpg"

    image.save(save_path, exif=exif_data)
    print(f"Image saved with date metadata: {date_exif} at {save_path}")

def snapchatexport(topic, json_file_path, log, force):
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

    with open(json_file_path, 'r') as file:
        json_data = json.load(file)

    for entry in json_data:
        date = entry["Date"].replace(" UTC", "")
        download_link = entry["Download Link"]

        image_data = download_file(download_link)
        if image_data:
            add_metadata_to_image(image_data, date)
        else:
            print(f"Failed to download or process image from {download_link}")

    if log:
        print("\n\n\n")
        sys.stdout.close()
        sys.stdout = sys.__stdout__
        print(f'[{datetime.datetime.now()}] BVD abgeschlossen.')