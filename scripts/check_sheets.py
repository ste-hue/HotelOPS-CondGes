#!/usr/bin/env python3
"""
Verifica lo stato dei fogli - mostra VALORI CALCOLATI
"""

import gspread
from google.oauth2.service_account import Credentials
from pathlib import Path

SPREADSHEET_ID = "1CAT_EN6DOXyT3vEbYmnwRQh1pWrdnrCXHFWR--JtFmQ"
CREDS_PATH = Path("config/hotelHops.json")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def main():
    credentials = Credentials.from_service_account_file(str(CREDS_PATH), scopes=SCOPES)
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(SPREADSHEET_ID)

    # Check Riepilogo - valori calcolati
    print("="*70)
    print("FOGLIO: Riepilogo (VALORI CALCOLATI)")
    print("="*70)

    try:
        ws = spreadsheet.worksheet('Riepilogo')
        # Ottieni valori calcolati con FORMATTED_VALUE
        data = ws.get(value_render_option='FORMATTED_VALUE')

        errors = [c for row in data for c in row if str(c).startswith('#')]
        if errors:
            print(f"⚠️  ERRORI: {errors}")
        else:
            print("✅ Nessun errore")

        print("\nVALORI:")
        print("-"*70)
        print(f"{'Voce':<20} {'ORTI':>15} {'INTUR':>15} {'CONSOLIDATO':>15}")
        print("-"*70)
        for row in data[3:]:  # Skip header rows
            if len(row) >= 4 and row[0]:
                label = row[0][:20]
                orti = row[1] if len(row) > 1 else ''
                intur = row[2] if len(row) > 2 else ''
                cons = row[3] if len(row) > 3 else ''
                print(f"{label:<20} {orti:>15} {intur:>15} {cons:>15}")

    except Exception as e:
        print(f"❌ Errore: {e}")

    # Check colonne Dashboard per verificare allineamento formule
    print("\n" + "="*70)
    print("STRUTTURA COLONNE ORTI_Dashboard")
    print("="*70)

    try:
        ws = spreadsheet.worksheet('ORTI_Dashboard')
        headers = ws.row_values(1)
        print("Colonne:")
        for i, h in enumerate(headers, 1):
            col_letter = chr(64 + i) if i <= 26 else f"A{chr(64 + i - 26)}"
            print(f"  {col_letter}: {h}")

    except Exception as e:
        print(f"❌ Errore: {e}")

    print("\n" + "="*70)
    print("VERIFICA COMPLETATA")
    print("="*70)

if __name__ == '__main__':
    main()
