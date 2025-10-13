#!/usr/bin/env python3
"""
CONDGES V4.0 - Script per caricare tutti i dati CERTI disponibili
"""

import pandas as pd
import json
import os
from datetime import datetime

print("=" * 80)
print("📊 CONDGES V4.0 - RESOCONTO DATI CERTI E DISPONIBILI")
print("=" * 80)

# ============================================================================
# 1. DATI CERTI CHE ABBIAMO
# ============================================================================

dati_certi = {
    "MUTUI": {
        "ORTI": {
            "MPS_3.5M": {
                "mensile": 12135,
                "annuale": 145618,
                "scadenza": "2039",
                "status": "✅ CERTO"
            },
            "Intesa_1.4M": {
                "mensile": 10793,
                "annuale": 129518,
                "scadenza": "2028",
                "status": "✅ CERTO"
            }
        },
        "INTUR": {
            "Sella_600K": {
                "mensile": 50000,
                "annuale": 600000,
                "scadenza": "Dic 2025 (balloon)",
                "status": "✅ CERTO"
            },
            "Intesa_1M": {
                "mensile": 8500,
                "annuale": 102000,
                "scadenza": "2031",
                "status": "✅ CERTO"
            },
            "MPS_75K": {
                "mensile": 1059,
                "annuale": 12706,
                "scadenza": "2030",
                "status": "✅ CERTO"
            }
        }
    },
    
    "PERSONALE_2025": {
        "ORTI": {
            "Marzo": 30254,
            "Aprile": 91363,
            "Maggio": 123816,
            "Giugno": 134498,
            "Luglio": 142254,
            "Agosto": 139050,
            "status": "✅ CERTO da CSV"
        },
        "INTUR": {
            "status": "❓ DA VERIFICARE nei PDF"
        }
    },
    
    "RICAVI_2024": {
        "ORTI": {
            "Settembre": 711000,
            "Ottobre": 444000,
            "status": "✅ CERTO da bilancini"
        }
    },
    
    "FITTI": {
        "INTUR_riceve": {
            "Hotel": 122000,  # mensile
            "Residence": 120000,  # mensile
            "status": "✅ CERTO contrattuale"
        }
    }
}

# ============================================================================
# 2. DATI CHE DOBBIAMO VERIFICARE/ESTRARRE
# ============================================================================

dati_da_verificare = {
    "PERSONALE": {
        "Gen-Feb 2025": "❓ Non abbiamo CSV, verificare se ci sono PDF",
        "Set-Dic 2025": "📅 Proiezione basata su 2024 + stagionalità",
        "2026": "📅 Proiezione basata su 2025",
        "INTUR tutti": "❓ Verificare PDF INTUR se esistono"
    },
    
    "RICAVI_OPERATIVI": {
        "Gen-Ago 2025": "❓ Verificare se abbiamo dati PMS o bilancini",
        "Set-Dic 2025": "📅 Proiezione +10% su 2024",
        "2026": "📅 Proiezione basata su 2025"
    },
    
    "COSTI_PRODUZIONE": {
        "Fornitori": "❓ Verificare file fornitoricosto.xlsx",
        "Materiali": "❓ Verificare categorie da uscite_complete",
        "Pattern stagionale": "📅 Basare su 2024"
    },
    
    "COSTI_COMMERCIALI": {
        "OTA (Expedia/Booking)": "❓ Verificare categorizzazione banca",
        "Marketing": "❓ Verificare spese pubblicitarie",
        "Pattern": "📅 3-5% dei ricavi"
    },
    
    "GESTIONE_FINANZA": {
        "IMU": "❓ Verificare importo annuale",
        "Tasse immobiliari": "❓ Verificare TARI, etc.",
        "Utenze base": "❓ Verificare contratti fissi",
        "Assicurazioni": "❓ Verificare polizze"
    }
}

# ============================================================================
# 3. ESTRAZIONE DATI PERSONALE DA CSV
# ============================================================================

print("\n📁 ESTRAZIONE DATI PERSONALE DA CSV:")
print("-" * 40)

personale_csv = {}
csv_path = "data/uscite/personale/costopersonale/PC_csv/ORTI"

for file in os.listdir(csv_path):
    if file.endswith('.csv'):
        mese = file.split('_')[2]  # ORT_PC_03_2025.pdf.csv → 03
        
        try:
            df = pd.read_csv(os.path.join(csv_path, file))
            # Cerca riga "Totale Conti Economici"
            totale_row = df[df.iloc[:, 0].str.contains('***', na=False)]
            if not totale_row.empty:
                valore = totale_row.iloc[0, 4]  # Colonna Saldo
                # Converti formato italiano
                if isinstance(valore, str):
                    valore = valore.replace('.', '').replace(',', '.')
                    valore = float(valore)
                personale_csv[f"Mese_{mese}"] = valore
                print(f"  ✅ Mese {mese}: €{valore:,.0f}")
        except Exception as e:
            print(f"  ❌ Errore mese {mese}: {e}")

# ============================================================================
# 4. AZIONI NECESSARIE
# ============================================================================

print("\n🎯 AZIONI NECESSARIE PER COMPLETARE I DATI:")
print("-" * 40)

azioni = [
    "1. 📄 Verificare PDF personale INTUR (se esistono)",
    "2. 📊 Estrarre ricavi Gen-Ago 2025 da bilancini o PMS",
    "3. 💼 Verificare file fornitoricosto.xlsx per produzione",
    "4. 🏦 Verificare categorizzazione banca per OTA/commerciali",
    "5. 🏢 Cercare importi IMU/TARI nei documenti",
    "6. 📈 Applicare proiezioni per Set-Dic 2025 basate su 2024",
    "7. 📅 Proiettare 2026 basandosi su pattern 2025"
]

for azione in azioni:
    print(f"  {azione}")

# ============================================================================
# 5. EXPORT DATI CERTI IN JSON
# ============================================================================

output_data = {
    "timestamp": datetime.now().isoformat(),
    "dati_certi": dati_certi,
    "personale_csv_estratto": personale_csv,
    "dati_da_verificare": dati_da_verificare,
    "azioni_necessarie": azioni
}

output_file = "DATI_CERTI_CONDGES.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"\n💾 Dati salvati in: {output_file}")

# ============================================================================
# 6. GENERAZIONE DATAFRAME PER STREAMLIT
# ============================================================================

print("\n📊 GENERAZIONE DATI PER STREAMLIT APP:")
print("-" * 40)

# Crea DataFrame con dati certi
mesi = ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic']

# ORTI 2025
orti_2025 = pd.DataFrame({
    'Mese': mesi,
    'Personale': [0, 0, 30254, 91363, 123816, 134498, 142254, 139050, 0, 0, 0, 0],
    'Mutuo_MPS': [12135] * 12,
    'Mutuo_Intesa': [10793] * 12,
    'Status_Personale': ['❓', '❓', '✅', '✅', '✅', '✅', '✅', '✅', '📅', '📅', '📅', '📅']
})

# INTUR 2025
intur_2025 = pd.DataFrame({
    'Mese': mesi,
    'Fitto_Hotel': [122000] * 12,
    'Fitto_Residence': [120000] * 12,
    'Mutuo_Sella': [50000] * 12,  # Finisce a Dic
    'Mutuo_Intesa': [8500] * 12,
    'Mutuo_MPS': [1059] * 12
})

print("✅ DataFrames pronti per Streamlit")
print(f"  • ORTI: {len(orti_2025)} mesi")
print(f"  • INTUR: {len(intur_2025)} mesi")

# Salva anche come CSV per facile import
orti_2025.to_csv('ORTI_2025_DATI_CERTI.csv', index=False)
intur_2025.to_csv('INTUR_2025_DATI_CERTI.csv', index=False)

print("\n✅ RESOCONTO COMPLETATO!")
print("=" * 80)
