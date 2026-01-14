#!/usr/bin/env python3
"""
Crea INTUR_MASTRINO_PULITO da INTUR_mesepermese.xlsx
Struttura identica a ORTI_MASTRINO_PULITO
"""

import pandas as pd
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials

DATA_DIR = Path('data')
SPREADSHEET_ID = "1CAT_EN6DOXyT3vEbYmnwRQh1pWrdnrCXHFWR--JtFmQ"
CREDS_PATH = Path("config/hotelHops.json")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

MESI_NOMI = {
    1: '01_GENNAIO', 2: '02_FEBBRAIO', 3: '03_MARZO', 4: '04_APRILE',
    5: '05_MAGGIO', 6: '06_GIUGNO', 7: '07_LUGLIO', 8: '08_AGOSTO',
    9: '09_SETTEMBRE', 10: '10_OTTOBRE', 11: '11_NOVEMBRE', 12: '12_DICEMBRE'
}

def get_conto_levels(conto: str) -> dict:
    """Estrae i livelli gerarchici dal codice conto"""
    parts = str(conto).split('.')
    levels = {'conto_l1': '', 'conto_l2': '', 'conto_l3': ''}

    if len(parts) >= 1:
        levels['conto_l1'] = parts[0]
    if len(parts) >= 2:
        levels['conto_l2'] = f"{parts[0]}.{parts[1]}"
    if len(parts) >= 3:
        levels['conto_l3'] = f"{parts[0]}.{parts[1]}.{parts[2]}"

    return levels

def get_livello(conto: str) -> int:
    """Determina il livello gerarchico del conto"""
    parts = str(conto).split('.')
    return min(len(parts), 4)

def process_intur_mesepermese():
    """Processa INTUR_mesepermese.xlsx e crea mastrino pulito"""

    input_file = DATA_DIR / 'INTUR_mesepermese.xlsx'
    print(f"Lettura {input_file}...")

    # Leggi tutte le sheet (ogni mese è una sheet)
    xl = pd.ExcelFile(input_file)
    print(f"  Sheet trovate: {xl.sheet_names}")

    all_data = []

    for sheet_name in xl.sheet_names:
        # Estrai numero mese dal nome sheet
        try:
            # Prova a parsare il mese dal nome (es. "Gennaio", "01", etc.)
            mese_num = None
            sheet_lower = sheet_name.lower().strip()

            # Mapping nomi italiani
            mesi_map = {
                'gennaio': 1, 'febbraio': 2, 'marzo': 3, 'aprile': 4,
                'maggio': 5, 'giugno': 6, 'luglio': 7, 'agosto': 8,
                'settembre': 9, 'ottobre': 10, 'novembre': 11, 'dicembre': 12
            }

            for nome, num in mesi_map.items():
                if nome in sheet_lower:
                    mese_num = num
                    break

            if mese_num is None:
                # Prova parsing numerico
                import re
                match = re.search(r'(\d+)', sheet_name)
                if match:
                    mese_num = int(match.group(1))

            if mese_num is None or mese_num < 1 or mese_num > 12:
                print(f"  Skipping sheet '{sheet_name}' - non riconosciuto come mese")
                continue

        except Exception as e:
            print(f"  Skipping sheet '{sheet_name}': {e}")
            continue

        print(f"  Processing: {sheet_name} -> mese {mese_num}")

        df = pd.read_excel(input_file, sheet_name=sheet_name)

        # Trova le colonne rilevanti (possono avere nomi diversi)
        col_mapping = {}
        for col in df.columns:
            col_lower = str(col).lower()
            if 'conto' in col_lower and 'desc' not in col_lower:
                col_mapping['Conto'] = col
            elif 'descrizione' in col_lower or 'desc' in col_lower:
                col_mapping['Descrizione'] = col
            elif 'dare' in col_lower:
                col_mapping['dare'] = col
            elif 'avere' in col_lower:
                col_mapping['avere'] = col
            elif 'saldo' in col_lower:
                col_mapping['saldo'] = col
            elif 'partitari' in col_lower:
                col_mapping['Partitari'] = col

        if 'Conto' not in col_mapping:
            print(f"    WARN: Colonna 'Conto' non trovata in {sheet_name}")
            print(f"    Colonne disponibili: {list(df.columns)}")
            continue

        # Processa ogni riga
        for _, row in df.iterrows():
            conto = row.get(col_mapping.get('Conto', ''), '')
            if pd.isna(conto) or str(conto).strip() == '':
                continue

            conto = str(conto).strip()

            record = {
                'mese': mese_num,
                'mese_foglio': MESI_NOMI.get(mese_num, f'{mese_num:02d}'),
                'Conto': conto,
                'Partitari': row.get(col_mapping.get('Partitari', ''), ''),
                'Descrizione': row.get(col_mapping.get('Descrizione', ''), ''),
                'dare': row.get(col_mapping.get('dare', ''), 0) or 0,
                'avere': row.get(col_mapping.get('avere', ''), 0) or 0,
                'livello': get_livello(conto),
            }

            # Calcola saldo se non presente
            if col_mapping.get('saldo'):
                record['saldo'] = row.get(col_mapping['saldo'], 0) or 0
            else:
                dare = float(record['dare']) if pd.notna(record['dare']) else 0
                avere = float(record['avere']) if pd.notna(record['avere']) else 0
                record['saldo'] = dare - avere

            # Aggiungi livelli conto
            levels = get_conto_levels(conto)
            record.update(levels)

            all_data.append(record)

    if not all_data:
        print("ERRORE: Nessun dato estratto!")
        return None

    # Crea DataFrame
    df_out = pd.DataFrame(all_data)

    # Ordina per mese e conto
    df_out = df_out.sort_values(['mese', 'Conto'])

    # Colonne in ordine corretto
    columns = ['mese', 'mese_foglio', 'Conto', 'Partitari', 'Descrizione',
               'dare', 'avere', 'saldo', 'livello', 'conto_l1', 'conto_l2', 'conto_l3']
    df_out = df_out[columns]

    print(f"\nTotale righe: {len(df_out)}")
    print(f"Mesi presenti: {sorted(df_out['mese'].unique())}")

    return df_out


def upload_to_sheets(df: pd.DataFrame):
    """Carica il mastrino su Google Sheets"""

    print("\nUpload su Google Sheets...")

    credentials = Credentials.from_service_account_file(str(CREDS_PATH), scopes=SCOPES)
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(SPREADSHEET_ID)

    sheet_name = "INTUR_MASTRINO_PULITO"

    try:
        ws = spreadsheet.worksheet(sheet_name)
        print(f"  Foglio '{sheet_name}' esistente, aggiornamento...")
        ws.clear()
    except gspread.WorksheetNotFound:
        print(f"  Creazione foglio '{sheet_name}'...")
        ws = spreadsheet.add_worksheet(title=sheet_name, rows=len(df)+10, cols=15)

    # Prepara dati
    header = df.columns.tolist()
    data = df.fillna('').astype(str).values.tolist()
    all_data = [header] + data

    # Scrivi
    ws.update(range_name="A1", values=all_data)
    print(f"  Scritte {len(data)} righe")

    # Formattazione header
    ws.format("1:1", {
        "backgroundColor": {"red": 0.27, "green": 0.45, "blue": 0.77},
        "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
        "horizontalAlignment": "CENTER",
    })

    # Freeze header
    ws.freeze(rows=1)

    print("  Formattazione applicata")


def main():
    print("="*60)
    print("CREAZIONE INTUR_MASTRINO_PULITO")
    print("="*60)

    df = process_intur_mesepermese()

    if df is not None:
        # Salva CSV locale
        output_path = Path('output') / 'INTUR_mastrino_pulito.csv'
        df.to_csv(output_path, index=False)
        print(f"\nSalvato: {output_path}")

        # Upload su Sheets
        upload_to_sheets(df)

        print("\n" + "="*60)
        print("COMPLETATO!")
        print(f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")
        print("="*60)


if __name__ == '__main__':
    main()
