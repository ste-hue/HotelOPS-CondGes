# CondGes - Hotel Analytics Dashboard

Sistema semplificato per l'analisi dei dati di hotel multipli da file XML.

## 🚀 Quick Start

```bash
# Installa le dipendenze
pip install -r requirements.txt

# Avvia il dashboard
streamlit run condges_dashboard.py
```

## 📊 Funzionalità

- **Caricamento Multi-File**: Carica più file XML contemporaneamente
- **Confronto Anno su Anno**: Visualizza trend e variazioni percentuali
- **Analisi Ricavi**: Breakdown per categoria e trend mensili
- **Heatmap Occupazione**: Visualizzazione grafica dell'occupazione camere
- **Export Dati**: Scarica i dati filtrati in formato CSV

## 📁 Formati Supportati

### Produzione Giornaliera (HotelCube)
File XML con struttura `matrix1_Data` contenenti:
- Dati giornalieri di occupazione
- Ricavi per categoria
- Numero ospiti (adulti, bambini)

### Segmenti Cliente (HotelCube)
File XML con struttura `table1_Group3` contenenti:
- Analisi per segmento/nazionalità
- Confronti periodo corrente vs precedente

## 💡 Utilizzo

1. Clicca su "Seleziona file XML" nella sidebar
2. Carica uno o più file
3. Clicca "Analizza" per processare i dati
4. Usa i filtri per hotel e periodo
5. Esplora le diverse tab per analisi dettagliate

## 📋 Requisiti

- Python 3.8+
- streamlit
- pandas
- plotly

## 📂 Struttura Progetto

```
CondGes/
├── condges_dashboard.py    # Dashboard principale
├── requirements.txt        # Dipendenze Python
├── README.md              # Questo file
└── Data/                  # Directory dati (opzionale)
    ├── HotelCube/
    ├── MPS/
    └── NEXI/
```
