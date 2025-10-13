#!/usr/bin/env python3
import pandas as pd
import json
import sys

def get_category_mapping():
    """Mapping delle categorie con i loro subcategory_id dal database"""
    return {
        # REVENUE CATEGORIES
        "Entrate Hotel": "c1832baa-c125-401a-9ad8-0509ba445326",
        "Entrate Residence": "ebdc5cc8-fc3f-4556-ade0-e7339286817a", 
        "Entrate CVM": "d37b6d1a-39d3-49d5-8b96-47d57aed21dd",
        "Entrate Supermercato": "6f95ff64-759b-4ea7-99ad-59eaf052f720",
        "Rientro Sospesi": "bf6d3f4a-2ee3-405a-8eba-870999168297",
        "Caparre Intur": "1e60606d-977c-4e0f-a9bb-4e5b755d974a",
        
        # EXPENSE CATEGORIES  
        "Salari e Stipendi": "cf210edd-c4cc-45b3-bb3c-b8608f3fc369",
        "Utenze": "2a89ab53-05dd-497d-b355-48a1d0eafe0e",
        "Materie Prime/Consumo": "eabf8d77-8847-42ff-b0bd-f997fed1a36a",
        "Tasse e Imposte": "e0bbef20-54e8-473d-a38a-6d14cce1dbd8",
        "Commissioni Portali": "d84a5d8f-8553-4903-8900-e8c79a546ca8",
        "Mutui e Finanziamenti": "6c12b9d8-c0e6-4b3f-9bcf-b82a35d51b91",
        "Consulenze": "53acc9ad-423e-4537-bf6e-7e4c8a3a88bf",
        "Godimento Beni di Terzi": "61d2e60f-b869-4ca2-86d3-9e5d3911a7a4",
        "Canoni e servizi": "ea99dbff-df45-4201-a6e9-25f9d4d0eb25",
        "Varie ed Eventuali": "93761931-cbeb-4dd7-b65d-ba366d1e1f1b"
    }

def extract_complete_excel_data():
    """Estrae TUTTI i dati dal Piano Finanziario Excel, incluse le Entrate Hotel"""
    
    try:
        file_path = "Piano Finanziario Jul 24 2025.xlsx"
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
        
        # Categorie da cercare (incluso con possibili variazioni di spazi)
        category_variations = {
            # ENTRATE - con possibili variazioni di spazio
            "Entrate Hotel ": "Entrate Hotel",        # Excel ha spazio finale
            "Entrate Hotel": "Entrate Hotel",         # Senza spazio
            "Entrate Residence": "Entrate Residence", 
            "Entrate CVM": "Entrate CVM",
            "Entrate Supermercato": "Entrate Supermercato",
            "Rientro Sospesi": "Rientro Sospesi",
            "Caparre Intur": "Caparre Intur",
            
            # USCITE - con possibili variazioni di spazio  
            "Salari e Stipendi": "Salari e Stipendi",
            "Utenze": "Utenze",
            "Materie Prime/Consumo": "Materie Prime/Consumo",
            "Tasse e Imposte": "Tasse e Imposte",
            "Commissioni Portali": "Commissioni Portali",
            "Mutui e Finaziamenti": "Mutui e Finanziamenti",  # Excel ha questa grafia
            "Mutui e Finanaziamenti": "Mutui e Finanziamenti", # Possibile typo in Excel
            "Consulenze": "Consulenze",
            "Godimento Beni di Terzi": "Godimento Beni di Terzi",
            "Gofimento Beni di Terzi": "Godimento Beni di Terzi", # Possibile typo
            "Canoni e servizi": "Canoni e servizi",
            "Varie ed Eventuali": "Varie ed Eventuali",
            " Varie ed Eventuali": "Varie ed Eventuali",  # Con spazio iniziale
            "Variee ed Eventuali": "Varie ed Eventuali"   # Possibile typo
        }
        
        entries_data = []
        category_mapping = get_category_mapping()
        
        print("🔍 Analizzando il file Excel...")
        
        # Processa ogni riga del dataframe
        for idx, row in df.iterrows():
            if pd.notna(row[0]):
                category_name_raw = str(row[0]).strip()
                
                # Cerca nelle variazioni di nomi
                if category_name_raw in category_variations:
                    category_name = category_variations[category_name_raw]
                    
                    # Verifica che la categoria sia nel nostro mapping
                    if category_name in category_mapping:
                        subcategory_id = category_mapping[category_name]
                        
                        # Estrai valori per ogni mese
                        for col, month in months.items():
                            if col < len(row) and pd.notna(row[col]):
                                try:
                                    value = float(row[col])
                                    if value != 0:
                                        entries_data.append({
                                            "category_name": category_name,
                                            "subcategory_id": subcategory_id,
                                            "month": month,
                                            "year": 2025,
                                            "value": value,
                                            "is_projection": True,
                                            "notes": f"{category_name} - proiezione Excel Piano Finanziario"
                                        })
                                except (ValueError, TypeError):
                                    continue
        
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
            months_list = sorted(set(e['month'] for e in entries))
            print(f"  {cat}: {months_with_data} mesi, totale €{total:,.2f} (mesi: {months_list})")
        
        return entries_data
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return []

def generate_sql_inserts(entries_data):
    """Genera gli statement SQL per inserire tutti i dati"""
    
    if not entries_data:
        return ""
    
    sql_statements = []
    
    # Raggruppa entries per ottimizzare gli insert
    batch_size = 50
    for i in range(0, len(entries_data), batch_size):
        batch = entries_data[i:i+batch_size]
        
        values = []
        for entry in batch:
            values.append(f"('{entry['subcategory_id']}', {entry['year']}, {entry['month']}, {entry['value']}, {entry['is_projection']}, '{entry['notes']}')")
        
        sql = f"""
-- Inserimento batch {i//batch_size + 1} - {len(batch)} entries
INSERT INTO entries (subcategory_id, year, month, value, is_projection, notes) VALUES
{',\n'.join(values)};
"""
        sql_statements.append(sql)
    
    return '\n'.join(sql_statements)

if __name__ == "__main__":
    print("🚀 Avvio estrazione completa dati Excel...")
    data = extract_complete_excel_data()
    
    if data:
        # Salva in JSON per debug
        with open("complete_excel_data.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Genera SQL
        sql = generate_sql_inserts(data)
        with open("insert_statements.sql", 'w', encoding='utf-8') as f:
            f.write(sql)
        
        print(f"\n✅ Processo completato!")
        print(f"📊 {len(data)} entries pronte per l'inserimento")
        print(f"💾 File generati:")
        print(f"   - complete_excel_data.json (dati estratti)")
        print(f"   - insert_statements.sql (SQL per inserimento)")
        
    else:
        print("❌ Nessun dato estratto.")