#!/usr/bin/env python3
"""
Advanced Dashboard Builder for ORTI/INTUR 2025
"""

import gspread
from google.oauth2.service_account import Credentials
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
CONFIG_DIR = PROJECT_DIR / "config"

SPREADSHEET_ID = "1CAT_EN6DOXyT3vEbYmnwRQh1pWrdnrCXHFWR--JtFmQ"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Styles
HEADER_BLUE = {"textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
               "backgroundColor": {"red": 0.2, "green": 0.4, "blue": 0.7}}
HEADER_GREEN = {"textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                "backgroundColor": {"red": 0.2, "green": 0.6, "blue": 0.3}}
HEADER_PURPLE = {"textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                 "backgroundColor": {"red": 0.5, "green": 0.3, "blue": 0.7}}
HEADER_ORANGE = {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.9, "green": 0.7, "blue": 0.2}}
HEADER_GRAY = {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}}
NUM_EUR = {"numberFormat": {"type": "NUMBER", "pattern": "€#,##0"}}
NUM_PCT = {"numberFormat": {"type": "PERCENT", "pattern": "0.0%"}}
NUM_DELTA = {"numberFormat": {"type": "NUMBER", "pattern": "+€#,##0;-€#,##0"}}
NUM_PCT_DELTA = {"numberFormat": {"type": "PERCENT", "pattern": "+0.0%;-0.0%"}}
INPUT_CELL = {"backgroundColor": {"red": 1, "green": 0.95, "blue": 0.8}, "numberFormat": {"type": "PERCENT", "pattern": "0%"}}


def get_client():
    credentials = Credentials.from_service_account_file(str(CONFIG_DIR / "hotelHops.json"), scopes=SCOPES)
    return gspread.authorize(credentials)


def get_or_create_sheet(spreadsheet, name, rows=100, cols=20):
    try:
        ws = spreadsheet.worksheet(name)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=name, rows=rows, cols=cols)
    return ws


def create_kpi_dashboard(spreadsheet):
    """KPI Dashboard with key metrics"""
    print("  Creating KPI Dashboard...")
    ws = get_or_create_sheet(spreadsheet, "📊 KPI_2025", 50, 10)

    data = [
        ["🏨 HOTELOPS - KPI DASHBOARD 2025"],
        [""],
        ["📈 KEY METRICS", "", "ORTI", "INTUR", "CONSOLIDATO"],
        [""],
        ["Ricavi Totali", "", "=SUM(ORTI_Dashboard!H2:H13)", "=SUM(INTUR_Dashboard!H2:H13)", "=C5+D5"],
        ["Costi Totali", "", "=SUM(ORTI_Dashboard!L2:L13)", "=SUM(INTUR_Dashboard!L2:L13)", "=C6+D6"],
        ["EBITDA", "", "=C5-C6", "=D5-D6", "=E5-E6"],
        ["Margine EBITDA %", "", "=C7/C5", "=D7/D5", "=E7/E5"],
        [""],
        ["💰 RICAVI PER BU", "", "ORTI", "INTUR", "TOTALE", "% Mix"],
        [""],
        ["Hotel", "", "=SUM(ORTI_Dashboard!B2:B13)", "=SUM(INTUR_Dashboard!B2:B13)", "=C12+D12", "=E12/$E$5"],
        ["Angelina", "", "=SUM(ORTI_Dashboard!C2:C13)", "=SUM(INTUR_Dashboard!C2:C13)", "=C13+D13", "=E13/$E$5"],
        ["CVM", "", "=SUM(ORTI_Dashboard!D2:D13)", "=SUM(INTUR_Dashboard!D2:D13)", "=C14+D14", "=E14/$E$5"],
        ["F&B", "", "=SUM(ORTI_Dashboard!E2:E13)", "=SUM(INTUR_Dashboard!E2:E13)", "=C15+D15", "=E15/$E$5"],
        ["Spiaggia", "", "=SUM(ORTI_Dashboard!F2:F13)", "=SUM(INTUR_Dashboard!F2:F13)", "=C16+D16", "=E16/$E$5"],
        ["Altri", "", "=SUM(ORTI_Dashboard!G2:G13)", "=SUM(INTUR_Dashboard!G2:G13)", "=C17+D17", "=E17/$E$5"],
        [""],
        ["📉 STRUTTURA COSTI", "", "ORTI", "INTUR", "TOTALE", "% Ricavi"],
        [""],
        ["Costi Fissi", "", "=SUM(ORTI_Dashboard!I2:I13)", "=SUM(INTUR_Dashboard!I2:I13)", "=C21+D21", "=E21/$E$5"],
        ["Costi Variabili", "", "=SUM(ORTI_Dashboard!J2:J13)", "=SUM(INTUR_Dashboard!J2:J13)", "=C22+D22", "=E22/$E$5"],
        ["Personale", "", "=SUM(ORTI_Dashboard!K2:K13)", "=SUM(INTUR_Dashboard!K2:K13)", "=C23+D23", "=E23/$E$5"],
        [""],
        ["🌞 STAGIONALITÀ", "", "Alta (Giu-Set)", "Bassa (Resto)", "Ratio"],
        [""],
        ["Ricavi Consolidati", "", "=SUM(ORTI_Dashboard!H7:H10)+SUM(INTUR_Dashboard!H7:H10)",
         "=SUM(ORTI_Dashboard!H2:H6)+SUM(ORTI_Dashboard!H11:H13)+SUM(INTUR_Dashboard!H2:H6)+SUM(INTUR_Dashboard!H11:H13)", "=C27/D27"],
        ["EBITDA Consolidato", "", "=SUM(ORTI_Dashboard!M7:M10)+SUM(INTUR_Dashboard!M7:M10)",
         "=SUM(ORTI_Dashboard!M2:M6)+SUM(ORTI_Dashboard!M11:M13)+SUM(INTUR_Dashboard!M2:M6)+SUM(INTUR_Dashboard!M11:M13)", "=IF(D28<>0,C28/D28,0)"],
    ]
    ws.update(range_name="A1", values=data)

    # Formatting
    ws.format("A1", {"textFormat": {"bold": True, "fontSize": 16}})
    ws.format("A3:F3", HEADER_BLUE)
    ws.format("A10:F10", HEADER_GREEN)
    ws.format("A19:F19", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.7, "green": 0.3, "blue": 0.3},
                          "foregroundColor": {"red": 1, "green": 1, "blue": 1}})
    ws.format("A25:E25", HEADER_ORANGE)
    ws.format("C5:E7", NUM_EUR)
    ws.format("C8:E8", NUM_PCT)
    ws.format("C12:E17", NUM_EUR)
    ws.format("F12:F17", NUM_PCT)
    ws.format("C21:E23", NUM_EUR)
    ws.format("F21:F23", NUM_PCT)
    ws.format("C27:D28", NUM_EUR)
    ws.freeze(rows=1)
    print("    ✓ Done")


def create_monthly_trends(spreadsheet):
    """Monthly trends analysis"""
    print("  Creating Monthly Trends...")
    ws = get_or_create_sheet(spreadsheet, "📈 Trends", 20, 15)

    data = [
        ["📈 TREND MENSILI CONSOLIDATO 2025"],
        [""],
        ["", "Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic", "TOTALE"],
        ["Ricavi", "=ORTI_Dashboard!H2+INTUR_Dashboard!H2", "=ORTI_Dashboard!H3+INTUR_Dashboard!H3",
         "=ORTI_Dashboard!H4+INTUR_Dashboard!H4", "=ORTI_Dashboard!H5+INTUR_Dashboard!H5",
         "=ORTI_Dashboard!H6+INTUR_Dashboard!H6", "=ORTI_Dashboard!H7+INTUR_Dashboard!H7",
         "=ORTI_Dashboard!H8+INTUR_Dashboard!H8", "=ORTI_Dashboard!H9+INTUR_Dashboard!H9",
         "=ORTI_Dashboard!H10+INTUR_Dashboard!H10", "=ORTI_Dashboard!H11+INTUR_Dashboard!H11",
         "=ORTI_Dashboard!H12+INTUR_Dashboard!H12", "=ORTI_Dashboard!H13+INTUR_Dashboard!H13", "=SUM(B4:M4)"],
        ["Costi", "=ORTI_Dashboard!L2+INTUR_Dashboard!L2", "=ORTI_Dashboard!L3+INTUR_Dashboard!L3",
         "=ORTI_Dashboard!L4+INTUR_Dashboard!L4", "=ORTI_Dashboard!L5+INTUR_Dashboard!L5",
         "=ORTI_Dashboard!L6+INTUR_Dashboard!L6", "=ORTI_Dashboard!L7+INTUR_Dashboard!L7",
         "=ORTI_Dashboard!L8+INTUR_Dashboard!L8", "=ORTI_Dashboard!L9+INTUR_Dashboard!L9",
         "=ORTI_Dashboard!L10+INTUR_Dashboard!L10", "=ORTI_Dashboard!L11+INTUR_Dashboard!L11",
         "=ORTI_Dashboard!L12+INTUR_Dashboard!L12", "=ORTI_Dashboard!L13+INTUR_Dashboard!L13", "=SUM(B5:M5)"],
        ["EBITDA", "=B4-B5", "=C4-C5", "=D4-D5", "=E4-E5", "=F4-F5", "=G4-G5",
         "=H4-H5", "=I4-I5", "=J4-J5", "=K4-K5", "=L4-L5", "=M4-M5", "=SUM(B6:M6)"],
        ["Margine %", "=IF(B4=0,0,B6/B4)", "=IF(C4=0,0,C6/C4)", "=IF(D4=0,0,D6/D4)", "=IF(E4=0,0,E6/E4)",
         "=IF(F4=0,0,F6/F4)", "=IF(G4=0,0,G6/G4)", "=IF(H4=0,0,H6/H4)", "=IF(I4=0,0,I6/I4)",
         "=IF(J4=0,0,J6/J4)", "=IF(K4=0,0,K6/K4)", "=IF(L4=0,0,L6/L4)", "=IF(M4=0,0,M6/M4)", "=IF(N4=0,0,N6/N4)"],
        [""],
        ["YTD CUMULATO", "Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"],
        ["Ricavi Cum.", "=B4", "=B10+C4", "=C10+D4", "=D10+E4", "=E10+F4", "=F10+G4",
         "=G10+H4", "=H10+I4", "=I10+J4", "=J10+K4", "=K10+L4", "=L10+M4"],
        ["EBITDA Cum.", "=B6", "=B11+C6", "=C11+D6", "=D11+E6", "=E11+F6", "=F11+G6",
         "=G11+H6", "=H11+I6", "=I11+J6", "=J11+K6", "=K11+L6", "=L11+M6"],
    ]
    ws.update(range_name="A1", values=data)

    ws.format("A1", {"textFormat": {"bold": True, "fontSize": 16}})
    ws.format("A3:N3", HEADER_BLUE)
    ws.format("A9:M9", HEADER_GRAY)
    ws.format("B4:N6", NUM_EUR)
    ws.format("B7:N7", NUM_PCT)
    ws.format("B10:M11", NUM_EUR)
    print("    ✓ Done")


def create_scenario_builder(spreadsheet):
    """2026 scenario projection builder"""
    print("  Creating 2026 Scenario Builder...")
    ws = get_or_create_sheet(spreadsheet, "🔮 Scenario_2026", 50, 12)

    data = [
        ["🔮 SCENARIO BUILDER 2026"],
        [""],
        ["⚙️ PARAMETRI (modifica celle gialle)", "", "Valore"],
        [""],
        ["Crescita Ricavi %", "", "5%"],
        ["Δ Costi Fissi %", "", "3%"],
        ["Δ Costi Variabili %", "", "4%"],
        ["Δ Personale %", "", "5%"],
        [""],
        ["═══════════════════════════════════════════════════════════════"],
        [""],
        ["📊 BASELINE 2025", "", "ORTI", "INTUR", "CONSOLIDATO"],
        [""],
        ["Ricavi", "", "=SUM(ORTI_Dashboard!H2:H13)", "=SUM(INTUR_Dashboard!H2:H13)", "=C14+D14"],
        ["Costi Fissi", "", "=SUM(ORTI_Dashboard!I2:I13)", "=SUM(INTUR_Dashboard!I2:I13)", "=C15+D15"],
        ["Costi Variabili", "", "=SUM(ORTI_Dashboard!J2:J13)", "=SUM(INTUR_Dashboard!J2:J13)", "=C16+D16"],
        ["Personale", "", "=SUM(ORTI_Dashboard!K2:K13)", "=SUM(INTUR_Dashboard!K2:K13)", "=C17+D17"],
        ["Costi Totali", "", "=C15+C16+C17", "=D15+D16+D17", "=E15+E16+E17"],
        ["EBITDA", "", "=C14-C18", "=D14-D18", "=E14-E18"],
        ["Margine %", "", "=C19/C14", "=D19/D14", "=E19/E14"],
        [""],
        ["═══════════════════════════════════════════════════════════════"],
        [""],
        ["🚀 PROIEZIONE 2026", "", "ORTI", "INTUR", "CONSOLIDATO", "Δ €", "Δ %"],
        [""],
        ["Ricavi", "", "=C14*(1+$C$5)", "=D14*(1+$C$5)", "=C26+D26", "=E26-E14", "=F26/E14"],
        ["Costi Fissi", "", "=C15*(1+$C$6)", "=D15*(1+$C$6)", "=C27+D27", "=E27-E15", "=F27/E15"],
        ["Costi Variabili", "", "=C16*(1+$C$7)", "=D16*(1+$C$7)", "=C28+D28", "=E28-E16", "=F28/E16"],
        ["Personale", "", "=C17*(1+$C$8)", "=D17*(1+$C$8)", "=C29+D29", "=E29-E17", "=F29/E17"],
        ["Costi Totali", "", "=C27+C28+C29", "=D27+D28+D29", "=E27+E28+E29", "=E30-E18", "=F30/E18"],
        ["EBITDA", "", "=C26-C30", "=D26-D30", "=E26-E30", "=E31-E19", "=IF(E19<>0,F31/E19,0)"],
        ["Margine %", "", "=C31/C26", "=D31/D26", "=E31/E26", "=E32-E20", ""],
        [""],
        ["═══════════════════════════════════════════════════════════════"],
        [""],
        ["📋 SCENARI RAPIDI", "", "Conservative", "Base", "Optimistic", "Aggressive"],
        [""],
        ["Crescita Ricavi", "", "2%", "5%", "8%", "12%"],
        ["Δ Costi", "", "2%", "4%", "5%", "7%"],
        [""],
        ["EBITDA 2026", "",
         "=E14*(1+C38)-E18*(1+C39)", "=E14*(1+D38)-E18*(1+D39)",
         "=E14*(1+E38)-E18*(1+E39)", "=E14*(1+F38)-E18*(1+F39)"],
        ["Margine %", "",
         "=C41/(E14*(1+C38))", "=D41/(E14*(1+D38))", "=E41/(E14*(1+E38))", "=F41/(E14*(1+F38))"],
        ["Δ vs 2025", "", "=C41-E19", "=D41-E19", "=E41-E19", "=F41-E19"],
    ]
    ws.update(range_name="A1", values=data)

    ws.format("A1", {"textFormat": {"bold": True, "fontSize": 16}})
    ws.format("A3", {"textFormat": {"bold": True}})
    ws.format("C5:C8", INPUT_CELL)
    ws.format("A12:E12", HEADER_BLUE)
    ws.format("A24:G24", HEADER_GREEN)
    ws.format("A36:F36", HEADER_ORANGE)
    ws.format("C14:E20", NUM_EUR)
    ws.format("C20:E20", NUM_PCT)
    ws.format("C26:E32", NUM_EUR)
    ws.format("F26:F31", NUM_DELTA)
    ws.format("G26:G31", NUM_PCT_DELTA)
    ws.format("C32:E32", NUM_PCT)
    ws.format("C38:F39", NUM_PCT)
    ws.format("C41:F41", NUM_EUR)
    ws.format("C42:F42", NUM_PCT)
    ws.format("C43:F43", NUM_DELTA)
    ws.freeze(rows=1)
    print("    ✓ Done")


def create_bu_breakdown(spreadsheet):
    """Business Unit breakdown"""
    print("  Creating BU Breakdown...")
    ws = get_or_create_sheet(spreadsheet, "🏢 BU_Detail", 30, 10)

    data = [
        ["🏢 DETTAGLIO BUSINESS UNIT 2025"],
        [""],
        ["BU", "ORTI", "INTUR", "TOTALE", "% Mix", "Stagione Peak"],
        [""],
        ["Hotel", "=SUM(ORTI_Dashboard!B2:B13)", "=SUM(INTUR_Dashboard!B2:B13)", "=B5+C5", "=D5/$D$11", "Lug-Set"],
        ["Angelina", "=SUM(ORTI_Dashboard!C2:C13)", "=SUM(INTUR_Dashboard!C2:C13)", "=B6+C6", "=D6/$D$11", "Lug-Set"],
        ["CVM", "=SUM(ORTI_Dashboard!D2:D13)", "=SUM(INTUR_Dashboard!D2:D13)", "=B7+C7", "=D7/$D$11", "Lug-Set"],
        ["F&B", "=SUM(ORTI_Dashboard!E2:E13)", "=SUM(INTUR_Dashboard!E2:E13)", "=B8+C8", "=D8/$D$11", "Ago"],
        ["Spiaggia", "=SUM(ORTI_Dashboard!F2:F13)", "=SUM(INTUR_Dashboard!F2:F13)", "=B9+C9", "=D9/$D$11", "Lug-Ago"],
        ["Altri", "=SUM(ORTI_Dashboard!G2:G13)", "=SUM(INTUR_Dashboard!G2:G13)", "=B10+C10", "=D10/$D$11", "Variabile"],
        ["TOTALE", "=SUM(B5:B10)", "=SUM(C5:C10)", "=SUM(D5:D10)", "100%", ""],
        [""],
        ["PERFORMANCE ORTI vs INTUR", "", "ORTI", "INTUR", "Δ", "Note"],
        [""],
        ["Ricavi Totali", "", "=SUM(ORTI_Dashboard!H2:H13)", "=SUM(INTUR_Dashboard!H2:H13)", "=C15-D15", ""],
        ["EBITDA", "", "=SUM(ORTI_Dashboard!M2:M13)", "=SUM(INTUR_Dashboard!M2:M13)", "=C16-D16", ""],
        ["Margine %", "", "=C16/C15", "=D16/D15", "=C17-D17", ""],
        ["Personale/Ricavi", "", "=SUM(ORTI_Dashboard!K2:K13)/C15", "=SUM(INTUR_Dashboard!K2:K13)/D15", "=C18-D18", ""],
    ]
    ws.update(range_name="A1", values=data)

    ws.format("A1", {"textFormat": {"bold": True, "fontSize": 16}})
    ws.format("A3:F3", HEADER_BLUE)
    ws.format("A11:F11", HEADER_GRAY)
    ws.format("A13:F13", HEADER_GREEN)
    ws.format("B5:D11", NUM_EUR)
    ws.format("E5:E10", NUM_PCT)
    ws.format("C15:E16", NUM_EUR)
    ws.format("C17:E18", NUM_PCT)
    print("    ✓ Done")


def main():
    print("=" * 60)
    print("🚀 CREATING ADVANCED DASHBOARDS")
    print("=" * 60)

    gc = get_client()
    spreadsheet = gc.open_by_key(SPREADSHEET_ID)
    print(f"\nSpreadsheet: {spreadsheet.title}")
    print("\nCreating sheets...")

    create_kpi_dashboard(spreadsheet)
    create_monthly_trends(spreadsheet)
    create_scenario_builder(spreadsheet)
    create_bu_breakdown(spreadsheet)

    print("\n" + "=" * 60)
    print("✅ ALL DASHBOARDS CREATED!")
    print(f"\n📊 Open: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")
    print("\n📋 New Sheets:")
    print("  - 📊 KPI_2025: Key metrics summary")
    print("  - 📈 Trends: Monthly & cumulative trends")
    print("  - 🔮 Scenario_2026: Projection builder (edit yellow cells!)")
    print("  - 🏢 BU_Detail: Business unit breakdown")
    print("=" * 60)


if __name__ == "__main__":
    main()
