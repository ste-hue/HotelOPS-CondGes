#!/usr/bin/env python3
import json
import os
from supabase import create_client, Client

def load_supabase_client():
    """Carica il client Supabase"""
    url = "https://fgbaqpzipjmjzpuhxwkx.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZnYmFxcHppcGptanpwdWh4d2t4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzE5Mzg2NjAsImV4cCI6MjA0NzUxNDY2MH0.1rLKb6c_2R6VFGZ8QGAaXnFCvJU8TxEGhqbQzaKHJdM"
    return create_client(url, key)

def insert_august_data():
    """Inserisce i dati di agosto 2025 nel database"""
    
    # Carica i dati dall'Excel
    with open('excel_data.json', 'r') as f:
        data = json.load(f)
    
    # Filtra solo agosto 2025
    august_data = [d for d in data if d['month'] == 8 and d['year'] == 2025]
    
    if not august_data:
        print("❌ Nessun dato di agosto trovato")
        return
    
    print(f"📊 Trovati {len(august_data)} entries per agosto 2025")
    
    # Connetti a Supabase
    supabase = load_supabase_client()
    
    # Inserisci ogni entry
    success_count = 0
    error_count = 0
    
    for entry in august_data:
        try:
            # Trova la categoria
            category_response = supabase.table('categories').select('id').eq('name', entry['category_name']).execute()
            
            if not category_response.data:
                print(f"⚠️  Categoria non trovata: {entry['category_name']}")
                continue
            
            category_id = category_response.data[0]['id']
            
            # Trova la subcategoria (assumiamo 'Main' come default)
            subcategory_response = supabase.table('subcategories').select('id').eq('category_id', category_id).eq('name', 'Main').execute()
            
            if not subcategory_response.data:
                print(f"⚠️  Subcategoria 'Main' non trovata per: {entry['category_name']}")
                continue
            
            subcategory_id = subcategory_response.data[0]['id']
            
            # Inserisci l'entry
            insert_data = {
                'subcategory_id': subcategory_id,
                'year': entry['year'],
                'month': entry['month'],
                'value': entry['value'],
                'is_projection': entry['is_projection'],
                'notes': entry['notes']
            }
            
            result = supabase.table('entries').insert(insert_data).execute()
            
            if result.data:
                success_count += 1
                print(f"✅ {entry['category_name']}: €{entry['value']:,.2f}")
            else:
                error_count += 1
                print(f"❌ Errore inserimento {entry['category_name']}")
                
        except Exception as e:
            error_count += 1
            print(f"❌ Errore {entry['category_name']}: {e}")
    
    print(f"\n📊 RISULTATO:")
    print(f"✅ Inseriti: {success_count}")
    print(f"❌ Errori: {error_count}")
    
    # Verifica finale
    print(f"\n🔍 VERIFICA FINALE:")
    try:
        # Calcola totali
        result = supabase.rpc('get_month_cash_flow', {'p_year': 2025, 'p_month': 8}).execute()
        cash_flow = result.data if result.data else 0
        
        result = supabase.rpc('get_total_bank_balance', {'p_year': 2025, 'p_month': 7}).execute()
        prev_balance = result.data if result.data else 0
        
        projected_balance = prev_balance + cash_flow
        
        print(f"💰 Cash Flow Agosto: €{cash_flow:,.2f}")
        print(f"🏦 Saldo Luglio: €{prev_balance:,.2f}")
        print(f"🔮 Saldo Previsto Agosto: €{projected_balance:,.2f}")
        
    except Exception as e:
        print(f"❌ Errore verifica: {e}")

if __name__ == "__main__":
    insert_august_data()