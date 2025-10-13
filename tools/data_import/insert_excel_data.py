#!/usr/bin/env python3
import pandas as pd
import json
import sys

def extract_excel_data():
    """Estrae tutti i dati dal Piano Finanziario Excel"""
    
    try:
        # Leggi il foglio principale
        file_path = "ORTI Piano Finanziario Jul 24 2025 (1).xlsx"
        df = pd.read_excel(file_path, sheet_name="Piano Finanziario", header=None)
        
        # Mappa dei mesi (colonne 2-13 = Gen-Dic 2025)
        months = {
            2: 1,   # Gennaio
            3: 2,   # Febbraio
            4: 3,   # Marzo
            5: 4,   # Aprile
            6: 5,   # Maggio
            7: 6,   # Giugno
            8: 7,   # Luglio
            9: 8,   # Agosto
            10: 9,  # Settembre
            11: 10, # Ottobre
            12: 11, # Novembre
            13: 12  # Dicembre
        }
        
        # Dati da inserire
        entries_data = []
        
        # ENTRATE (Revenue)
        revenue_categories = {
            "Entrate Hotel": "Entrate Hotel",  # Rimosso spazio finale
            "Entrate Residence": "Entrate Residence", 
            "Entrate CVM": "Entrate CVM",
            "Entrate Supermercato": "Entrate Supermercato",
            "Rientro Sospesi": "Rientro Sospesi",
            "Caparre Intur": "Caparre Intur"
        }
        
        # USCITE (Expense)
        expense_categories = {
            "Salari e Stipendi": "Salari e Stipendi",
            "Utenze": "Utenze",
            "Materie Prime/Consumo": "Materie Prime/Consumo",
            "Tasse e Imposte": "Tasse e Imposte",
            "Commissioni Portali": "Commissioni Portali",
            "Mutui e Finaziamenti": "Mutui e Finanziamenti",
            "Consulenze": "Consulenze",
            "Godimento Beni di Terzi": "Godimento Beni di Terzi",
            "Canoni e servizi": "Canoni e servizi",
            " Varie ed Eventuali": "Varie ed Eventuali"
        }
        
        # Processa ogni riga del dataframe
        for idx, row in df.iterrows():
            if pd.notna(row[0]):
                category_name_raw = str(row[0]).strip()
                
                # Cerca nelle entrate
                if category_name_raw in revenue_categories:
                    category_name = revenue_categories[category_name_raw]
                    category_type = "revenue"
                    
                    # Estrai valori per ogni mese
                    for col, month in months.items():
                        if col < len(row) and pd.notna(row[col]):
                            value = float(row[col])
                            if value != 0:
                                entries_data.append({
                                    "category_name": category_name,
                                    "category_type": category_type,
                                    "month": month,
                                    "year": 2025,
                                    "value": value,
                                    "is_projection": True,
                                    "notes": f"{category_name} - proiezione da Excel"
                                })
                
                # Cerca nelle uscite
                elif category_name_raw in expense_categories:
                    category_name = expense_categories[category_name_raw]
                    category_type = "expense"
                    
                    # Estrai valori per ogni mese
                    for col, month in months.items():
                        if col < len(row) and pd.notna(row[col]):
                            value = float(row[col])
                            if value != 0:
                                entries_data.append({
                                    "category_name": category_name,
                                    "category_type": category_type,
                                    "month": month,
                                    "year": 2025,
                                    "value": value,
                                    "is_projection": True,
                                    "notes": f"{category_name} - proiezione da Excel"
                                })
        
        print(f"📊 Estratti {len(entries_data)} entries dai dati Excel")
        
        # Raggruppa per categoria per debug
        by_category = {}
        for entry in entries_data:
            cat = entry['category_name']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(entry)
        
        print("\n📋 Riepilogo per categoria:")
        for cat, entries in by_category.items():
            total = sum(e['value'] for e in entries)
            months_with_data = len(entries)
            print(f"  {cat}: {months_with_data} mesi, totale €{total:,.2f}")
        
        return entries_data
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return []

def save_to_json(data, filename="excel_data.json"):
    """Salva i dati in JSON per debug"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"💾 Dati salvati in {filename}")

if __name__ == "__main__":
    data = extract_excel_data()
    if data:
        save_to_json(data)
        print(f"\n✅ Processo completato. {len(data)} entries pronte per l'inserimento.")
    else:
        print("❌ Nessun dato estratto.")