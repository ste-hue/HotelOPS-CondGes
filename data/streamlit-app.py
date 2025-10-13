# ═══════════════════════════════════════════════════════════════════════════════
# 🌐 CONDGES DASHBOARD - STREAMLIT PROTOTYPE
# ═══════════════════════════════════════════════════════════════════════════════

def create_dashboard_prototype():
    print("🌐 CREATING DASHBOARD PROTOTYPE")
    print("=" * 60)
    
    # Create Streamlit app file
    dashboard_code = '''
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# Page config
st.set_page_config(
    page_title="CONDGES V4.0 - Hotel Financial Dashboard",
    page_icon="🏨",
    layout="wide"
)

# Title
st.title("🏨 CONDGES V4.0 - Hotel Financial Dashboard")
st.markdown("**Gruppo Panorama - Amalfi Coast Operations**")

# Load data
@st.cache_data
def load_data():
    try:
        # Load JSON data
        with open('output/CONDGES_ALLOCAZIONE_COMPLETA_PER_ASSET.json', 'r') as f:
            data = json.load(f)
        return data
    except:
        st.error("❌ Data file not found")
        return None

data = load_data()

if data:
    # Sidebar filters
    st.sidebar.header("🔧 Filters")
    
    # Year selection
    years = list(data['data'].keys())
    selected_year = st.sidebar.selectbox("📅 Select Year", years, index=len(years)-1)
    
    # Asset selection
    assets = ["HOTEL", "RESIDENCE_ANGELINA", "CVM"]
    selected_assets = st.sidebar.multiselect("🏢 Select Assets", assets, default=assets)
    
    # Main dashboard
    col1, col2, col3 = st.columns(3)
    
    # KPIs
    year_data = data['summary'][selected_year]
    
    with col1:
        st.metric(
            "🏨 Hotel Revenue", 
            f"€{year_data['HOTEL']['ricavi_annuali']:,.0f}",
            f"{year_data['HOTEL']['margine_pct']:.1f}% margin"
        )
    
    with col2:
        st.metric(
            "🏠 Residence Angelina", 
            f"€{year_data['RESIDENCE_ANGELINA']['ricavi_annuali']:,.0f}",
            f"{year_data['RESIDENCE_ANGELINA']['margine_pct']:.1f}% margin"
        )
    
    with col3:
        st.metric(
            "🏘️ CVM", 
            f"€{year_data['CVM']['ricavi_annuali']:,.0f}",
            f"{year_data['CVM']['margine_pct']:.1f}% margin"
        )
    
    # Monthly trends
    st.header("📈 Monthly Performance")
    
    # Prepare data for charts
    monthly_data = []
    for month, month_data in data['data'][selected_year].items():
        for asset in selected_assets:
            monthly_data.append({
                'Month': month,
                'Asset': asset.replace('_', ' ').title(),
                'Revenue': month_data[asset]['ricavi'],
                'Costs': month_data[asset]['costi']['totale'],
                'Margin': month_data[asset]['margine'],
                'Margin_PCT': month_data[asset]['margine_pct']
            })
    
    df_monthly = pd.DataFrame(monthly_data)
    
    # Revenue chart
    fig_revenue = px.line(
        df_monthly, 
        x='Month', 
        y='Revenue', 
        color='Asset',
        title=f"Monthly Revenue by Asset ({selected_year})",
        markers=True
    )
    st.plotly_chart(fig_revenue, use_container_width=True)
    
    # Margin chart
    fig_margin = px.bar(
        df_monthly, 
        x='Month', 
        y='Margin_PCT', 
        color='Asset',
        title=f"Monthly Margin % by Asset ({selected_year})",
        barmode='group'
    )
    st.plotly_chart(fig_margin, use_container_width=True)
    
    # Detailed table
    st.header("📊 Detailed Monthly Data")
    
    # Create detailed view
    detailed_data = []
    for month, month_data in data['data'][selected_year].items():
        for asset in selected_assets:
            asset_data = month_data[asset]
            detailed_data.append({
                'Month': month,
                'Asset': asset.replace('_', ' ').title(),
                'Revenue': f"€{asset_data['ricavi']:,.0f}",
                'Personnel': f"€{asset_data['costi']['personale']:,.0f}",
                'Production': f"€{asset_data['costi']['produzione']:,.0f}",
                'Management': f"€{asset_data['costi']['gestione']:,.0f}",
                'Commercial': f"€{asset_data['costi']['commerciale']:,.0f}",
                'Total Costs': f"€{asset_data['costi']['totale']:,.0f}",
                'Margin': f"€{asset_data['margine']:,.0f}",
                'Margin %': f"{asset_data['margine_pct']:.1f}%"
            })
    
    df_detailed = pd.DataFrame(detailed_data)
    st.dataframe(df_detailed, use_container_width=True)
    
    # Year comparison
    if len(years) > 1:
        st.header("📊 Year-over-Year Comparison")
        
        comparison_data = []
        for asset in assets:
            for year in years:
                year_summary = data['summary'][year][asset]
                comparison_data.append({
                    'Asset': asset.replace('_', ' ').title(),
                    'Year': year,
                    'Revenue': year_summary['ricavi_annuali'],
                    'Costs': year_summary['costi_annuali'],
                    'Margin': year_summary['margine_annuale'],
                    'Margin %': year_summary['margine_pct']
                })
        
        df_comparison = pd.DataFrame(comparison_data)
        
        # YoY Revenue comparison
        fig_yoy = px.bar(
            df_comparison,
            x='Asset',
            y='Revenue',
            color='Year',
            title="Year-over-Year Revenue Comparison",
            barmode='group'
        )
        st.plotly_chart(fig_yoy, use_container_width=True)

else:
    st.error("❌ Unable to load data")
'''
    
    # Save dashboard file
    dashboard_path = '/Users/stefanodellapietra/Desktop/Projects/HotelOPS/modules/CondGes/dashboard.py'
    
    with open(dashboard_path, 'w') as f:
        f.write(dashboard_code)
    
    print(f"✅ Dashboard created: {dashboard_path}")
    
    # Create requirements for dashboard
    requirements_dashboard = '''
streamlit>=1.28.0
plotly>=5.15.0
pandas>=2.0.0
'''
    
    with open('/Users/stefanodellapietra/Desktop/Projects/HotelOPS/modules/CondGes/requirements_dashboard.txt', 'w') as f:
        f.write(requirements_dashboard)
    
    print(f"✅ Requirements created: requirements_dashboard.txt")
    
    print(f"\n🚀 TO RUN DASHBOARD:")
    print(f"  1. pip install -r requirements_dashboard.txt")
    print(f"  2. streamlit run dashboard.py")
    print(f"  3. Open browser to http://localhost:8501")
    
    print(f"\n📊 DASHBOARD FEATURES:")
    print(f"  ✅ Interactive year/asset filters")
    print(f"  ✅ Monthly revenue/margin charts")
    print(f"  ✅ Detailed cost breakdown tables")
    print(f"  ✅ Year-over-year comparisons")
    print(f"  ✅ Professional hotel industry styling")

# Create dashboard
create_dashboard_prototype()