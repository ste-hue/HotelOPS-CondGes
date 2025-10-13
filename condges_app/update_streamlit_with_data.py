#!/usr/bin/env python3
"""
CONDGES V4.0 - Aggiornamento Streamlit App con dati certi
"""

import pandas as pd
import json
import re
import os

print("=" * 80)
print("📊 CONDGES V4.0 - INSERIMENTO DATI CERTI IN STREAMLIT")
print("=" * 80)

# ============================================================================
# 1. ESTRAZIONE PERSONALE DA CSV (TUTTI I FORMATI)
# ============================================================================

def estrai_personale_completo():
    """Estrae personale gestendo tutti i formati CSV"""
    csv_path = "../data/uscite/personale/costopersonale/PC_csv/ORTI"
    risultati = {}
    
    for file in os.listdir(csv_path):
        if file.endswith('.csv'):
            mese_num = int(file.split('_')[2])  # ORT_PC_03_2025.pdf.csv → 03
            
            with open(os.path.join(csv_path, file), 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Prova diversi pattern
                patterns = [
                    r'\*\*\*,Totale Conti Economici[",]+([\d.,]+)[",]+([\d.,]+)[",]+([\d.,]+)',
                    r',\*\*\* Totale Conti Economici[",]+([\d.,]+)[",]+([\d.,]+)[",]+([\d.,]+)',
                    r',\*\*\* Totale Conti,Economici[",]+([\d.,]+)[",]+([\d.,]+)[",]+([\d.,]+)',
                    r'Totale Conti Economici ([\d.,]+) ([\d.,]+) ([\d.,]+)'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, content)
                    if match:
                        saldo = match.group(3)
                        # Converti formato italiano
                        saldo = saldo.replace('"', '').replace('.', '').replace(',', '.')
                        saldo = float(saldo)
                        risultati[mese_num] = saldo
                        break
    
    return risultati

personale_dati = estrai_personale_completo()

print("\n📁 PERSONALE ESTRATTO DA CSV:")
print("-" * 40)
mesi_nomi = ['', 'Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic']
for mese, valore in sorted(personale_dati.items()):
    print(f"  {mesi_nomi[mese]}: €{valore:,.0f}")

# ============================================================================
# 2. DATI CERTI COMPLETI
# ============================================================================

print("\n✅ DATI CERTI DISPONIBILI:")
print("-" * 40)

dati_certi_2025 = {
    "ORTI": {
        "PERSONALE": {
            1: 0,  # Gen - da proiettare
            2: 0,  # Feb - da proiettare
            3: personale_dati.get(3, 30254),
            4: personale_dati.get(4, 91363),
            5: personale_dati.get(5, 123816),
            6: personale_dati.get(6, 134498),
            7: personale_dati.get(7, 142254),
            8: personale_dati.get(8, 139050),
            9: 100000,  # Set - proiezione da 2024
            10: 70000,  # Ott - proiezione da 2024
            11: 50000,  # Nov - proiezione da 2024
            12: 45000   # Dic - proiezione da 2024
        },
        "MUTUI": {
            "MPS": [12135] * 18,  # 18 mesi
            "Intesa": [10793] * 18
        },
        "RICAVI_2024_BASE": {
            1: 71000, 2: 71000, 3: 106000, 4: 212000, 5: 530000, 6: 707000,
            7: 814000, 8: 757000, 9: 711000, 10: 444000, 11: 106000, 12: 71000
        }
    },
    "INTUR": {
        "FITTI": {
            "Hotel": [122000] * 18,
            "Residence": [120000] * 18
        },
        "MUTUI": {
            "Sella": [50000] * 12 + [0] * 6,  # Finisce Dic 2025
            "Intesa": [8500] * 18,
            "MPS": [1059] * 18
        },
        "PERSONALE_STIMATO": [15000] * 18
    }
}

# ============================================================================
# 3. GENERAZIONE CODICE PER STREAMLIT
# ============================================================================

print("\n📝 CODICE DA INSERIRE IN STREAMLIT:")
print("-" * 40)

streamlit_code = '''
# Da inserire nella funzione create_empty_dataframe() di streamlit_app.py

def load_certain_data(df, company='orti'):
    """Carica i dati certi nel DataFrame"""
    
    if company == 'orti':
        # PERSONALE REALE
        personale_certi = {
            'Mar 2025': 30254, 'Apr 2025': 91363, 'Mag 2025': 123816,
            'Giu 2025': 134498, 'Lug 2025': 142254, 'Ago 2025': 139050
        }
        
        for col, val in personale_certi.items():
            if col in df.columns:
                df.loc['PERSONALE', col] = val
        
        # RICAVI PROIEZIONE +10%
        ricavi_2024 = [71000, 71000, 106000, 212000, 530000, 707000, 
                       814000, 757000, 711000, 444000, 106000, 71000]
        
        for i, val in enumerate(ricavi_2024):
            col = df.columns[i] if i < len(df.columns) else None
            if col and '2025' in col:
                # Distribuzione per asset
                df.loc['Hotel (76 camere)', col] = val * 0.75 * 1.1
                df.loc['Residence Angelina (19 unità)', col] = val * 0.15 * 1.1
                df.loc['CVM (8 appartamenti)', col] = val * 0.08 * 1.1
                df.loc['Supermercato', col] = 25620  # Fisso
    
    else:  # INTUR
        # FITTI FISSI
        for col in df.columns:
            df.loc['Fitto Hotel', col] = 122000
            df.loc['Fitto Angelina Residence', col] = 120000
            df.loc['Entrate Farmacia', col] = 3750
        
        # PERSONALE INTUR
        for col in df.columns:
            df.loc['PERSONALE', col] = 15000
    
    return df
'''

print(streamlit_code)

# ============================================================================
# 4. EXPORT PER EXCEL
# ============================================================================

print("\n💾 GENERAZIONE FILE EXCEL CON DATI CERTI:")
print("-" * 40)

# Crea DataFrame completo ORTI
mesi_2025 = ['Gen 25', 'Feb 25', 'Mar 25', 'Apr 25', 'Mag 25', 'Giu 25',
             'Lug 25', 'Ago 25', 'Set 25', 'Ott 25', 'Nov 25', 'Dic 25']
mesi_2026 = ['Gen 26', 'Feb 26', 'Mar 26', 'Apr 26', 'Mag 26', 'Giu 26']

columns = mesi_2025 + mesi_2026

# ORTI DataFrame
orti_data = {
    'Voce': [
        'RICAVI Hotel', 'RICAVI Residence', 'RICAVI CVM', 'RICAVI Supermercato',
        'PERSONALE', 'PRODUZIONE', 'COMMERCIALE', 'GESTIONE',
        'Mutuo MPS', 'Mutuo Intesa', 'IMU/Tasse', 'Canoni/Utenze'
    ]
}

# Popola con dati certi e proiezioni
for i, col in enumerate(columns):
    mese_idx = (i % 12) + 1
    anno = 2025 if i < 12 else 2026
    
    # Ricavi (proiezione +10% su 2024)
    if i < 12:
        base = dati_certi_2025['ORTI']['RICAVI_2024_BASE'][mese_idx]
        orti_data[col] = [
            base * 0.75 * 1.1,  # Hotel
            base * 0.15 * 1.1,  # Residence  
            base * 0.08 * 1.1,  # CVM
            25620,  # Supermercato
            dati_certi_2025['ORTI']['PERSONALE'].get(mese_idx, 0),
            0,  # Produzione - da inserire
            0,  # Commerciale - da inserire
            0,  # Gestione - da inserire
            12135,  # Mutuo MPS
            10793,  # Mutuo Intesa
            0,  # IMU - da inserire
            0   # Canoni - da inserire
        ]
    else:
        # 2026 - proiezioni base
        orti_data[col] = [0] * 12

df_orti = pd.DataFrame(orti_data)
df_orti.to_excel('ORTI_DATI_CERTI.xlsx', index=False)

print("✅ File salvato: ORTI_DATI_CERTI.xlsx")

# ============================================================================
# 5. RIEPILOGO FINALE
# ============================================================================

print("\n📊 RIEPILOGO DATI DA COMPLETARE:")
print("-" * 40)

da_completare = [
    "❓ PERSONALE Gen-Feb 2025 (ORTI)",
    "❓ PERSONALE Set-Dic 2025 (ORTI) - ora proiezione",
    "❓ PERSONALE INTUR tutti i mesi - verificare PDF",
    "❓ PRODUZIONE - verificare fornitoricosto.xlsx",
    "❓ COMMERCIALE - verificare OTA da banca",
    "❓ IMU/TARI - cercare importi nei documenti",
    "❓ Canoni/Utenze base - verificare contratti",
    "❓ Ricavi effettivi Gen-Ago 2025 - verificare PMS/bilancini"
]

for item in da_completare:
    print(f"  {item}")

print("\n✅ SCRIPT COMPLETATO!")
print("=" * 80)
