#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CondGes Dashboard - Unified Hotel Analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import xml.etree.ElementTree as ET
from datetime import datetime, date
from pathlib import Path
import numpy as np
from typing import Dict, List, Tuple
import io

# Page config
st.set_page_config(page_title="CondGes Analytics", page_icon="🏨", layout="wide")

# Constants
HOTELS = ['PANORAMA', 'CVM', 'ANGELINA']
REVENUE_CATEGORIES = {
    'Camere': ['BBCAMERA', 'NOSHOW', 'UPGRADE'],
    'F&B': ['BAR', 'RISDFOOD', 'RISDBEV', 'SCBKFBB'],
    'Servizi': ['CITYTAX', 'PARKCATA', 'PARKCATB', 'PARKCATC'],
}

@st.cache_data
def parse_xml(content: bytes, filename: str) -> pd.DataFrame:
    """Parse XML file and return DataFrame"""
    try:
        root = ET.fromstring(content)
        rows = []

        # Remove namespace for easier parsing
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}')[1]

        # Detect and parse based on structure
        if root.find('.//matrix1_Data'):  # Production format
            for day in root.findall('.//matrix1_Data'):
                date_str = day.get('Data', '')
                if not date_str: continue

                row = {'data': pd.to_datetime(date_str), 'tipo': 'produzione'}

                for charge in day.findall('.//matrix1_Codiceaddebito'):
                    code = charge.get('Codiceaddebito', '')
                    cell = charge.find('.//Cell')
                    if cell is not None:
                        value_str = cell.get('Importo', '0')
                        # Handle Italian format where dot is thousand separator
                        if value_str:
                            # Remove thousand separators (dots) and replace comma with dot for decimals
                            value_str = value_str.replace('.', '')
                            value_str = value_str.replace(',', '.')
                            try:
                                value = float(value_str)
                            except:
                                value = 0
                        else:
                            value = 0
                    else:
                        value = 0

                    if code == 'Camere':
                        row['camere'] = int(value)
                    elif code == 'Adulti':
                        row['adulti'] = int(value)
                    elif code == 'Tot. Gen.':
                        row['totale'] = value
                    elif code and value:
                        row[f'ricavo_{code.lower()}'] = value

                rows.append(row)

        elif root.find('.//table1_Group3'):  # Segment or Market format
            # Detect if it's market or segment based on content
            is_market = False
            first_detail = root.find('.//Detail')
            if first_detail is not None:
                first_value = first_detail.get('textbox36', '')
                # Common market channels
                market_channels = ['OTA', 'DIR', 'GRM', 'ADV', 'TO', 'SITOWEB', 'WAIN', 'TUIUK']
                if first_value in market_channels:
                    is_market = True

            for group in root.findall('.//table1_Group3'):
                period = group.get('Data', '')

                for detail in group.findall('.//Detail'):
                    channel_or_segment = detail.get('textbox36', '')

                    row = {
                        'periodo': period,
                        'camere': float(detail.get('textbox37', 0) or 0),
                        'importo': float(detail.get('textbox39', 0) or 0),
                        'notti': float(detail.get('textbox38', 0) or 0),
                        'tariffa_media': float(detail.get('textbox40', 0) or 0),
                        'tipo': 'mercato' if is_market else 'segmento'
                    }

                    # Add appropriate column based on type
                    if is_market:
                        row['canale'] = channel_or_segment
                    else:
                        row['segmento'] = channel_or_segment

                    if '-' in period:
                        month, year = period.split('-')
                        row['mese'] = int(month)
                        row['anno'] = 2000 + int(year)

                    rows.append(row)

        df = pd.DataFrame(rows)

        # Extract hotel from filename - try multiple patterns
        filename_upper = filename.upper()
        hotel_found = False

        # Check for hotel names in filename
        for hotel in HOTELS:
            if hotel in filename_upper:
                df['hotel'] = hotel
                hotel_found = True
                break

        # Additional patterns for PANORAMA
        if not hotel_found:
            if 'HP' in filename_upper or 'PANORAMA' in filename_upper or 'HOTELP' in filename_upper:
                df['hotel'] = 'PANORAMA'
            elif 'CVM' in filename_upper:
                df['hotel'] = 'CVM'
            elif 'ANGELINA' in filename_upper:
                df['hotel'] = 'ANGELINA'
            else:
                df['hotel'] = 'UNKNOWN'

        # Add time columns
        if 'data' in df.columns:
            df['anno'] = df['data'].dt.year
            df['mese'] = df['data'].dt.month
            df['giorno'] = df['data'].dt.day

        return df

    except Exception as e:
        st.error(f"Error parsing {filename}: {str(e)}")
        return pd.DataFrame()

def process_multiple_files(files):
    """Process multiple uploaded files and return combined dataframe"""
    all_dfs = []

    for file in files:
        try:
            # Reset file position if needed
            if hasattr(file, 'seek'):
                file.seek(0)
            content = file.read()
            df = parse_xml(content, file.name)
            if not df.empty:
                all_dfs.append(df)
        except Exception as e:
            st.error(f"Error processing {file.name}: {str(e)}")

    if all_dfs:
        return pd.concat(all_dfs, ignore_index=True)
    return pd.DataFrame()

def create_kpi_metrics(df: pd.DataFrame, year_current: int, year_previous: int):
    """Calculate and display KPI metrics"""
    current = df[df['anno'] == year_current]
    previous = df[df['anno'] == year_previous]

    col1, col2, col3, col4 = st.columns(4)

    # Revenue
    if 'totale' in df.columns:
        curr_rev = current['totale'].sum()
        prev_rev = previous['totale'].sum()
        delta = ((curr_rev - prev_rev) / prev_rev * 100) if prev_rev > 0 else 0
        with col1:
            st.metric("Ricavi Totali", f"€{curr_rev:,.0f}", f"{delta:+.1f}%")

    # Rooms
    if 'camere' in df.columns:
        curr_rooms = current['camere'].sum()
        prev_rooms = previous['camere'].sum()
        delta = ((curr_rooms - prev_rooms) / prev_rooms * 100) if prev_rooms > 0 else 0
        with col2:
            st.metric("Camere", f"{curr_rooms:,.0f}", f"{delta:+.1f}%")

    # ADR
    if 'totale' in df.columns and 'camere' in df.columns:
        curr_adr = current['totale'].sum() / current['camere'].sum() if current['camere'].sum() > 0 else 0
        prev_adr = previous['totale'].sum() / previous['camere'].sum() if previous['camere'].sum() > 0 else 0
        delta = ((curr_adr - prev_adr) / prev_adr * 100) if prev_adr > 0 else 0
        with col3:
            st.metric("ADR", f"€{curr_adr:.2f}", f"{delta:+.1f}%")

    # Occupancy trend
    if 'camere' in df.columns:
        curr_avg = current['camere'].mean()
        prev_avg = previous['camere'].mean()
        delta = ((curr_avg - prev_avg) / prev_avg * 100) if prev_avg > 0 else 0
        with col4:
            st.metric("Media Camere/Giorno", f"{curr_avg:.1f}", f"{delta:+.1f}%")

def create_comparison_chart(df: pd.DataFrame, metric: str, title: str):
    """Create year-over-year comparison chart"""
    if metric not in df.columns:
        return None

    monthly = df.groupby(['anno', 'mese'])[metric].sum().reset_index()

    fig = px.line(monthly, x='mese', y=metric, color='anno',
                  title=title, markers=True)

    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu',
                      'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic']
        )
    )

    return fig

def create_revenue_breakdown(df: pd.DataFrame):
    """Create revenue breakdown chart"""
    # Check what type of data we have
    if 'tipo' in df.columns:
        tipo = df['tipo'].iloc[0] if not df.empty else 'unknown'

        if tipo == 'mercato' and 'canale' in df.columns:
            # Market channel breakdown
            channel_data = df.groupby('canale')['importo'].sum().sort_values(ascending=False)
            if not channel_data.empty:
                fig = px.pie(values=channel_data.values,
                           names=channel_data.index,
                           title="Ricavi per Canale di Vendita")
                return fig

        elif tipo == 'segmento' and 'segmento' in df.columns:
            # Segment breakdown
            segment_data = df.groupby('segmento')['importo'].sum().sort_values(ascending=False)
            if not segment_data.empty:
                fig = px.pie(values=segment_data.values,
                           names=segment_data.index,
                           title="Ricavi per Segmento Cliente")
                return fig

    # Default: revenue categories for production data
    revenue_cols = [col for col in df.columns if col.startswith('ricavo_')]

    if not revenue_cols:
        return None

    # Categorize revenues
    category_sums = {}
    for category, codes in REVENUE_CATEGORIES.items():
        total = 0
        for col in revenue_cols:
            for code in codes:
                if code.lower() in col:
                    total += df[col].sum()
        if total > 0:
            category_sums[category] = total

    # Add uncategorized
    all_revenue = sum(df[col].sum() for col in revenue_cols)
    categorized = sum(category_sums.values())
    if all_revenue > categorized:
        category_sums['Altri'] = all_revenue - categorized

    if category_sums:
        fig = px.pie(values=list(category_sums.values()),
                     names=list(category_sums.keys()),
                     title="Breakdown Ricavi per Categoria")
        return fig

    return None

def main():
    st.title("🏨 CondGes - Hotel Analytics Dashboard")

    # Initialize session state
    if 'data' not in st.session_state:
        st.session_state.data = pd.DataFrame()

    # Sidebar
    with st.sidebar:
        st.header("📁 Carica File")

        uploaded_files = st.file_uploader(
            "Seleziona file XML",
            type=['xml'],
            accept_multiple_files=True
        )

        if uploaded_files:
            if st.button("📊 Analizza", type="primary"):
                with st.spinner(f"Elaborazione di {len(uploaded_files)} file..."):
                    st.session_state.data = process_multiple_files(uploaded_files)

                    if not st.session_state.data.empty:
                        st.success(f"✅ Caricati {len(uploaded_files)} file con {len(st.session_state.data)} record totali")

                        # Show quick summary
                        if 'hotel' in st.session_state.data.columns:
                            hotel_counts = st.session_state.data['hotel'].value_counts()
                            st.write("File caricati per hotel:")
                            for hotel, count in hotel_counts.items():
                                st.write(f"  • {hotel}: {count} record")

                        # Show type summary
                        if 'tipo' in st.session_state.data.columns:
                            type_counts = st.session_state.data['tipo'].value_counts()
                            st.write("\nTipi di dati:")
                            for tipo, count in type_counts.items():
                                st.write(f"  • {tipo}: {count} record")

                        # Show year summary
                        if 'anno' in st.session_state.data.columns:
                            year_counts = st.session_state.data['anno'].value_counts().sort_index()
                            st.write("\nDati per anno:")
                            for year, count in year_counts.items():
                                st.write(f"  • {year}: {count} record")

                            if len(year_counts) == 1:
                                st.info(f"⚠️ I dati caricati contengono solo l'anno {year_counts.index[0]}. Per confronti anno su anno, carica anche i dati dell'anno precedente.")
                    else:
                        st.error("Nessun dato valido trovato nei file caricati")

        if not st.session_state.data.empty:
            st.divider()
            st.header("🔍 Filtri")

            # Hotel filter
            if 'hotel' in st.session_state.data.columns:
                hotels = ['Tutti'] + sorted(st.session_state.data['hotel'].unique())
                selected_hotel = st.selectbox("Hotel", hotels)

            # Year filter
            if 'anno' in st.session_state.data.columns:
                years = sorted(st.session_state.data['anno'].unique())
                if len(years) >= 2:
                    col1, col2 = st.columns(2)
                    with col1:
                        year_current = st.selectbox("Anno corrente", years, index=len(years)-1)
                    with col2:
                        year_previous = st.selectbox("Anno confronto", years, index=len(years)-2)
                else:
                    year_current = years[0] if years else datetime.now().year
                    year_previous = year_current - 1

    # Main content
    if not st.session_state.data.empty:
        # Apply filters
        df = st.session_state.data.copy()
        if 'selected_hotel' in locals() and selected_hotel != 'Tutti':
            df = df[df['hotel'] == selected_hotel]

        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "💰 Ricavi", "🏨 Occupazione", "📊 Dati"])

        with tab1:
            st.header("Dashboard Overview")

            # KPIs
            create_kpi_metrics(df, year_current, year_previous)

            # Revenue trend
            col1, col2 = st.columns(2)
            with col1:
                fig = create_comparison_chart(df, 'totale', 'Ricavi Totali - Confronto Annuale')
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = create_comparison_chart(df, 'camere', 'Camere Occupate - Confronto Annuale')
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.header("Analisi Ricavi")

            # Revenue breakdown
            fig = create_revenue_breakdown(df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

            # Monthly revenue table
            if 'totale' in df.columns:
                monthly_rev = df.groupby(['anno', 'mese'])['totale'].sum().unstack(fill_value=0)
                st.subheader("Ricavi Mensili")
                st.dataframe(monthly_rev.style.format("€{:,.0f}"), use_container_width=True)

        with tab3:
            st.header("Analisi Occupazione")

            if 'camere' in df.columns and 'mese' in df.columns and 'giorno' in df.columns:
                # Occupancy heatmap
                try:
                    # Create pivot table
                    pivot = df.pivot_table(values='camere', index='giorno', columns='mese', aggfunc='mean')

                    # Fill missing values and ensure all months are present
                    all_months = list(range(1, 13))
                    all_days = list(range(1, 32))

                    # Reindex to ensure consistent dimensions
                    pivot = pivot.reindex(index=all_days, columns=all_months, fill_value=0)

                    # Create heatmap
                    fig = go.Figure(data=go.Heatmap(
                        z=pivot.values,
                        x=['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu',
                           'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic'],
                        y=list(range(1, 32)),
                        colorscale="RdYlGn",
                        hoverongaps=False,
                        hovertemplate='Giorno: %{y}<br>Mese: %{x}<br>Camere: %{z:.0f}<extra></extra>'
                    ))

                    fig.update_layout(
                        title="Heatmap Occupazione Media",
                        xaxis_title="Mese",
                        yaxis_title="Giorno",
                        height=600
                    )

                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Impossibile creare heatmap occupazione: {str(e)}")

            # Guest analysis
            if 'adulti' in df.columns:
                col1, col2 = st.columns(2)
                with col1:
                    monthly_guests = df.groupby(['anno', 'mese'])['adulti'].sum().reset_index()
                    fig = px.bar(monthly_guests, x='mese', y='adulti', color='anno',
                                title="Ospiti Adulti per Mese", barmode='group')
                    st.plotly_chart(fig, use_container_width=True)

        with tab4:
            st.header("Dati Raw")

            # Data preview
            st.write(f"**Totale record:** {len(df):,}")

            # Column selector
            cols = st.multiselect("Colonne da visualizzare",
                                 df.columns.tolist(),
                                 default=['data', 'hotel', 'camere', 'totale'][:4])

            if cols:
                st.dataframe(df[cols].head(1000), use_container_width=True)

                # Export
                csv = df[cols].to_csv(index=False)
                st.download_button(
                    "📥 Scarica CSV",
                    csv,
                    f"condges_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )

    else:
        st.info("👋 Carica uno o più file XML per iniziare l'analisi")

        with st.expander("ℹ️ Formati supportati"):
            st.markdown("""
            - **Produzione**: Dati giornalieri di occupazione e ricavi (matrix1_Data)
            - **Segmenti**: Analisi per segmento cliente (INLE, GRLE, etc.)
            - **Mercato**: Analisi per canale di vendita (OTA, DIR, GRM, etc.)
            - **Multi-hotel**: Supporta PANORAMA, CVM, ANGELINA
            """)

if __name__ == "__main__":
    main()
