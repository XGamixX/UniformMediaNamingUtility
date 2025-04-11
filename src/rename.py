import os
import sys
import datetime
import dateparser
import exifread
import re
import zoneinfo
import hachoir.parser
import hachoir.metadata

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".svg", ".heif", ".heic", ".ico")
VIDEO_EXTENSIONS = (".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mpeg", ".mpg", ".3gp", ".m4v", ".ogv", ".h265", ".hevc")

def parse_duration(time_str):
    if time_str.isdigit():
        return datetime.timedelta(minutes=int(time_str))

    base_time = datetime.datetime(2000, 1, 1)
    dt = dateparser.parse(time_str, languages=["de"], settings={'RELATIVE_BASE': base_time})

    if dt:
        return dt - base_time

    matches = re.findall(r"(\d*\.?\d+)\s*(h|m|s)", time_str)

    total_seconds = 0
    time_units = {"h": 3600, "m": 60, "s": 1}

    for value, unit in matches:
        total_seconds += float(value) * time_units[unit]

    return datetime.timedelta(seconds=total_seconds)

def extract_time(file, timezone):
    time = None
    if file.lower().endswith(IMAGE_EXTENSIONS):
        with open(file, 'rb') as f:
            tags = exifread.process_file(f)
            if 'EXIF DateTimeOriginal' in tags:
                time = str(tags['EXIF DateTimeOriginal'])
                time = datetime.datetime.strptime(time, '%Y:%m:%d %H:%M:%S')
            else:
                print(f"EXIF-Daten nicht gefunden in {file}")
    elif file.lower().endswith(VIDEO_EXTENSIONS):
        with open(file, 'rb') as f:
            parser = hachoir.parser.createParser(f)
            metadata = hachoir.metadata.extractMetadata(parser)
            if metadata and metadata.has("creation_date"):
                time = metadata.get("creation_date")
                time = time.replace(tzinfo=zoneinfo.ZoneInfo("UTC")).astimezone(zoneinfo.ZoneInfo(timezone))
            else:
                print(f"Metadaten nicht gefunden in {file}")
    return time

def rename(topic, timezone, offset_time, copy, handeingabe, bvd_only, log, force):
    time_offset = parse_duration(offset_time)
    if not force:
        print('thema:', topic)
        print('zeitverschiebung:', timezone)
        print('zeitoffset:', "-" if time_offset.total_seconds() < 0 else "", datetime.timedelta(seconds=abs(time_offset.total_seconds())))
        print('copy:', copy)
        print('handeingabe:', handeingabe)
        print('bvd_only:', bvd_only)
        print('logs:', log)

        if 'y' != input('Fortfahren? (y/n): ').lower():
            print('Abgebrochen.')
            return

    if log:
        sys.stdout = open('bvd.log', 'a')
        print(f'[{datetime.datetime.now()}] BVD (rename) gestartet mit den Parametern: thema={topic}, zeitoffset={time_offset.total_seconds()}, copy={copy}, handeingabe={handeingabe}, bvd_only={bvd_only}, logs={log}')

    files = os.listdir('.')
    files = [f for f in files if (not f.startswith('BVD_')) ^ bvd_only]
    files = [os.path.join(os.getcwd(), f) for f in files if os.path.isfile(f)]
    files = [f for f in files if f.lower().endswith(IMAGE_EXTENSIONS + VIDEO_EXTENSIONS)]

    if not files:
        print('Keine Dateien gefunden.')
        print("\n\n\n")
        return

    for file in files:
        print(f'\nBearbeite {file}...')

        file_name = os.path.basename(file)
        file_extension = os.path.splitext(file_name)[1]
        file_name = os.path.splitext(file_name)[0]

        time = extract_time(file, timezone)

        handeingabe_used = False
        modification_time_used = False
        if time is None:
            if handeingabe:
                print(f"Kein Datum gefunden in {file}. Bitte Datum eingeben:")
                date_input = input()
                time = dateparser.parse(date_input, languages=["de", "en"])
                if time is None:
                    print(f"Ungültiges Datum: {date_input}")
                    continue
                print(f"Datum erkannt: {time}")
                if 'y' != input("Datum korrekt? (y/n): ").lower():
                    print("Abgebrochen.")
                    continue
                handeingabe_used = True
            else:
                modification_time = os.path.getmtime(file)
                time = datetime.datetime.fromtimestamp(modification_time)
                modification_time_used = True

        time -= time_offset

        new_file_name = f"BVD_{time.strftime('%Y%m%d_%H%M%S')}"
        if handeingabe_used:
            new_file_name += "h"
        elif modification_time_used:
            new_file_name += "e"

        new_file_name += f"_{topic}"

        new_file_name += f"_{file_name[:10]}"

        if time_offset:
            new_file_name += f"_t{int(abs(time_offset.total_seconds())/60)}"

        count = 0
        while True:
            if os.path.exists(os.path.join(os.getcwd(), new_file_name + (f"_{count}" if count>0 else "") + file_extension)):
                count += 1
            else:
                break
        if count > 0:
            new_file_name += f"_{count}"

        new_file_name += file_extension

        new_file_path = os.path.join(os.getcwd(), new_file_name)

        if os.path.exists(new_file_path):
            print(f"Datei {new_file_path} existiert bereits. Abgebrochen.")
            continue

        if copy:
            print(f"Kopiert {file} nach {new_file_path}")
            os.system(f'copy "{file}" "{new_file_path}"')
        else:
            print(f"Bennent {file} um in {new_file_path}")
            os.rename(file, new_file_path)

    if log:
        print("\n\n\n")
        sys.stdout.close()
        sys.stdout = sys.__stdout__
        print(f'[{datetime.datetime.now()}] BVD abgeschlossen.')