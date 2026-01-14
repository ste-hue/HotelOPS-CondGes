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

Output separato:
- RETRIBUZIONI: stipendi puri
- ONERI: contributi, accantonamenti, TFR, trasferte
"""

import pandas as pd
from pathlib import Path
import re

# RETRIBUZIONI = stipendi puri
VOCI_RETRIBUZIONI = [
    'Retribuzioni',
    'Retrib. Stage',
]

# ONERI = contributi + accantonamenti + altro
VOCI_ONERI = [
    'Trasferte',
    'Rimborso spese Km extracomune',
    'Contributi Inps',
    'Contributi ASPI Inps',
    'Recupero contributi Inps',
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
    """Estrae costo personale da un file PC, separando retribuzioni da oneri"""
    df = pd.read_excel(file_path, sheet_name='FoglioDati')

    # Filtra solo Tipo conto = 'E' (Economico)
    df_eco = df[df['Tipo conto'] == 'E'].copy()

    # Calcola saldo per ogni voce
    retribuzioni = 0.0
    oneri = 0.0
    dettaglio = {}

    for _, row in df_eco.iterrows():
        desc = str(row['Descrizione']).strip()
        dare = float(row['Dare']) if pd.notna(row['Dare']) else 0.0
        avere = float(row['Avere']) if pd.notna(row['Avere']) else 0.0
        saldo = dare - avere

        # Salta voci escluse
        if any(desc.startswith(v) for v in VOCI_ESCLUSE):
            continue

        # Check retribuzioni
        for voce in VOCI_RETRIBUZIONI:
            if desc.startswith(voce) or desc == voce:
                retribuzioni += saldo
                dettaglio[desc] = {'categoria': 'RETRIBUZIONI', 'importo': saldo}
                break
        else:
            # Check oneri
            for voce in VOCI_ONERI:
                if desc.startswith(voce) or desc == voce:
                    oneri += saldo
                    dettaglio[desc] = {'categoria': 'ONERI', 'importo': saldo}
                    break

    # Estrai mese e anno dal dataframe
    mese = int(df['Mese'].iloc[0])
    anno = int(df['Anno'].iloc[0])

    return {
        'anno': anno,
        'mese': mese,
        'retribuzioni': round(retribuzioni, 2),
        'oneri': round(oneri, 2),
        'totale': round(retribuzioni + oneri, 2),
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
        'retribuzioni': 'sum',
        'oneri': 'sum',
        'totale': 'sum'
    }).reset_index()

    df_agg = df_agg.sort_values(['societa', 'anno', 'mese'])

    # Output
    output_path = Path('output')
    output_path.mkdir(exist_ok=True)

    # Pivot per RETRIBUZIONI
    pivot_retr = df_agg.pivot(index='mese', columns='societa', values='retribuzioni').fillna(0)
    pivot_retr.columns = [f'{c}_RETRIB' for c in pivot_retr.columns]

    # Pivot per ONERI
    pivot_oneri = df_agg.pivot(index='mese', columns='societa', values='oneri').fillna(0)
    pivot_oneri.columns = [f'{c}_ONERI' for c in pivot_oneri.columns]

    # Pivot per TOTALE
    pivot_tot = df_agg.pivot(index='mese', columns='societa', values='totale').fillna(0)
    pivot_tot.columns = [f'{c}_TOTALE' for c in pivot_tot.columns]

    # Combina tutto
    pivot = pd.concat([pivot_retr, pivot_oneri, pivot_tot], axis=1)
    # Riordina colonne: ORTI_RETRIB, ORTI_ONERI, ORTI_TOTALE, INTUR_RETRIB, etc.
    cols_order = []
    for soc in ['ORTI', 'INTUR']:
        for tipo in ['RETRIB', 'ONERI', 'TOTALE']:
            col = f'{soc}_{tipo}'
            if col in pivot.columns:
                cols_order.append(col)
    pivot = pivot[cols_order]

    # Aggiungi totali complessivi
    pivot['TOT_RETRIB'] = pivot[[c for c in pivot.columns if '_RETRIB' in c]].sum(axis=1)
    pivot['TOT_ONERI'] = pivot[[c for c in pivot.columns if '_ONERI' in c]].sum(axis=1)
    pivot['TOT_PERSONALE'] = pivot[[c for c in pivot.columns if '_TOTALE' in c]].sum(axis=1)

    # Dettaglio per file
    df_out[['societa', 'tipo', 'anno', 'mese', 'retribuzioni', 'oneri', 'totale', 'file']].to_csv(
        output_path / 'personale_dettaglio.csv', index=False
    )

    # Riepilogo mensile
    pivot.to_csv(output_path / 'personale_mensile.csv')

    print("\n" + "="*70)
    print("RIEPILOGO PERSONALE 2025 - RETRIBUZIONI vs ONERI")
    print("="*70)

    # Vista semplificata per società
    for soc in ['ORTI', 'INTUR']:
        retrib_col = f'{soc}_RETRIB'
        oneri_col = f'{soc}_ONERI'
        tot_col = f'{soc}_TOTALE'
        if tot_col in pivot.columns:
            print(f"\n{soc}:")
            print(f"  {'Mese':<6} {'Retribuzioni':>14} {'Oneri':>14} {'Totale':>14}")
            print(f"  {'-'*6} {'-'*14} {'-'*14} {'-'*14}")
            for mese in pivot.index:
                r = pivot.loc[mese, retrib_col] if retrib_col in pivot.columns else 0
                o = pivot.loc[mese, oneri_col] if oneri_col in pivot.columns else 0
                t = pivot.loc[mese, tot_col]
                print(f"  {mese:<6} €{r:>12,.2f} €{o:>12,.2f} €{t:>12,.2f}")

            tot_r = pivot[retrib_col].sum() if retrib_col in pivot.columns else 0
            tot_o = pivot[oneri_col].sum() if oneri_col in pivot.columns else 0
            tot_t = pivot[tot_col].sum()
            print(f"  {'-'*6} {'-'*14} {'-'*14} {'-'*14}")
            print(f"  {'TOT':<6} €{tot_r:>12,.2f} €{tot_o:>12,.2f} €{tot_t:>12,.2f}")

    print("\n" + "="*70)
    print("RIEPILOGO COMPLESSIVO")
    print("="*70)
    tot_retrib = pivot['TOT_RETRIB'].sum()
    tot_oneri = pivot['TOT_ONERI'].sum()
    tot_pers = pivot['TOT_PERSONALE'].sum()
    print(f"  RETRIBUZIONI TOTALI: €{tot_retrib:>12,.2f}")
    print(f"  ONERI TOTALI:        €{tot_oneri:>12,.2f}")
    print(f"  PERSONALE TOTALE:    €{tot_pers:>12,.2f}")
    print("="*70)


if __name__ == '__main__':
    main()
