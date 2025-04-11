import platform
import argparse
import sys

import snapchatexport
import rename

def parse_args():
    parser = argparse.ArgumentParser(description='BVD - Bilder und Videos umbenennen und sortieren')
    subparsers = parser.add_subparsers(dest='command', required=True, help='Liste der Befehle')

    rename_parser = subparsers.add_parser('rename', help='Bilder und Videos umbenennen')
    rename_parser.add_argument('--topic', '-t', default='Diverses', help='Zusammenfassende Überschrift der im Verzeichnis liegenden Bilder und Videos (default: Diverses)')
    rename_parser.add_argument('--timezone', '-z', default='Europe/Berlin', help='Zeitzone für die Zeitverschiebung (IANA tz format; default: Europe/Berlin)')
    rename_parser.add_argument('--offset_time', '-o', default='', help='Manuelle Zeitverschiebung (in Worten oder Minuten; Aufnahmezeit - Wunschzeit; default: 0)')
    copy_or_rename = rename_parser.add_mutually_exclusive_group()
    copy_or_rename.add_argument('--rename', '-r', action='store_true', help='Benennt die Dateien um (default)')
    copy_or_rename.add_argument('--copy', '-c', action='store_true', help='Erstellt Kopien der Dateien (alternative zu --rename)')
    rename_parser.add_argument('--manual', '-m', action='store_true', help='Fragt nach Handeingabe bei unklarem Datum (default: Erstelldatum)')
    rename_parser.add_argument('--bvd_only', '-b', action='store_true', help='Bearbeitet ausschließlich bereits mit BVD umbenannte Dateien (default: überspringt diese)')
    rename_parser.add_argument('--log', '-l', action='store_true', help='Erstellt ein Logfile mit den umbenannten Dateien (default: kein Logfile)')
    rename_parser.add_argument('--force', '-f', action='store_true', help='Erzwingt die Ausführung ohne Bestätigungsaufforderung')

    snapchat_parser = subparsers.add_parser('snapchat', help='Bilder und Videos von Snapchat umbenennen')
    snapchat_parser.add_argument('--topic', '-t', default='Diverses', help='Zusammenfassende Überschrift der im Download vorhandednen Bilder und Videos (default: Diverses)')
    snapchat_parser.add_argument('--json_file', '-j', required=True, help='Pfad zur JSON-Datei mit den Metadaten')
    snapchat_parser.add_argument('--log', '-l', action='store_true', help='Erstellt ein Logfile mit den umbenannten Dateien (default: kein Logfile)')
    snapchat_parser.add_argument('--force', '-f', action='store_true', help='Erzwingt die Ausführung ohne Bestätigungsaufforderung')

    args = parser.parse_args()
    if not args.copy and not args.rename:
        args.rename = True
    return args

def main():
    parsed_args = parse_args()

    if parsed_args.command == 'snapchat':
        snapchatexport.snapchatexport(parsed_args.topic, parsed_args.json_file, parsed_args.log, parsed_args.force)
    elif parsed_args.command == 'rename':
        rename.rename(parsed_args.topic, parsed_args.timezone, parsed_args.offset_time, parsed_args.copy, parsed_args.manual, parsed_args.bvd_only, parsed_args.logs, parsed_args.force)
    else:
        print('Unbekannter Befehl:', parsed_args.command)
        sys.exit(1)

if __name__ == '__main__':
    if platform.system() != 'Windows':
        print('Dieses Skript ist nur für Windows-Betriebssysteme geeignet.')
        sys.exit(1)

    main()