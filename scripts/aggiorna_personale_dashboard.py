#!/usr/bin/env python3
"""
Aggiorna i dashboard CSV con i dati personale corretti dai Prospetti Contabili.
Mette i valori estratti dove disponibili, segna come mancanti dove non ci sono dati.
"""

import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path('output')

MESI_NOME = {
    1: 'Gennaio', 2: 'Febbraio', 3: 'Marzo', 4: 'Aprile',
    5: 'Maggio', 6: 'Giugno', 7: 'Luglio', 8: 'Agosto',
    9: 'Settembre', 10: 'Ottobre', 11: 'Novembre', 12: 'Dicembre'
}

# Mesi con dati PC disponibili
ORTI_MESI_DISPONIBILI = [3, 4, 5, 6, 7, 8]  # Mar-Ago
INTUR_MESI_DISPONIBILI = [1, 2, 3, 4, 5, 6, 7, 8]  # Gen-Ago

def main():
    # Carica personale estratto
    personale = pd.read_csv(OUTPUT_DIR / 'personale_mensile.csv')

    # === ORTI ===
    print("Aggiornamento ORTI_dashboard...")
    orti_df = pd.read_csv(OUTPUT_DIR / 'ORTI_dashboard_semplificato.csv')

    # Reset colonne personale
    orti_df['RETRIBUZIONI'] = 0.0
    orti_df['ONERI'] = 0.0
    orti_df['PERSONALE'] = 0.0
    orti_df['NOTE'] = ''

    for idx, row in orti_df.iterrows():
        mese_nome = row['Mese']
        mese_num = [k for k, v in MESI_NOME.items() if v == mese_nome]
        if not mese_num:
            continue
        mese_num = mese_num[0]

        if mese_num in ORTI_MESI_DISPONIBILI:
            pers_row = personale[personale['mese'] == mese_num]
            if not pers_row.empty:
                orti_df.loc[idx, 'RETRIBUZIONI'] = pers_row['ORTI_RETRIB'].values[0]
                orti_df.loc[idx, 'ONERI'] = pers_row['ORTI_ONERI'].values[0]
                orti_df.loc[idx, 'PERSONALE'] = pers_row['ORTI_TOTALE'].values[0]
                orti_df.loc[idx, 'NOTE'] = 'PC'
        elif mese_num < 3:
            # Gen-Feb ORTI non operativo
            orti_df.loc[idx, 'NOTE'] = 'Non operativo'
        else:
            # Set-Dic mancanti
            orti_df.loc[idx, 'NOTE'] = 'MANCA PC'

    # Ricalcola TOT_COSTI e EBITDA
    orti_df['TOT_COSTI'] = orti_df['COSTI_FISSI'] + orti_df['COSTI_VARIABILI'] + orti_df['PERSONALE']
    orti_df['EBITDA'] = orti_df['TOT_RICAVI'] - orti_df['TOT_COSTI']

    # Riordina colonne
    cols = ['Mese', 'HOTEL', 'ANGELINA', 'CVM', 'F&B', 'SPIAGGIA', 'ALTRI_RICAVI', 'TOT_RICAVI',
            'COSTI_FISSI', 'COSTI_VARIABILI', 'RETRIBUZIONI', 'ONERI', 'PERSONALE', 'TOT_COSTI', 'EBITDA', 'NOTE']
    orti_df = orti_df[cols]
    orti_df.to_csv(OUTPUT_DIR / 'ORTI_dashboard_semplificato.csv', index=False)
    print(f"  Salvato: ORTI_dashboard_semplificato.csv")

    # === INTUR ===
    print("\nAggiornamento INTUR_dashboard...")
    intur_df = pd.read_csv(OUTPUT_DIR / 'INTUR_dashboard_semplificato.csv')

    # Reset colonne personale
    intur_df['RETRIBUZIONI'] = 0.0
    intur_df['ONERI'] = 0.0
    intur_df['PERSONALE'] = 0.0
    intur_df['NOTE'] = ''

    for idx, row in intur_df.iterrows():
        mese_nome = row['Mese']
        mese_num = [k for k, v in MESI_NOME.items() if v == mese_nome]
        if not mese_num:
            continue
        mese_num = mese_num[0]

        if mese_num in INTUR_MESI_DISPONIBILI:
            pers_row = personale[personale['mese'] == mese_num]
            if not pers_row.empty:
                intur_df.loc[idx, 'RETRIBUZIONI'] = pers_row['INTUR_RETRIB'].values[0]
                intur_df.loc[idx, 'ONERI'] = pers_row['INTUR_ONERI'].values[0]
                intur_df.loc[idx, 'PERSONALE'] = pers_row['INTUR_TOTALE'].values[0]
                intur_df.loc[idx, 'NOTE'] = 'PC'
        else:
            # Set-Dic mancanti
            intur_df.loc[idx, 'NOTE'] = 'MANCA PC'

    # Ricalcola TOT_COSTI e EBITDA
    intur_df['TOT_COSTI'] = intur_df['COSTI_FISSI'] + intur_df['COSTI_VARIABILI'] + intur_df['PERSONALE']
    intur_df['EBITDA'] = intur_df['TOT_RICAVI'] - intur_df['TOT_COSTI']

    # Riordina colonne
    intur_df = intur_df[cols]
    intur_df.to_csv(OUTPUT_DIR / 'INTUR_dashboard_semplificato.csv', index=False)
    print(f"  Salvato: INTUR_dashboard_semplificato.csv")

    # === STAMPA RIEPILOGO ===
    print("\n" + "="*80)
    print("RIEPILOGO PERSONALE NEI DASHBOARD")
    print("="*80)

    print("\nORTI:")
    print(orti_df[['Mese', 'RETRIBUZIONI', 'ONERI', 'PERSONALE', 'NOTE']].to_string(index=False))
    tot_orti = orti_df[orti_df['NOTE'] == 'PC']['PERSONALE'].sum()
    print(f"\nTotale Personale ORTI (con dati PC): €{tot_orti:,.2f}")

    print("\n" + "-"*80)
    print("\nINTUR:")
    print(intur_df[['Mese', 'RETRIBUZIONI', 'ONERI', 'PERSONALE', 'NOTE']].to_string(index=False))
    tot_intur = intur_df[intur_df['NOTE'] == 'PC']['PERSONALE'].sum()
    print(f"\nTotale Personale INTUR (con dati PC): €{tot_intur:,.2f}")

    print("\n" + "="*80)
    print(f"TOTALE PERSONALE CONSOLIDATO (con dati PC): €{tot_orti + tot_intur:,.2f}")
    print("="*80)

    # Elenca mancanti
    print("\n⚠️  FILE PC MANCANTI:")
    print("   ORTI: Settembre, Ottobre, Novembre, Dicembre")
    print("   INTUR: Settembre, Ottobre, Novembre, Dicembre")


if __name__ == '__main__':
    main()
