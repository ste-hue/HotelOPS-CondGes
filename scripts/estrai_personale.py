#!/usr/bin/env python3
"""
Estrae costi personale dai file prospetti contabili (PC)
Fonte: data/personale/PROSPETTO ORTI/*.xlsx e data/personale/PROSPETTO INTUR/*.xlsx
Output: output/personale_mensile.csv

Tipi file:
- *_PC_MM_YYYY.xlsx: dipendenti fissi
- *_PCSTAG_MM_YYYY.xlsx: stagionali
- *_PCCOLLAB_MM_YYYY.xlsx: collaboratori
- *_PC_14_YYYY.xlsx: 13ma/14ma fine anno
"""

import pandas as pd
from pathlib import Path
import re

# Voci da includere (Tipo conto = 'E')
# ESCLUSE: Ferie, ROL (come da CLAUDE.md)
VOCI_PERSONALE = [
    'Retribuzioni',
    'Retrib. Stage',
    'Trasferte',
    'Rimborso spese Km extracomune',
    'Contributi Inps',           # attenzione: minuscolo!
    'Contributi ASPI Inps',
    'Recupero contributi Inps',  # viene sottratto automaticamente (Avere > Dare)
    'Premio Inail mese',
    'Premio Inail retrib.differite',
    'Accanton. 13ma',
    'Accanton. 14ma',
    'Accanton. TFR mese',
    'Accanton. TFR retrib.differite',
    'Oneri previd. Accant. 13ma',
    'Oneri previd. Accant. 14ma',
]

# Voci esplicitamente escluse
VOCI_ESCLUSE = [
    'Accanton. Ferie',
    'Accanton. R.O.L.',
    'Rec.0,50% Fondo TFR',  # partita di giro
]


def estrai_personale(file_path: Path) -> dict:
    """Estrae costo personale da un file PC"""
    df = pd.read_excel(file_path, sheet_name='FoglioDati')

    # Filtra solo Tipo conto = 'E' (Economico)
    df_eco = df[df['Tipo conto'] == 'E'].copy()

    # Calcola saldo per ogni voce
    totale = 0.0
    dettaglio = {}

    for _, row in df_eco.iterrows():
        desc = str(row['Descrizione']).strip()
        dare = float(row['Dare']) if pd.notna(row['Dare']) else 0.0
        avere = float(row['Avere']) if pd.notna(row['Avere']) else 0.0
        saldo = dare - avere

        # Salta voci escluse
        if any(desc.startswith(v) for v in VOCI_ESCLUSE):
            continue

        # Controlla se è una voce da includere
        for voce in VOCI_PERSONALE:
            if desc.startswith(voce) or desc == voce:
                totale += saldo
                dettaglio[desc] = dettaglio.get(desc, 0) + saldo
                break

    # Estrai mese e anno dal dataframe
    mese = int(df['Mese'].iloc[0])
    anno = int(df['Anno'].iloc[0])

    return {
        'anno': anno,
        'mese': mese,
        'totale': round(totale, 2),
        'dettaglio': dettaglio,
        'file': file_path.name
    }


def parse_file_type(filename: str) -> str:
    """Identifica il tipo di file PC"""
    if '_PCSTAG_' in filename:
        return 'stagionali'
    elif '_PCCOLLAB_' in filename or '_PCCOLL_' in filename:
        return 'collaboratori'
    elif '_PC_14_' in filename:
        return '13ma_14ma'
    else:
        return 'dipendenti'


def main():
    base_path = Path('data/personale')
    results = []

    # Processa ORTI
    orti_path = base_path / 'PROSPETTO ORTI'
    if orti_path.exists():
        for f in sorted(orti_path.glob('ORT_PC*.xlsx')):
            print(f"Processing {f.name}...")
            try:
                data = estrai_personale(f)
                data['societa'] = 'ORTI'
                data['tipo'] = parse_file_type(f.name)
                results.append(data)
            except Exception as e:
                print(f"  ERRORE: {e}")
    else:
        print(f"Directory non trovata: {orti_path}")

    # Processa INTUR
    intur_path = base_path / 'PROSPETTO INTUR'
    if intur_path.exists():
        for f in sorted(intur_path.glob('INT_PC*.xlsx')):
            print(f"Processing {f.name}...")
            try:
                data = estrai_personale(f)
                data['societa'] = 'INTUR'
                data['tipo'] = parse_file_type(f.name)
                results.append(data)
            except Exception as e:
                print(f"  ERRORE: {e}")
    else:
        print(f"Directory non trovata: {intur_path}")

    if not results:
        print("\nNessun file trovato!")
        return

    # Crea DataFrame
    df_out = pd.DataFrame(results)

    # Aggrega per società/mese (somma dipendenti + stagionali + collaboratori)
    df_agg = df_out.groupby(['societa', 'anno', 'mese']).agg({
        'totale': 'sum'
    }).reset_index()

    df_agg = df_agg.sort_values(['societa', 'anno', 'mese'])

    # Pivot per vista mensile
    pivot = df_agg.pivot(index='mese', columns='societa', values='totale').fillna(0)
    pivot['TOTALE'] = pivot.sum(axis=1)

    # Output
    output_path = Path('output')
    output_path.mkdir(exist_ok=True)

    # Dettaglio per file
    df_out[['societa', 'tipo', 'anno', 'mese', 'totale', 'file']].to_csv(
        output_path / 'personale_dettaglio.csv', index=False
    )

    # Riepilogo mensile
    pivot.to_csv(output_path / 'personale_mensile.csv')

    print("\n" + "="*60)
    print("RIEPILOGO PERSONALE 2025")
    print("="*60)
    print(pivot.to_string(float_format=lambda x: f"€{x:,.2f}"))

    print("\n" + "-"*60)
    orti_tot = pivot['ORTI'].sum() if 'ORTI' in pivot.columns else 0
    intur_tot = pivot['INTUR'].sum() if 'INTUR' in pivot.columns else 0
    print(f"TOTALE ANNO ORTI:   €{orti_tot:>12,.2f}")
    print(f"TOTALE ANNO INTUR:  €{intur_tot:>12,.2f}")
    print(f"TOTALE COMPLESSIVO: €{orti_tot + intur_tot:>12,.2f}")
    print("-"*60)

    # Dettaglio per tipo
    print("\nDETTAGLIO PER TIPO:")
    tipo_agg = df_out.groupby(['societa', 'tipo'])['totale'].sum()
    for (soc, tipo), val in tipo_agg.items():
        print(f"  {soc} - {tipo}: €{val:,.2f}")


if __name__ == '__main__':
    main()
