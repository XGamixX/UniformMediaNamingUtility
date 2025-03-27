import argparse

def main(thema, zeitoffset, copy, handeingabe, bvd_only):
    print('thema:', thema)
    print('zeitoffset:', zeitoffset)
    print('copy:', copy)
    print('handeingabe:', handeingabe)
    print('bvd_only:', bvd_only)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BVD - Bilder und Videos umbenennen und sortieren')
    parser.add_argument('--thema', default='Diverses', help='Zusammenfassende Überschrift der im Verzeichnis liegenden Bilder und Videos (default: Diverses)')
    parser.add_argument('--zeitoffset', default=0, help='Zeitverschiebung in Sekunden (Wunschzeit - Aufnahmezeit; default: 0)')
    copy_or_rename = parser.add_mutually_exclusive_group()
    copy_or_rename.add_argument('--rename', action='store_true', help='Benennt die Dateien um (default)')
    copy_or_rename.add_argument('--copy', action='store_true', help='Erstellt Kopien der Dateien (alternative zu --rename)')
    parser.add_argument('--handeingabe', action='store_true', help='Fragt nach Handeingabe bei unklarem Datum (default: Erstelldatum)')
    parser.add_argument('--bvd_only', action='store_true', help='Bearbeitet ausschließlich bereits mit BVD umbenannte Dateien (default: überspringt diese)')
    args = parser.parse_args()
    if not args.copy and not args.rename:
        args.rename = True

    main(args.thema, args.zeitoffset, args.copy, args.handeingabe, args.bvd_only)