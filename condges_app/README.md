# CONDGES V4.0 - Dashboard Finanziario Dinamico

Dashboard web dinamico per l'analisi finanziaria del Gruppo Panorama (Hotel, Residence Angelina, CVM) con backend Flask e database Supabase.

## 🚀 Caratteristiche

- **Dashboard Dinamico**: Interfaccia web responsive con grafici interattivi
- **Backend Flask**: API RESTful per operazioni CRUD sui dati finanziari
- **Database Supabase**: Storage cloud con calcoli automatici
- **Grafici Real-time**: Visualizzazioni con Chart.js
- **Filtri Avanzati**: Per anno, asset e periodo
- **Mobile Responsive**: Ottimizzato per tutti i dispositivi

## 📊 Funzionalità

### Dashboard Features
- ✅ KPI Cards con confronti anno/anno
- ✅ Grafici ricavi mensili per asset
- ✅ Grafici margini percentuali
- ✅ Tabelle dettagliate mensili
- ✅ Confronti annuali
- ✅ Filtri dinamici per anno e asset
- ✅ Indicatore stato connessione database

### API Endpoints
- `GET /api/assets` - Lista degli asset
- `GET /api/monthly` - Dati mensili (con filtri)
- `GET /api/annual` - Riepiloghi annuali
- `GET /api/summary` - Dashboard summary completo
- `GET /api/health` - Health check del sistema

## 🛠 Installazione

### Prerequisiti
- Python 3.8+
- Virtual environment (consigliato)
- Account Supabase configurato

### Setup

1. **Installa le dipendenze**:
```bash
cd condges_app
pip install -r requirements.txt
```

2. **Configura le variabili d'ambiente** (opzionale):
```bash
export FLASK_ENV=development  # Per development
export PORT=5000              # Porta personalizzata
export HOST=0.0.0.0          # Host personalizzato
```

3. **Avvia l'applicazione**:
```bash
# Metodo 1: Script di avvio
python run.py

# Metodo 2: Direttamente con Flask
python app.py

# Metodo 3: Con Gunicorn (produzione)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

4. **Accedi al dashboard**:
   - Apri il browser su `http://localhost:5000`

## 📁 Struttura del Progetto

```
condges_app/
├── app.py                 # Main Flask application
├── run.py                 # Production runner script
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── dashboard.html    # Main dashboard template
├── static/
│   ├── css/
│   │   └── dashboard.css # Dashboard styling
│   └── js/
│       └── dashboard.js  # Dashboard logic
├── api/                  # API modules (future expansion)
└── config/              # Configuration files (future)
```

## 🔧 Configurazione

### Supabase Connection
Le credenziali Supabase sono configurate in `app.py`:
- URL: `https://udeavsfewakatewsphfw.supabase.co`
- Chiave anonima inclusa nel codice

### Database Schema
Il sistema utilizza le seguenti tabelle in Supabase:
- `condges_assets` - Informazioni sugli asset
- `condges_monthly_financials` - Dati finanziari mensili
- `condges_annual_summaries` - Riepiloghi annuali
- `condges_dashboard_data` - Vista per il dashboard

## 🚀 Deployment

### Sviluppo
```bash
python run.py
```

### Produzione
```bash
# Con Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Con Docker (futuro)
docker build -t condges-dashboard .
docker run -p 8000:8000 condges-dashboard
```

### Environment Variables
- `FLASK_ENV`: `development` o `production`
- `PORT`: Porta del server (default: 5000)
- `HOST`: Host del server (default: 0.0.0.0)

## 📊 API Usage

### Esempi di chiamate API

```javascript
// Ottenere tutti gli asset
fetch('/api/assets')
  .then(response => response.json())
  .then(data => console.log(data));

// Filtrare dati per anno
fetch('/api/monthly?year=2025')
  .then(response => response.json())
  .then(data => console.log(data));

// Ottenere summary completo
fetch('/api/summary')
  .then(response => response.json())
  .then(data => console.log(data));
```

## 🔍 Troubleshooting

### Problemi Comuni

1. **Errore connessione database**:
   - Verificare credenziali Supabase
   - Controllare connessione internet
   - Verificare health endpoint: `/api/health`

2. **Dati non visualizzati**:
   - Verificare migrazione dati completata
   - Controllare console browser per errori JavaScript
   - Verificare endpoint API funzionanti

3. **Errori di permessi**:
   - Verificare RLS policies in Supabase
   - Controllare chiave API corretta

### Log e Debug
- I log sono visibili nella console del server
- Attivare debug mode con `FLASK_ENV=development`
- Controllare Network tab nel browser per errori API

## 🔄 Aggiornamenti

Per aggiornare i dati:
1. Eseguire nuovamente `migrate_to_supabase.py`
2. Il dashboard si aggiornerà automaticamente
3. Utilizzare il pulsante "🔄 Aggiorna" nell'interfaccia

## 📝 Note Tecniche

- **Frontend**: HTML5, CSS3, JavaScript ES6+, Chart.js, Axios
- **Backend**: Flask 3.0, Python 3.8+
- **Database**: Supabase (PostgreSQL)
- **Styling**: CSS Grid, Flexbox, Responsive Design
- **Charts**: Chart.js per visualizzazioni interattive









