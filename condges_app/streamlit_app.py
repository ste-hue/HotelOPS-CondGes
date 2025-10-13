#!/usr/bin/env python3
"""
CONDGES V4.0 - Streamlit Dashboard
Sistema completo per gestione finanziaria ORTI/INTUR con confronto 2024 ed export Excel
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, date
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO

# Page config
st.set_page_config(
    page_title="CONDGES V4.0 Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .positive { color: #28a745; }
    .negative { color: #dc3545; }
    .warning { color: #ffc107; }
    div[data-testid="metric-container"] {
        background-color: rgba(28, 131, 225, 0.1);
        border: 2px solid rgba(28, 131, 225, 0.2);
        padding: 5px 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_orti' not in st.session_state:
    st.session_state.data_orti = None
if 'data_intur' not in st.session_state:
    st.session_state.data_intur = None
if 'data_2024' not in st.session_state:
    # Dati 2024 di riferimento
    st.session_state.data_2024 = {
        'orti': {
            'ricavi': [71000, 71000, 106000, 212000, 530000, 707000, 814000, 757000, 711000, 444000, 106000, 71000],
            'personale': [40000, 40000, 45000, 55000, 65000, 80000, 120000, 130000, 100000, 70000, 50000, 45000],
            'produzione': [15000, 18000, 22000, 30000, 40000, 50000, 70000, 75000, 60000, 40000, 20000, 15000],
            'commerciale': [5000, 6000, 8000, 12000, 18000, 25000, 45000, 50000, 40000, 25000, 10000, 6000],
            'gestione': [60000, 60000, 60000, 60000, 60000, 60000, 60000, 60000, 60000, 180000, 60000, 60000]
        },
        'intur': {
            'ricavi': [245750, 245750, 245750, 245750, 245750, 285750, 285750, 285750, 245750, 245750, 245750, 245750],
            'personale': [15000, 15000, 15000, 15000, 15000, 15000, 15000, 15000, 15000, 15000, 15000, 15000],
            'gestione': [224000, 224000, 224000, 224000, 224000, 224000, 224000, 224000, 224000, 224000, 224000, 224000]
        }
    }

def create_empty_dataframe(company='orti'):
    """Crea DataFrame vuoto con struttura corretta"""
    months = ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic']
    years = ['2025', '2026']
    
    # Create multi-index columns for 18 months
    columns = []
    for year in years:
        for month in months:
            columns.append(f"{month} {year}")
            if year == '2026' and month == 'Giu':
                break
    
    if company == 'orti':
        index = [
            '📈 RICAVI',
            'Hotel (76 camere)',
            'Residence Angelina (19 unità)',
            'CVM (8 appartamenti)',
            'Supermercato',
            'TOTALE RICAVI',
            '',
            '💰 COSTI',
            'PERSONALE',
            'PRODUZIONE (fornitori, materiali)',
            'COMMERCIALE (OTA, marketing)',
            'GESTIONE E FINANZA',
            '  └─ Mutuo MPS €3.5M',
            '  └─ Mutuo Intesa €1.4M',
            '  └─ IMU e tasse',
            '  └─ Canoni e utenze base',
            'TOTALE COSTI',
            '',
            '📊 RISULTATI',
            'EBITDA',
            'Margine EBITDA %',
            'Scostamento vs 2024'
        ]
    else:  # intur
        index = [
            '📈 RICAVI',
            'Fitto Hotel',
            'Fitto Angelina Residence',
            'Entrate Farmacia',
            'Entrate Spiaggia/Lido',
            'TOTALE RICAVI',
            '',
            '💰 COSTI',
            'PERSONALE',
            'PRODUZIONE (manutenzioni)',
            'COMMERCIALE',
            'GESTIONE E FINANZA',
            '  └─ Mutuo Sella €600K',
            '  └─ Mutuo Intesa €1M',
            '  └─ Mutuo MPS €75K',
            '  └─ IMU e tasse',
            '  └─ Canoni fissi',
            'TOTALE COSTI',
            '',
            '📊 RISULTATI',
            'EBITDA',
            'Margine EBITDA %',
            'Scostamento vs 2024'
        ]
    
    # Create DataFrame with zeros
    df = pd.DataFrame(0.0, index=index, columns=columns[:18])
    
    # Pre-fill mutui for ORTI
    if company == 'orti':
        df.loc['  └─ Mutuo MPS €3.5M'] = 12135
        df.loc['  └─ Mutuo Intesa €1.4M'] = 10793
    else:  # INTUR
        # Sella: 50K/month until Dec 2025, then 0
        for col in df.columns[:12]:  # 2025
            df.loc['  └─ Mutuo Sella €600K', col] = 50000
        df.loc['  └─ Mutuo Intesa €1M'] = 8500
        df.loc['  └─ Mutuo MPS €75K'] = 1059
    
    return df

def calculate_totals(df):
    """Calcola totali e risultati"""
    # Skip header rows and empty rows
    revenue_rows = ['Hotel (76 camere)', 'Residence Angelina (19 unità)', 'CVM (8 appartamenti)', 'Supermercato'] if 'Hotel' in df.index else \
                   ['Fitto Hotel', 'Fitto Angelina Residence', 'Entrate Farmacia', 'Entrate Spiaggia/Lido']
    
    cost_rows = ['PERSONALE', 'PRODUZIONE (fornitori, materiali)', 'COMMERCIALE (OTA, marketing)', 'GESTIONE E FINANZA'] if 'PERSONALE' in df.index else \
                ['PERSONALE', 'PRODUZIONE (manutenzioni)', 'COMMERCIALE', 'GESTIONE E FINANZA']
    
    # Calculate totals
    for col in df.columns:
        # Total revenues
        total_revenue = df.loc[revenue_rows, col].sum()
        df.loc['TOTALE RICAVI', col] = total_revenue
        
        # Total costs
        total_costs = df.loc[cost_rows, col].sum()
        df.loc['TOTALE COSTI', col] = total_costs
        
        # EBITDA
        ebitda = total_revenue - total_costs
        df.loc['EBITDA', col] = ebitda
        
        # Margin %
        if total_revenue > 0:
            df.loc['Margine EBITDA %', col] = (ebitda / total_revenue) * 100
        else:
            df.loc['Margine EBITDA %', col] = 0
    
    return df

def calculate_scostamento(df, company):
    """Calcola scostamento vs 2024"""
    if company in st.session_state.data_2024:
        data_2024 = st.session_state.data_2024[company]
        
        # Only for 2025 months
        for i, col in enumerate(df.columns[:12]):
            if i < len(data_2024['ricavi']):
                ricavi_2025 = df.loc['TOTALE RICAVI', col]
                ricavi_2024 = data_2024['ricavi'][i]
                
                if ricavi_2024 > 0:
                    scostamento = ((ricavi_2025 - ricavi_2024) / ricavi_2024) * 100
                    df.loc['Scostamento vs 2024', col] = scostamento
    
    return df

def export_to_excel(df_orti, df_intur):
    """Export data to Excel with formatting"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write ORTI sheet
        df_orti.to_excel(writer, sheet_name='ORTI', index=True)
        
        # Write INTUR sheet
        df_intur.to_excel(writer, sheet_name='INTUR', index=True)
        
        # Add 2024 comparison sheet
        df_2024 = pd.DataFrame(st.session_state.data_2024)
        df_2024.to_excel(writer, sheet_name='Dati 2024', index=True)
        
        # Get workbook and add formats
        workbook = writer.book
        
        # Formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#1e3c72',
            'font_color': 'white',
            'align': 'center'
        })
        
        money_format = workbook.add_format({
            'num_format': '€#,##0',
            'align': 'right'
        })
        
        percent_format = workbook.add_format({
            'num_format': '0.0%',
            'align': 'right'
        })
        
        total_format = workbook.add_format({
            'bold': True,
            'bg_color': '#ffc107',
            'num_format': '€#,##0'
        })
        
        ebitda_format = workbook.add_format({
            'bold': True,
            'bg_color': '#28a745',
            'font_color': 'white',
            'num_format': '€#,##0'
        })
        
        # Format each sheet
        for sheet_name in ['ORTI', 'INTUR']:
            worksheet = writer.sheets[sheet_name]
            worksheet.set_column('A:A', 35)  # First column width
            worksheet.set_column('B:T', 12)  # Data columns width
            
            # Apply number formatting
            for row in range(1, 25):
                for col in range(1, 19):
                    worksheet.write(row, col, df_orti.iloc[row-1, col-1] if sheet_name == 'ORTI' else df_intur.iloc[row-1, col-1], money_format)
    
    output.seek(0)
    return output

# Main App
st.title("📊 CONDGES V4.0 - Dashboard Finanziario Unificato")
st.markdown("**Gennaio 2025 - Giugno 2026** | Sistema completo ORTI + INTUR")

# Sidebar
with st.sidebar:
    st.header("⚙️ Controlli")
    
    company = st.selectbox(
        "Seleziona Società",
        ["ORTI (Operativo)", "INTUR (Immobiliare)", "Consolidato"]
    )
    
    st.divider()
    
    # Quick fill options
    st.subheader("🚀 Riempimento Rapido")
    
    if st.button("📥 Carica Dati 2024 (+10%)", help="Proietta i dati 2024 con crescita 10%"):
        if 'orti' in company.lower():
            df = create_empty_dataframe('orti')
            # Fill with 2024 data + 10%
            data_2024 = st.session_state.data_2024['orti']
            for i in range(12):
                col = df.columns[i]
                df.loc['Hotel (76 camere)', col] = data_2024['ricavi'][i] * 0.75 * 1.1
                df.loc['Residence Angelina (19 unità)', col] = data_2024['ricavi'][i] * 0.15 * 1.1
                df.loc['CVM (8 appartamenti)', col] = data_2024['ricavi'][i] * 0.10 * 1.1
                df.loc['PERSONALE', col] = data_2024['personale'][i] * 1.1
                df.loc['PRODUZIONE (fornitori, materiali)', col] = data_2024['produzione'][i] * 1.1
                df.loc['COMMERCIALE (OTA, marketing)', col] = data_2024['commerciale'][i] * 1.1
                df.loc['GESTIONE E FINANZA', col] = data_2024['gestione'][i]
            st.session_state.data_orti = df
            st.success("✅ Dati ORTI caricati con proiezione +10%")
    
    if st.button("🗑️ Azzera Tutto"):
        if st.checkbox("Conferma azzeramento"):
            st.session_state.data_orti = None
            st.session_state.data_intur = None
            st.rerun()
    
    st.divider()
    
    # Export section
    st.subheader("💾 Export")
    
    if st.button("📊 Genera Excel Completo"):
        if st.session_state.data_orti is not None or st.session_state.data_intur is not None:
            df_orti = st.session_state.data_orti if st.session_state.data_orti is not None else create_empty_dataframe('orti')
            df_intur = st.session_state.data_intur if st.session_state.data_intur is not None else create_empty_dataframe('intur')
            
            excel_file = export_to_excel(df_orti, df_intur)
            
            st.download_button(
                label="⬇️ Scarica Excel",
                data=excel_file,
                file_name=f"CONDGES_V4_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# Main content area
if "orti" in company.lower():
    st.header("🏢 ORTI S.r.l. - Gestione Operativa")
    
    # Initialize or load data
    if st.session_state.data_orti is None:
        st.session_state.data_orti = create_empty_dataframe('orti')
    
    # Display editable dataframe
    st.subheader("📝 Inserimento Dati")
    
    edited_df = st.data_editor(
        st.session_state.data_orti,
        num_rows="fixed",
        use_container_width=True,
        hide_index=False,
        column_config={
            col: st.column_config.NumberColumn(
                col,
                format="€%.0f",
                width="small"
            ) for col in st.session_state.data_orti.columns
        }
    )
    
    # Update calculations
    if st.button("🔄 Ricalcola Totali"):
        edited_df = calculate_totals(edited_df)
        edited_df = calculate_scostamento(edited_df, 'orti')
        st.session_state.data_orti = edited_df
        st.rerun()
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue_2025 = edited_df.loc['TOTALE RICAVI', edited_df.columns[:12]].sum()
        st.metric("Ricavi 2025", f"€{total_revenue_2025:,.0f}")
    
    with col2:
        total_costs_2025 = edited_df.loc['TOTALE COSTI', edited_df.columns[:12]].sum()
        st.metric("Costi 2025", f"€{total_costs_2025:,.0f}")
    
    with col3:
        total_ebitda_2025 = edited_df.loc['EBITDA', edited_df.columns[:12]].sum()
        st.metric("EBITDA 2025", f"€{total_ebitda_2025:,.0f}")
    
    with col4:
        if total_revenue_2025 > 0:
            margin_2025 = (total_ebitda_2025 / total_revenue_2025) * 100
            st.metric("Margine %", f"{margin_2025:.1f}%")
    
    # Charts
    st.subheader("📈 Visualizzazioni")
    
    tab1, tab2, tab3 = st.tabs(["Andamento Mensile", "Confronto 2024", "Breakdown Costi"])
    
    with tab1:
        # Monthly trend chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=edited_df.columns[:12],
            y=edited_df.loc['TOTALE RICAVI', edited_df.columns[:12]],
            name='Ricavi',
            marker_color='green'
        ))
        
        fig.add_trace(go.Bar(
            x=edited_df.columns[:12],
            y=edited_df.loc['TOTALE COSTI', edited_df.columns[:12]],
            name='Costi',
            marker_color='red'
        ))
        
        fig.add_trace(go.Scatter(
            x=edited_df.columns[:12],
            y=edited_df.loc['EBITDA', edited_df.columns[:12]],
            name='EBITDA',
            line=dict(color='blue', width=3),
            mode='lines+markers'
        ))
        
        fig.update_layout(
            title="Andamento Mensile 2025",
            xaxis_title="Mese",
            yaxis_title="Euro",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # 2024 comparison
        data_2024 = st.session_state.data_2024['orti']['ricavi']
        data_2025 = [edited_df.loc['TOTALE RICAVI', col] for col in edited_df.columns[:12]]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic'],
            y=data_2024,
            name='2024',
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Bar(
            x=['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic'],
            y=data_2025,
            name='2025',
            marker_color='darkblue'
        ))
        
        fig.update_layout(
            title="Confronto Ricavi 2024 vs 2025",
            xaxis_title="Mese",
            yaxis_title="Euro",
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Cost breakdown pie chart
        cost_categories = {
            'Personale': edited_df.loc['PERSONALE', edited_df.columns[:12]].sum(),
            'Produzione': edited_df.loc['PRODUZIONE (fornitori, materiali)', edited_df.columns[:12]].sum(),
            'Commerciale': edited_df.loc['COMMERCIALE (OTA, marketing)', edited_df.columns[:12]].sum(),
            'Gestione': edited_df.loc['GESTIONE E FINANZA', edited_df.columns[:12]].sum()
        }
        
        fig = px.pie(
            values=list(cost_categories.values()),
            names=list(cost_categories.keys()),
            title="Breakdown Costi 2025"
        )
        
        st.plotly_chart(fig, use_container_width=True)

elif "intur" in company.lower():
    st.header("🏛️ INTUR S.r.l. - Gestione Immobiliare")
    
    # Initialize or load data
    if st.session_state.data_intur is None:
        st.session_state.data_intur = create_empty_dataframe('intur')
    
    # Similar interface for INTUR...
    st.info("Interfaccia INTUR in costruzione. Usa ORTI per ora.")

else:  # Consolidato
    st.header("📊 Gruppo Consolidato - ORTI + INTUR")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("ORTI")
        if st.session_state.data_orti is not None:
            st.dataframe(st.session_state.data_orti[['Gen 2025', 'Feb 2025', 'Mar 2025']])
    
    with col2:
        st.subheader("INTUR")
        if st.session_state.data_intur is not None:
            st.dataframe(st.session_state.data_intur[['Gen 2025', 'Feb 2025', 'Mar 2025']])

# Footer
st.divider()
st.caption("CONDGES V4.0 - Sistema Unificato di Controllo Gestione | © 2025")
