/**
 * HotelOPS Advanced Dashboard - Google Apps Script
 *
 * SETUP:
 * 1. Apri lo spreadsheet Budget_Mensile
 * 2. Estensioni > Apps Script
 * 3. Incolla questo codice
 * 4. Salva ed esegui setupAdvancedDashboard()
 */

// ============================================================
// MENU
// ============================================================
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🏨 HotelOPS')
    .addItem('📊 Setup Dashboard Completo', 'setupAdvancedDashboard')
    .addSeparator()
    .addItem('📈 Aggiorna KPI', 'createKPIDashboard')
    .addItem('📉 Aggiorna Trends', 'createTrendsDashboard')
    .addItem('🔮 Aggiorna Scenari 2026', 'createScenarioBuilder')
    .addItem('🏢 Aggiorna BU Analysis', 'createBUAnalysis')
    .addSeparator()
    .addItem('🎨 Formatta Tutto', 'formatAllSheets')
    .addToUi();
}

// ============================================================
// MAIN SETUP
// ============================================================
function setupAdvancedDashboard() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  SpreadsheetApp.getUi().showModalDialog(
    HtmlService.createHtmlOutput('<p>Creazione dashboard in corso...</p>').setWidth(300).setHeight(100),
    'Setup'
  );

  createKPIDashboard();
  createTrendsDashboard();
  createScenarioBuilder();
  createBUAnalysis();
  formatAllSheets();

  SpreadsheetApp.getUi().alert('✅ Dashboard creato!\n\nNuovi fogli:\n- 📊 KPI_2025\n- 📈 Trends\n- 🔮 Scenario_2026\n- 🏢 BU_Detail');
}

// ============================================================
// UTILITIES
// ============================================================
function getOrCreateSheet(ss, name, rows, cols) {
  let sheet = ss.getSheetByName(name);
  if (!sheet) {
    sheet = ss.insertSheet(name);
  }
  sheet.clear();
  return sheet;
}

function setHeader(sheet, range, text, bgColor) {
  const cell = sheet.getRange(range);
  cell.setValue(text);
  cell.setFontWeight('bold');
  cell.setFontSize(12);
  if (bgColor) {
    cell.setBackground(bgColor);
    cell.setFontColor('white');
  }
}

// ============================================================
// KPI DASHBOARD
// ============================================================
function createKPIDashboard() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = getOrCreateSheet(ss, '📊 KPI_2025', 35, 10);

  // Title
  sheet.getRange('A1').setValue('🏨 HOTELOPS - KPI DASHBOARD 2025').setFontSize(16).setFontWeight('bold');

  // KEY METRICS
  sheet.getRange('A3').setValue('📈 KEY METRICS').setFontWeight('bold').setBackground('#3366cc').setFontColor('white');
  sheet.getRange('C3:E3').setValues([['ORTI', 'INTUR', 'CONSOLIDATO']]).setFontWeight('bold').setBackground('#3366cc').setFontColor('white');

  const metrics = [
    ['Ricavi Totali', '=SUM(ORTI_Dashboard!H2:H13)', '=SUM(INTUR_Dashboard!H2:H13)', '=C5+D5'],
    ['Costi Totali', '=SUM(ORTI_Dashboard!L2:L13)', '=SUM(INTUR_Dashboard!L2:L13)', '=C6+D6'],
    ['EBITDA', '=C5-C6', '=D5-D6', '=E5-E6'],
    ['Margine EBITDA %', '=IF(C5=0,0,C7/C5)', '=IF(D5=0,0,D7/D5)', '=IF(E5=0,0,E7/E5)']
  ];
  sheet.getRange('A5:D8').setValues(metrics);
  sheet.getRange('C5:E7').setNumberFormat('€#,##0');
  sheet.getRange('C8:E8').setNumberFormat('0.0%');

  // REVENUE BY BU
  sheet.getRange('A10').setValue('💰 RICAVI PER BU').setFontWeight('bold').setBackground('#109618').setFontColor('white');
  sheet.getRange('C10:F10').setValues([['ORTI', 'INTUR', 'TOTALE', '% Mix']]).setFontWeight('bold').setBackground('#109618').setFontColor('white');

  const buData = [
    ['Hotel', '=SUM(ORTI_Dashboard!B2:B13)', '=SUM(INTUR_Dashboard!B2:B13)', '=C12+D12', '=IF($E$5=0,0,E12/$E$5)'],
    ['Angelina', '=SUM(ORTI_Dashboard!C2:C13)', '=SUM(INTUR_Dashboard!C2:C13)', '=C13+D13', '=IF($E$5=0,0,E13/$E$5)'],
    ['CVM', '=SUM(ORTI_Dashboard!D2:D13)', '=SUM(INTUR_Dashboard!D2:D13)', '=C14+D14', '=IF($E$5=0,0,E14/$E$5)'],
    ['F&B', '=SUM(ORTI_Dashboard!E2:E13)', '=SUM(INTUR_Dashboard!E2:E13)', '=C15+D15', '=IF($E$5=0,0,E15/$E$5)'],
    ['Spiaggia', '=SUM(ORTI_Dashboard!F2:F13)', '=SUM(INTUR_Dashboard!F2:F13)', '=C16+D16', '=IF($E$5=0,0,E16/$E$5)'],
    ['Altri', '=SUM(ORTI_Dashboard!G2:G13)', '=SUM(INTUR_Dashboard!G2:G13)', '=C17+D17', '=IF($E$5=0,0,E17/$E$5)']
  ];
  sheet.getRange('A12:E17').setValues(buData);
  sheet.getRange('C12:E17').setNumberFormat('€#,##0');
  sheet.getRange('F12:F17').setNumberFormat('0.0%');

  // COST STRUCTURE
  sheet.getRange('A19').setValue('📉 STRUTTURA COSTI').setFontWeight('bold').setBackground('#dc3912').setFontColor('white');
  sheet.getRange('C19:F19').setValues([['ORTI', 'INTUR', 'TOTALE', '% Ricavi']]).setFontWeight('bold').setBackground('#dc3912').setFontColor('white');

  const costData = [
    ['Costi Fissi', '=SUM(ORTI_Dashboard!I2:I13)', '=SUM(INTUR_Dashboard!I2:I13)', '=C21+D21', '=IF($E$5=0,0,E21/$E$5)'],
    ['Costi Variabili', '=SUM(ORTI_Dashboard!J2:J13)', '=SUM(INTUR_Dashboard!J2:J13)', '=C22+D22', '=IF($E$5=0,0,E22/$E$5)'],
    ['Personale', '=SUM(ORTI_Dashboard!K2:K13)', '=SUM(INTUR_Dashboard!K2:K13)', '=C23+D23', '=IF($E$5=0,0,E23/$E$5)']
  ];
  sheet.getRange('A21:E23').setValues(costData);
  sheet.getRange('C21:E23').setNumberFormat('€#,##0');
  sheet.getRange('F21:F23').setNumberFormat('0.0%');

  // SEASONALITY
  sheet.getRange('A25').setValue('🌞 STAGIONALITÀ').setFontWeight('bold').setBackground('#ff9900');
  sheet.getRange('C25:E25').setValues([['Alta (Giu-Set)', 'Bassa (Resto)', 'Ratio']]).setFontWeight('bold').setBackground('#ff9900');

  const seasonData = [
    ['Ricavi', '=SUM(ORTI_Dashboard!H7:H10)+SUM(INTUR_Dashboard!H7:H10)', '=SUM(ORTI_Dashboard!H2:H6)+SUM(ORTI_Dashboard!H11:H13)+SUM(INTUR_Dashboard!H2:H6)+SUM(INTUR_Dashboard!H11:H13)', '=IF(D27=0,0,C27/D27)'],
    ['EBITDA', '=SUM(ORTI_Dashboard!M7:M10)+SUM(INTUR_Dashboard!M7:M10)', '=SUM(ORTI_Dashboard!M2:M6)+SUM(ORTI_Dashboard!M11:M13)+SUM(INTUR_Dashboard!M2:M6)+SUM(INTUR_Dashboard!M11:M13)', '=IF(D28=0,0,C28/D28)']
  ];
  sheet.getRange('A27:D28').setValues(seasonData);
  sheet.getRange('C27:D28').setNumberFormat('€#,##0');
  sheet.getRange('E27:E28').setNumberFormat('0.0x');

  // Freeze
  sheet.setFrozenRows(1);
  sheet.autoResizeColumns(1, 6);
}

// ============================================================
// TRENDS DASHBOARD
// ============================================================
function createTrendsDashboard() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = getOrCreateSheet(ss, '📈 Trends', 15, 15);

  sheet.getRange('A1').setValue('📈 TREND MENSILI CONSOLIDATO 2025').setFontSize(16).setFontWeight('bold');

  // Headers
  const months = ['', 'Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic', 'TOTALE'];
  sheet.getRange('A3:N3').setValues([months]).setFontWeight('bold').setBackground('#3366cc').setFontColor('white');

  // Revenue row
  const ricaviFormulas = ['Ricavi'];
  for (let i = 2; i <= 13; i++) {
    ricaviFormulas.push(`=ORTI_Dashboard!H${i}+INTUR_Dashboard!H${i}`);
  }
  ricaviFormulas.push('=SUM(B4:M4)');
  sheet.getRange('A4:N4').setValues([ricaviFormulas]);

  // Costs row
  const costiFormulas = ['Costi'];
  for (let i = 2; i <= 13; i++) {
    costiFormulas.push(`=ORTI_Dashboard!L${i}+INTUR_Dashboard!L${i}`);
  }
  costiFormulas.push('=SUM(B5:M5)');
  sheet.getRange('A5:N5').setValues([costiFormulas]);

  // EBITDA row
  const ebitdaFormulas = ['EBITDA'];
  for (let col = 'B'.charCodeAt(0); col <= 'N'.charCodeAt(0); col++) {
    const c = String.fromCharCode(col);
    ebitdaFormulas.push(`=${c}4-${c}5`);
  }
  sheet.getRange('A6:N6').setValues([ebitdaFormulas]);

  // Margin row
  const marginFormulas = ['Margine %'];
  for (let col = 'B'.charCodeAt(0); col <= 'N'.charCodeAt(0); col++) {
    const c = String.fromCharCode(col);
    marginFormulas.push(`=IF(${c}4=0,0,${c}6/${c}4)`);
  }
  sheet.getRange('A7:N7').setValues([marginFormulas]);

  // YTD Cumulative
  sheet.getRange('A9:M9').setValues([['YTD CUMULATO', 'Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic']]);
  sheet.getRange('A9:M9').setFontWeight('bold').setBackground('#f3f3f3');

  const ricaviCum = ['Ricavi Cum.', '=B4'];
  for (let i = 3; i <= 13; i++) {
    const prev = String.fromCharCode(64 + i - 1);
    const curr = String.fromCharCode(64 + i);
    ricaviCum.push(`=${prev}10+${curr}4`);
  }
  sheet.getRange('A10:M10').setValues([ricaviCum]);

  const ebitdaCum = ['EBITDA Cum.', '=B6'];
  for (let i = 3; i <= 13; i++) {
    const prev = String.fromCharCode(64 + i - 1);
    const curr = String.fromCharCode(64 + i);
    ebitdaCum.push(`=${prev}11+${curr}6`);
  }
  sheet.getRange('A11:M11').setValues([ebitdaCum]);

  // Formatting
  sheet.getRange('B4:N6').setNumberFormat('€#,##0');
  sheet.getRange('B7:N7').setNumberFormat('0.0%');
  sheet.getRange('B10:M11').setNumberFormat('€#,##0');

  // Conditional formatting for EBITDA
  const ebitdaRange = sheet.getRange('B6:M6');
  const positiveRule = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberGreaterThan(0)
    .setBackground('#c6efce')
    .setRanges([ebitdaRange])
    .build();
  const negativeRule = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberLessThan(0)
    .setBackground('#ffc7ce')
    .setRanges([ebitdaRange])
    .build();
  sheet.setConditionalFormatRules([positiveRule, negativeRule]);

  sheet.autoResizeColumns(1, 14);
}

// ============================================================
// SCENARIO BUILDER 2026
// ============================================================
function createScenarioBuilder() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = getOrCreateSheet(ss, '🔮 Scenario_2026', 50, 12);

  sheet.getRange('A1').setValue('🔮 SCENARIO BUILDER 2026').setFontSize(16).setFontWeight('bold');

  // Parameters section
  sheet.getRange('A3').setValue('⚙️ PARAMETRI (modifica celle gialle)').setFontWeight('bold');

  const params = [
    ['Crescita Ricavi %', '5%'],
    ['Δ Costi Fissi %', '3%'],
    ['Δ Costi Variabili %', '4%'],
    ['Δ Personale %', '5%']
  ];
  sheet.getRange('A5:B8').setValues(params);
  sheet.getRange('B5:B8').setBackground('#fff2cc').setNumberFormat('0%');

  // Baseline 2025
  sheet.getRange('A11').setValue('📊 BASELINE 2025').setFontWeight('bold').setBackground('#3366cc').setFontColor('white');
  sheet.getRange('C11:E11').setValues([['ORTI', 'INTUR', 'CONSOLIDATO']]).setFontWeight('bold').setBackground('#3366cc').setFontColor('white');

  const baseline = [
    ['Ricavi', '=SUM(ORTI_Dashboard!H2:H13)', '=SUM(INTUR_Dashboard!H2:H13)', '=C13+D13'],
    ['Costi Fissi', '=SUM(ORTI_Dashboard!I2:I13)', '=SUM(INTUR_Dashboard!I2:I13)', '=C14+D14'],
    ['Costi Variabili', '=SUM(ORTI_Dashboard!J2:J13)', '=SUM(INTUR_Dashboard!J2:J13)', '=C15+D15'],
    ['Personale', '=SUM(ORTI_Dashboard!K2:K13)', '=SUM(INTUR_Dashboard!K2:K13)', '=C16+D16'],
    ['Costi Totali', '=C14+C15+C16', '=D14+D15+D16', '=E14+E15+E16'],
    ['EBITDA', '=C13-C17', '=D13-D17', '=E13-E17'],
    ['Margine %', '=IF(C13=0,0,C18/C13)', '=IF(D13=0,0,D18/D13)', '=IF(E13=0,0,E18/E13)']
  ];
  sheet.getRange('A13:D19').setValues(baseline);
  sheet.getRange('C13:E18').setNumberFormat('€#,##0');
  sheet.getRange('C19:E19').setNumberFormat('0.0%');

  // Projection 2026
  sheet.getRange('A21').setValue('🚀 PROIEZIONE 2026').setFontWeight('bold').setBackground('#109618').setFontColor('white');
  sheet.getRange('C21:G21').setValues([['ORTI', 'INTUR', 'CONSOLIDATO', 'Δ €', 'Δ %']]).setFontWeight('bold').setBackground('#109618').setFontColor('white');

  const projection = [
    ['Ricavi', '=C13*(1+$B$5)', '=D13*(1+$B$5)', '=C23+D23', '=E23-E13', '=IF(E13=0,0,F23/E13)'],
    ['Costi Fissi', '=C14*(1+$B$6)', '=D14*(1+$B$6)', '=C24+D24', '=E24-E14', '=IF(E14=0,0,F24/E14)'],
    ['Costi Variabili', '=C15*(1+$B$7)', '=D15*(1+$B$7)', '=C25+D25', '=E25-E15', '=IF(E15=0,0,F25/E15)'],
    ['Personale', '=C16*(1+$B$8)', '=D16*(1+$B$8)', '=C26+D26', '=E26-E16', '=IF(E16=0,0,F26/E16)'],
    ['Costi Totali', '=C24+C25+C26', '=D24+D25+D26', '=E24+E25+E26', '=E27-E17', '=IF(E17=0,0,F27/E17)'],
    ['EBITDA', '=C23-C27', '=D23-D27', '=E23-E27', '=E28-E18', '=IF(E18=0,0,F28/E18)'],
    ['Margine %', '=IF(C23=0,0,C28/C23)', '=IF(D23=0,0,D28/D23)', '=IF(E23=0,0,E28/E23)', '=E29-E19', '']
  ];
  sheet.getRange('A23:F29').setValues(projection);
  sheet.getRange('C23:E28').setNumberFormat('€#,##0');
  sheet.getRange('F23:F28').setNumberFormat('+€#,##0;-€#,##0');
  sheet.getRange('G23:G28').setNumberFormat('+0.0%;-0.0%');
  sheet.getRange('C29:E29').setNumberFormat('0.0%');

  // Quick Scenarios
  sheet.getRange('A31').setValue('📋 SCENARI RAPIDI').setFontWeight('bold').setBackground('#ff9900');
  sheet.getRange('C31:F31').setValues([['Conservative', 'Base', 'Optimistic', 'Aggressive']]).setFontWeight('bold').setBackground('#ff9900');

  const scenarios = [
    ['Crescita Ricavi', '2%', '5%', '8%', '12%'],
    ['Δ Costi', '2%', '4%', '5%', '7%'],
    ['', '', '', '', ''],
    ['EBITDA 2026', '=E13*(1+C33)-E17*(1+C34)', '=E13*(1+D33)-E17*(1+D34)', '=E13*(1+E33)-E17*(1+E34)', '=E13*(1+F33)-E17*(1+F34)'],
    ['Margine %', '=IF(E13*(1+C33)=0,0,C36/(E13*(1+C33)))', '=IF(E13*(1+D33)=0,0,D36/(E13*(1+D33)))', '=IF(E13*(1+E33)=0,0,E36/(E13*(1+E33)))', '=IF(E13*(1+F33)=0,0,F36/(E13*(1+F33)))'],
    ['Δ vs 2025', '=C36-E18', '=D36-E18', '=E36-E18', '=F36-E18']
  ];
  sheet.getRange('A33:E38').setValues(scenarios);
  sheet.getRange('C33:F34').setNumberFormat('0%');
  sheet.getRange('C36:F36').setNumberFormat('€#,##0').setFontWeight('bold');
  sheet.getRange('C37:F37').setNumberFormat('0.0%');
  sheet.getRange('C38:F38').setNumberFormat('+€#,##0;-€#,##0');

  // Highlight EBITDA improvement
  sheet.getRange('C36:F36').setBackground('#e6f2e6');
  sheet.getRange('A28:E28').setBackground('#e6f2e6');

  sheet.setFrozenRows(1);
  sheet.autoResizeColumns(1, 7);
}

// ============================================================
// BU ANALYSIS
// ============================================================
function createBUAnalysis() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = getOrCreateSheet(ss, '🏢 BU_Detail', 25, 10);

  sheet.getRange('A1').setValue('🏢 DETTAGLIO BUSINESS UNIT 2025').setFontSize(16).setFontWeight('bold');

  // BU Breakdown
  sheet.getRange('A3:F3').setValues([['BU', 'ORTI', 'INTUR', 'TOTALE', '% Mix', 'Peak']]);
  sheet.getRange('A3:F3').setFontWeight('bold').setBackground('#3366cc').setFontColor('white');

  const buData = [
    ['Hotel', '=SUM(ORTI_Dashboard!B2:B13)', '=SUM(INTUR_Dashboard!B2:B13)', '=B5+C5', '=IF($D$11=0,0,D5/$D$11)', 'Lug-Set'],
    ['Angelina', '=SUM(ORTI_Dashboard!C2:C13)', '=SUM(INTUR_Dashboard!C2:C13)', '=B6+C6', '=IF($D$11=0,0,D6/$D$11)', 'Lug-Set'],
    ['CVM', '=SUM(ORTI_Dashboard!D2:D13)', '=SUM(INTUR_Dashboard!D2:D13)', '=B7+C7', '=IF($D$11=0,0,D7/$D$11)', 'Lug-Set'],
    ['F&B', '=SUM(ORTI_Dashboard!E2:E13)', '=SUM(INTUR_Dashboard!E2:E13)', '=B8+C8', '=IF($D$11=0,0,D8/$D$11)', 'Agosto'],
    ['Spiaggia', '=SUM(ORTI_Dashboard!F2:F13)', '=SUM(INTUR_Dashboard!F2:F13)', '=B9+C9', '=IF($D$11=0,0,D9/$D$11)', 'Lug-Ago'],
    ['Altri', '=SUM(ORTI_Dashboard!G2:G13)', '=SUM(INTUR_Dashboard!G2:G13)', '=B10+C10', '=IF($D$11=0,0,D10/$D$11)', 'Variabile'],
    ['TOTALE', '=SUM(B5:B10)', '=SUM(C5:C10)', '=SUM(D5:D10)', '100%', '']
  ];
  sheet.getRange('A5:F11').setValues(buData);
  sheet.getRange('B5:D11').setNumberFormat('€#,##0');
  sheet.getRange('E5:E10').setNumberFormat('0.0%');
  sheet.getRange('A11:F11').setFontWeight('bold').setBackground('#f3f3f3');

  // ORTI vs INTUR Comparison
  sheet.getRange('A13:E13').setValues([['ORTI vs INTUR', '', 'ORTI', 'INTUR', 'Δ']]);
  sheet.getRange('A13:E13').setFontWeight('bold').setBackground('#109618').setFontColor('white');

  const comparison = [
    ['Ricavi Totali', '', '=SUM(ORTI_Dashboard!H2:H13)', '=SUM(INTUR_Dashboard!H2:H13)', '=C15-D15'],
    ['EBITDA', '', '=SUM(ORTI_Dashboard!M2:M13)', '=SUM(INTUR_Dashboard!M2:M13)', '=C16-D16'],
    ['Margine %', '', '=IF(C15=0,0,C16/C15)', '=IF(D15=0,0,D16/D15)', '=C17-D17'],
    ['Personale/Ricavi', '', '=IF(C15=0,0,SUM(ORTI_Dashboard!K2:K13)/C15)', '=IF(D15=0,0,SUM(INTUR_Dashboard!K2:K13)/D15)', '=C18-D18']
  ];
  sheet.getRange('A15:E18').setValues(comparison);
  sheet.getRange('C15:E16').setNumberFormat('€#,##0');
  sheet.getRange('C17:E18').setNumberFormat('0.0%');

  sheet.autoResizeColumns(1, 6);
}

// ============================================================
// FORMATTING
// ============================================================
function formatAllSheets() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  ['ORTI_Dashboard', 'INTUR_Dashboard'].forEach(name => {
    const sheet = ss.getSheetByName(name);
    if (sheet) {
      // Header
      sheet.getRange('1:1').setFontWeight('bold').setBackground('#4472c4').setFontColor('white');
      sheet.setFrozenRows(1);
      sheet.setFrozenColumns(1);

      // Number format for data
      const lastRow = sheet.getLastRow();
      const lastCol = sheet.getLastColumn();
      if (lastRow > 1 && lastCol > 1) {
        sheet.getRange(2, 2, lastRow - 1, lastCol - 1).setNumberFormat('#,##0.00');
      }

      // Auto-resize
      for (let i = 1; i <= lastCol; i++) {
        sheet.autoResizeColumn(i);
      }
    }
  });
}
