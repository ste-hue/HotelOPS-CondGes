#!/usr/bin/env python3
"""
Upload Dashboard CSV to Google Sheets
=====================================

Carica i dati del dashboard ORTI/INTUR su Google Sheets con formattazione.

SETUP:
1. pip install gspread google-auth
2. Scarica le credenziali del service account e salvale come:
   ~/.config/gspread/service_account.json

   Oppure specifica il percorso con --credentials

3. Assicurati che il service account abbia accesso al foglio:
   drive-audit@hotelops-suite.iam.gserviceaccount.com

USAGE:
    python upload_to_sheets.py
    python upload_to_sheets.py --credentials /path/to/credentials.json
"""

import argparse
import csv
from pathlib import Path

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    print("ERROR: Installa le dipendenze con:")
    print("  pip install gspread google-auth")
    exit(1)


# === CONFIGURAZIONE ===
SPREADSHEET_ID = "1CAT_EN6DOXyT3vEbYmnwRQh1pWrdnrCXHFWR--JtFmQ"
SERVICE_ACCOUNT_EMAIL = "drive-audit@hotelops-suite.iam.gserviceaccount.com"

# Percorsi relativi allo script
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_DIR / "output"

# File da caricare
FILES_TO_UPLOAD = {
    "ORTI_Dashboard": OUTPUT_DIR / "ORTI_dashboard_semplificato.csv",
    "INTUR_Dashboard": OUTPUT_DIR / "INTUR_dashboard_semplificato.csv",
}

# Scopes necessari
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def load_csv(filepath: Path) -> list[list[str]]:
    """Carica CSV e restituisce lista di righe."""
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        return list(reader)


def get_or_create_worksheet(spreadsheet, sheet_name: str, rows: int, cols: int):
    """Ottiene o crea un foglio con il nome specificato."""
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        print(f"  Foglio '{sheet_name}' esistente, aggiornamento...")
        # Ridimensiona se necessario
        worksheet.resize(rows=rows, cols=cols)
    except gspread.WorksheetNotFound:
        print(f"  Creazione foglio '{sheet_name}'...")
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=rows, cols=cols)

    return worksheet


def format_worksheet(worksheet, num_rows: int, num_cols: int):
    """Applica formattazione al foglio."""

    # Header bold e sfondo blu
    header_format = {
        "backgroundColor": {"red": 0.27, "green": 0.45, "blue": 0.77},
        "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
        "horizontalAlignment": "CENTER",
    }

    worksheet.format("1:1", header_format)

    # Numeri con separatore migliaia (colonne B onwards)
    number_format = {
        "numberFormat": {"type": "NUMBER", "pattern": "#,##0.00"},
        "horizontalAlignment": "RIGHT",
    }

    # Applica formato numerico alle colonne dati (B:M)
    if num_cols > 1:
        # Range dalla colonna B alla fine, dalla riga 2 in poi
        data_range = f"B2:{chr(64 + num_cols)}{num_rows}"
        worksheet.format(data_range, number_format)

    # Freeze header row
    worksheet.freeze(rows=1)

    # Auto-resize columns (approssimativo)
    # gspread non supporta auto-resize diretto, usiamo larghezze fisse

    print(f"  Formattazione applicata")


def upload_to_sheets(credentials_path: str = None, spreadsheet_id: str = None):
    """Carica i CSV su Google Sheets."""

    # Usa ID specificato o default
    sheet_id = spreadsheet_id or SPREADSHEET_ID

    print("=" * 60)
    print("UPLOAD DASHBOARD SU GOOGLE SHEETS")
    print("=" * 60)

    # Autenticazione
    print("\n1. Autenticazione...")

    if credentials_path:
        creds_file = Path(credentials_path)
    else:
        # Cerca in posizioni standard
        possible_paths = [
            Path.home() / ".config" / "gspread" / "service_account.json",
            Path.home() / ".gspread" / "service_account.json",
            PROJECT_DIR / "credentials" / "service_account.json",
            SCRIPT_DIR / "service_account.json",
        ]

        creds_file = None
        for p in possible_paths:
            if p.exists():
                creds_file = p
                break

        if not creds_file:
            print("\nERROR: File credenziali non trovato.")
            print("Cercato in:")
            for p in possible_paths:
                print(f"  - {p}")
            print("\nScarica le credenziali del service account da Google Cloud Console")
            print("e salvale in una delle posizioni sopra, oppure usa --credentials")
            return False

    print(f"  Credenziali: {creds_file}")

    try:
        credentials = Credentials.from_service_account_file(
            str(creds_file),
            scopes=SCOPES
        )
        gc = gspread.authorize(credentials)
    except Exception as e:
        print(f"\nERROR: Autenticazione fallita: {e}")
        return False

    # Apri spreadsheet
    print("\n2. Apertura spreadsheet...")
    print(f"  ID: {sheet_id}")

    try:
        spreadsheet = gc.open_by_key(sheet_id)
        print(f"  Nome: {spreadsheet.title}")
    except gspread.SpreadsheetNotFound:
        print(f"\nERROR: Spreadsheet non trovato.")
        print(f"Verifica che il service account {SERVICE_ACCOUNT_EMAIL}")
        print("abbia accesso al foglio.")
        return False
    except Exception as e:
        print(f"\nERROR: {e}")
        return False

    # Carica ogni file
    print("\n3. Caricamento dati...")

    for sheet_name, csv_path in FILES_TO_UPLOAD.items():
        print(f"\n  [{sheet_name}]")

        if not csv_path.exists():
            print(f"    SKIP: File non trovato: {csv_path}")
            continue

        # Carica dati
        data = load_csv(csv_path)
        if not data:
            print(f"    SKIP: File vuoto")
            continue

        num_rows = len(data)
        num_cols = len(data[0]) if data else 0
        print(f"    Righe: {num_rows}, Colonne: {num_cols}")

        # Crea/aggiorna foglio
        worksheet = get_or_create_worksheet(spreadsheet, sheet_name, num_rows + 5, num_cols)

        # Pulisci e scrivi dati
        worksheet.clear()
        worksheet.update(range_name="A1", values=data)
        print(f"    Dati scritti")

        # Formattazione
        format_worksheet(worksheet, num_rows, num_cols)

    # Aggiungi foglio riepilogo
    print("\n4. Creazione foglio Riepilogo...")
    create_summary_sheet(spreadsheet)

    print("\n" + "=" * 60)
    print("COMPLETATO!")
    print(f"Apri: https://docs.google.com/spreadsheets/d/{sheet_id}")
    print("=" * 60)

    return True


def create_summary_sheet(spreadsheet):
    """Crea foglio riepilogo con formule che aggregano i dati."""

    sheet_name = "Riepilogo"

    try:
        ws = spreadsheet.worksheet(sheet_name)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=sheet_name, rows=30, cols=10)

    # Contenuto riepilogo - COLONNE AGGIORNATE:
    # H=TOT_RICAVI, I=COSTI_FISSI, J=COSTI_VARIABILI, K=RETRIBUZIONI, L=ONERI, M=PERSONALE, N=TOT_COSTI, O=EBITDA
    summary_data = [
        ["RIEPILOGO DASHBOARD 2025", "", "", ""],
        ["", "", "", ""],
        ["", "ORTI", "INTUR", "CONSOLIDATO"],
        ["RICAVI TOTALI", "=SUM(ORTI_Dashboard!H2:H13)", "=SUM(INTUR_Dashboard!H2:H13)", "=B4+C4"],
        ["- Hotel", "=SUM(ORTI_Dashboard!B2:B13)", "=SUM(INTUR_Dashboard!B2:B13)", "=B5+C5"],
        ["- Angelina", "=SUM(ORTI_Dashboard!C2:C13)", "=SUM(INTUR_Dashboard!C2:C13)", "=B6+C6"],
        ["- CVM", "=SUM(ORTI_Dashboard!D2:D13)", "=SUM(INTUR_Dashboard!D2:D13)", "=B7+C7"],
        ["- F&B", "=SUM(ORTI_Dashboard!E2:E13)", "=SUM(INTUR_Dashboard!E2:E13)", "=B8+C8"],
        ["- Spiaggia", "=SUM(ORTI_Dashboard!F2:F13)", "=SUM(INTUR_Dashboard!F2:F13)", "=B9+C9"],
        ["- Altri", "=SUM(ORTI_Dashboard!G2:G13)", "=SUM(INTUR_Dashboard!G2:G13)", "=B10+C10"],
        ["", "", "", ""],
        ["COSTI TOTALI", "=SUM(ORTI_Dashboard!N2:N13)", "=SUM(INTUR_Dashboard!N2:N13)", "=B12+C12"],
        ["- Fissi", "=SUM(ORTI_Dashboard!I2:I13)", "=SUM(INTUR_Dashboard!I2:I13)", "=B13+C13"],
        ["- Variabili", "=SUM(ORTI_Dashboard!J2:J13)", "=SUM(INTUR_Dashboard!J2:J13)", "=B14+C14"],
        ["- Personale", "=SUM(ORTI_Dashboard!M2:M13)", "=SUM(INTUR_Dashboard!M2:M13)", "=B15+C15"],
        ["  (Retribuzioni)", "=SUM(ORTI_Dashboard!K2:K13)", "=SUM(INTUR_Dashboard!K2:K13)", "=B16+C16"],
        ["  (Oneri)", "=SUM(ORTI_Dashboard!L2:L13)", "=SUM(INTUR_Dashboard!L2:L13)", "=B17+C17"],
        ["", "", "", ""],
        ["EBITDA", "=SUM(ORTI_Dashboard!O2:O13)", "=SUM(INTUR_Dashboard!O2:O13)", "=B19+C19"],
        ["Margine %", "=IF(B4=0,0,B19/B4)", "=IF(C4=0,0,C19/C4)", "=IF(D4=0,0,D19/D4)"],
    ]

    ws.update(range_name="A1", values=summary_data)

    # Formattazione
    ws.format("A1", {
        "textFormat": {"bold": True, "fontSize": 14},
    })

    ws.format("A3:D3", {
        "backgroundColor": {"red": 0.27, "green": 0.45, "blue": 0.77},
        "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
        "horizontalAlignment": "CENTER",
    })

    ws.format("B4:D19", {
        "numberFormat": {"type": "NUMBER", "pattern": "#,##0.00"},
        "horizontalAlignment": "RIGHT",
    })

    ws.format("B20:D20", {
        "numberFormat": {"type": "PERCENT", "pattern": "0.0%"},
        "horizontalAlignment": "RIGHT",
    })

    # Evidenzia EBITDA
    ws.format("A19:D19", {
        "backgroundColor": {"red": 0.85, "green": 0.92, "blue": 0.83},
        "textFormat": {"bold": True},
    })

    # Evidenzia Personale (include breakdown)
    ws.format("A15:D17", {
        "backgroundColor": {"red": 0.95, "green": 0.95, "blue": 0.85},
    })

    print("  Foglio Riepilogo creato con formule")


def main():
    parser = argparse.ArgumentParser(
        description="Carica dashboard CSV su Google Sheets"
    )
    parser.add_argument(
        "--credentials", "-c",
        help="Percorso al file credenziali service account JSON"
    )
    parser.add_argument(
        "--spreadsheet-id", "-s",
        default=SPREADSHEET_ID,
        help=f"ID dello spreadsheet (default: {SPREADSHEET_ID})"
    )

    args = parser.parse_args()

    success = upload_to_sheets(
        credentials_path=args.credentials,
        spreadsheet_id=args.spreadsheet_id
    )
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
