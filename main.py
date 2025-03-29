import argparse
import os
import sys
import datetime
import exifread
import hachoir.parser
import hachoir.metadata

IMAGE_EXTENSIONS = (".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mpeg", ".mpg", ".3gp", ".m4v", ".ogv", ".h265", ".hevc")
VIDEO_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".svg", ".heif", ".heic", ".ico")

def parse_args():
    parser = argparse.ArgumentParser(description='BVD - Bilder und Videos umbenennen und sortieren')
    parser.add_argument('--topic', '-t', default='Diverses', help='Zusammenfassende Überschrift der im Verzeichnis liegenden Bilder und Videos (default: Diverses)')
    parser.add_argument('--offset_time', '-o', default=0, help='Zeitverschiebung in Sekunden (Aufnahmezeit - Wunschzeit; default: 0)')
    copy_or_rename = parser.add_mutually_exclusive_group()
    copy_or_rename.add_argument('--rename', '-r', action='store_true', help='Benennt die Dateien um (default)')
    copy_or_rename.add_argument('--copy', '-c', action='store_true', help='Erstellt Kopien der Dateien (alternative zu --rename)')
    parser.add_argument('--manual', '-m', action='store_true', help='Fragt nach Handeingabe bei unklarem Datum (default: Erstelldatum)')
    parser.add_argument('--bvd_only', '-b', action='store_true', help='Bearbeitet ausschließlich bereits mit BVD umbenannte Dateien (default: überspringt diese)')
    parser.add_argument('--logs', '-l', action='store_true', help='Erstellt ein Logfile mit den umbenannten Dateien (default: kein Logfile)')
    parser.add_argument('--force', '-f', action='store_true', help='Erzwingt die Ausführung ohne Bestätigungsaufforderung')
    args = parser.parse_args()
    if not args.copy and not args.rename:
        args.rename = True

    return args

def main(topic, time_offset: datetime.timedelta, copy, handeingabe, bvd_only, logs, force):
    if not force:
        print('thema:', topic)
        print('zeitoffset:', "-" if time_offset.total_seconds() < 0 else "", datetime.timedelta(seconds=abs(time_offset.total_seconds())))
        print('copy:', copy)
        print('handeingabe:', handeingabe)
        print('bvd_only:', bvd_only)
        print('logs:', logs)

        if 'y' != input('Fortfahren? (y/n): ').lower():
            print('Abgebrochen.')
            return

    if logs:
        sys.stdout = open('bvd.log', 'a')
        print(f'[{datetime.datetime.now()}] BVD gestartet mit den Parametern: thema={topic}, zeitoffset={time_offset.total_seconds()}, copy={copy}, handeingabe={handeingabe}, bvd_only={bvd_only}, logs={logs}')

    files = os.listdir('.')
    files = [f for f in files if (not f.startswith('BVD_')) ^ bvd_only]
    files = [os.path.join(os.getcwd(), f) for f in files if os.path.isfile(f)]
    files = [f for f in files if f.lower().endswith(IMAGE_EXTENSIONS + VIDEO_EXTENSIONS)]

    if not files:
        print('Keine Dateien gefunden.')
        return

    for file in files:
        print(f'Bearbeite {file}...')

        file_name = os.path.basename(file)
        file_extension = os.path.splitext(file_name)[1]
        file_name = os.path.splitext(file_name)[0]

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
                else:
                    print(f"Metadaten nicht gefunden in {file}")

        handeingabe_used = False
        if time is None:
            if handeingabe:
                print(f"Kein Datum gefunden in {file}. Bitte Datum eingeben (YYYY-MM-DD HH:MM:SS):")
                date_input = input()
                try:
                    time = datetime.datetime.strptime(date_input, '%Y-%m-%d %H:%M:%S')
                    handeingabe_used = True
                except ValueError:
                    print("Ungültiges Datum. Überspringe Datei.")
                    continue
            else:
                print(f"Kein Datum gefunden in {file}. Überspringe Datei.")
                continue

        time -= time_offset

        count = 0
        while True:
            new_file_name = f"BVD_{time.strftime('%Y%m%d_%H%M%S')}"
            if handeingabe_used:
                new_file_name += "h"
            if count > 0:
                new_file_name += f"_{count}"
            if any(f.startswith(new_file_name) for f in files):
                count += 1
            else:
                break

        new_file_name += f"_{topic}"

        new_file_name += f"_{file_name[:10]}"

        if time_offset:
            new_file_name += f"_t{int(abs(time_offset.total_seconds()))}"

        new_file_name += file_extension

        new_file_path = os.path.join(os.getcwd(), new_file_name)

        if copy:
            print(f"Kopiert {file} nach {new_file_path}")
            os.system(f'copy "{file}" "{new_file_path}"')
        else:
            print(f"Bennent {file} um in {new_file_path}")
            os.rename(file, new_file_path)

if __name__ == '__main__':
    parsed_args = parse_args()

    main(parsed_args.topic, datetime.timedelta(seconds=int(parsed_args.offset_time)), parsed_args.copy, parsed_args.manual, parsed_args.bvd_only, parsed_args.logs, parsed_args.force)