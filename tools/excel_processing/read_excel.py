#!/usr/bin/env python3
import pandas as pd
import sys

try:
    # Leggi il file Excel
    file_path = "Piano Finanziario Jul 24 2025.xlsx"
    
    # Prova a leggere tutti i fogli
    xl_file = pd.ExcelFile(file_path)
    print(f"📊 Fogli disponibili: {xl_file.sheet_names}")
    print()
    
    # Leggi il primo foglio o il foglio principale
    for sheet_name in xl_file.sheet_names:
        print(f"=== FOGLIO: {sheet_name} ===")
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        
        # Mostra le prime righe per capire la struttura
        print("Prime 20 righe del foglio:")
        for idx, row in df.head(20).iterrows():
            # Stampa solo le celle non vuote
            non_empty = [(i, str(val)) for i, val in enumerate(row) if pd.notna(val) and str(val).strip()]
            if non_empty:
                print(f"Riga {idx}: {non_empty}")
        
        print()
        print("-" * 50)
        print()
        
        # Se è un foglio piccolo, mostra tutto
        if len(df) < 50:
            print("CONTENUTO COMPLETO:")
            for idx, row in df.iterrows():
                non_empty = [(i, str(val)) for i, val in enumerate(row) if pd.notna(val) and str(val).strip()]
                if non_empty:
                    print(f"Riga {idx}: {non_empty}")
        
        print("=" * 80)
        print()

except Exception as e:
    print(f"❌ Errore nella lettura del file: {e}")
    import traceback
    traceback.print_exc()