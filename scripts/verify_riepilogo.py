#!/usr/bin/env python3
"""Verifica valori calcolati nel Riepilogo"""

import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = "1CAT_EN6DOXyT3vEbYmnwRQh1pWrdnrCXHFWR--JtFmQ"

credentials = Credentials.from_service_account_file(
    "config/hotelHops.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_key(SPREADSHEET_ID)

ws = spreadsheet.worksheet('Riepilogo')

# Usa range get con value_render_option
print("RIEPILOGO - VALORI")
print("="*60)

# Prendi tutto il range B4:D20
data = ws.get('B4:D20', value_render_option='FORMATTED_VALUE')

labels = [
    'RICAVI TOTALI',
    '- Hotel', '- Angelina', '- CVM', '- F&B', '- Spiaggia', '- Altri',
    '',
    'COSTI TOTALI',
    '- Fissi', '- Variabili', '- Personale',
    '  (Retribuzioni)', '  (Oneri)',
    '',
    'EBITDA',
    'Margine %'
]

print(f"{'Voce':<20} {'ORTI':>15} {'INTUR':>15} {'CONSOLIDATO':>15}")
print("-"*70)

for i, row in enumerate(data):
    if i < len(labels) and labels[i]:
        orti = row[0] if len(row) > 0 else ''
        intur = row[1] if len(row) > 1 else ''
        cons = row[2] if len(row) > 2 else ''
        print(f"{labels[i]:<20} {str(orti):>15} {str(intur):>15} {str(cons):>15}")
