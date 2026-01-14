# CondGes - Dashboard Contabilità 2025

## GOAL
Dashboard Google Apps Script:
- Ricavi mensili per BU (Hotel, Angelina, CVM, Spiaggia, F&B)
- Costi mensili: Fissi / Variabili / Personale
- 2025 consuntivo ORTI + INTUR
- 2026 proiezione

## FILE STRUTTURA
```
data/
├── ORTI_mesepermese.xlsx
├── INTUR_mesepermese.xlsx
└── personale/
    ├── Modello_PC_Orti.xlsx
    ├── PROSPETTO ORTI/
    │   ├── ORT_PC_MM_YYYY.xlsx      (dipendenti)
    │   ├── ORT_PCSTAG_MM_YYYY.xlsx  (stagionali)
    │   └── ORT_PC_14_YYYY.xlsx      (13ma/14ma)
    └── PROSPETTO INTUR/
        ├── INT_PC_MM_YYYY.xlsx      (dipendenti)
        ├── INT_PCCOLLAB_MM_YYYY.xlsx (collaboratori)
        ├── INT_PCSTAG_MM_YYYY.xlsx  (stagionali)
        └── INT_PC_14_YYYY.xlsx      (13ma/14ma)
```

## PERSONALE - REGOLE ESTRAZIONE
**Fonte:** file `*_PC_*.xlsx` dai Prospetti Contabili (NON 67.* contabile)

**Filtro:** `Tipo conto = 'E'` (Economico)

### VOCI INCLUSE:
| Categoria | Voci |
|-----------|------|
| Retribuzioni | Retribuzioni, Retrib. Stage |
| Rimborsi | Trasferte, Rimborso spese Km extracomune |
| Contributi | Contributi Inps, Contributi ASPI Inps, Recupero contributi Inps (netto Dare-Avere) |
| INAIL | Premio Inail mese, Premio Inail retrib.differite |
| Accantonamenti | Accanton. 13ma, Accanton. 14ma, Accanton. TFR mese, Accanton. TFR retrib.differite |
| Oneri previdenziali | Oneri previd. Accant. 13ma, Oneri previd. Accant. 14ma |

### VOCI ESCLUSE:
| Voce | Motivo |
|------|--------|
| Accanton. Ferie | Accantonamento temporaneo, non costo effettivo |
| Accanton. R.O.L. | Accantonamento temporaneo, non costo effettivo |
| Oneri previd. Ferie/ROL | Correlati a ferie/ROL |
| Rec.0,50% Fondo TFR | Partita di giro (Dare = Avere) |
| Tipo conto = 'P' | Patrimoniale, non economico |

### OUTPUT 2025 (gen-ago):
```
Mese  INTUR       ORTI        TOTALE
1     €21,207     €0          €21,207
2     €19,728     €0          €19,728
3     €16,380     €26,878     €43,258
4     €2,780      €84,218     €86,997
5     €3,245      €114,984    €118,229
6     €14,358     €125,010    €139,368
7     €15,853     €133,745    €149,598
8     €14,196     €128,348    €142,544
─────────────────────────────────────
TOT   €107,747    €613,182    €720,929
```

## RICAVI PER BU
| Conto | BU |
|-------|-----|
| 48.31.00 | Hotel |
| 48.32.00 | Angelina |
| 48.33.00 | CVM |
| 48.34.00 | Spiaggia |
| 48.35.00 | Affitti |

## COSTI FISSI
55.07.*, 57.01.51.*, 57.05.*, 57.09.01/09/90, 57.11.*, 59.*, 61.*, 63.*, 65.*, 66.*, 71.*

## COSTI VARIABILI
55.01.*, 55.03.*, 57.01.* (escluso 51.*), 57.09.01-05 (utenze)

## REGOLE BUSINESS
- ORTI: gestione operativa
- INTUR: fitto + spiaggia esterni, paga 480K a privato
- Personale = VARIABILE (stagionale)
- 75.* = ESCLUSO EBITDA

## VINCOLI 2026
- Tasse extra: €200k/anno
- Investimento spiaggia: €500k
- Nuove camere: +10% ricavi
- Stagione: 1 apr – 15 ott
