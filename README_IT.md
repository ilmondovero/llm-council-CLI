# LLM Council

![LLM Council](header.jpg)

Italiano | [Read in English](README.md)

Un sistema locale di deliberazione multi-modello basato su CLI che riunisce Google Gemini, OpenAI Codex e Anthropic Claude per rispondere collaborativamente alle tue domande attraverso un processo strutturato in 3 fasi.

## Panoramica

Invece di chiedere a un singolo LLM una risposta, LLM Council orchestra un processo di deliberazione collaborativa tra più modelli AI. Il sistema implementa un framework decisionale strutturato:

### Il Processo in 3 Fasi

#### Fase 1: Risposte Individuali
Ogni membro del consiglio (Gemini, Codex, Claude) analizza indipendentemente la tua domanda e fornisce la propria risposta. Questo garantisce prospettive diverse senza pensiero di gruppo o bias.

#### Fase 2: Revisione Anonima tra Pari
Le risposte vengono anonimizzate (etichettate come Risposta A, Risposta B, Risposta C) e ridistribuite a tutti i membri del consiglio. Ogni modello esamina e classifica tutte le risposte in base a precisione, intuizione e completezza - senza sapere quale modello ha prodotto quale risposta.

#### Fase 3: Sintesi del Presidente
Il modello Presidente designato (per default, Gemini) esamina tutte le risposte individuali e le classifiche tra pari per sintetizzare una risposta finale e completa che rappresenta la saggezza collettiva del consiglio.

## Caratteristiche Principali

- **Intelligenza Multi-Modello**: Sfrutta i punti di forza di Google Gemini, OpenAI Codex (GPT/o-series) e Anthropic Claude
- **Nessuna Chiave API Richiesta**: Utilizza strumenti CLI locali con i tuoi abbonamenti esistenti - non servono OpenRouter o chiavi API aggiuntive
- **Privacy-First**: Tutta l'elaborazione avviene localmente tramite sottoprocessi CLI
- **Processo Trasparente**: Visualizza tutte le risposte individuali, le classifiche tra pari e il processo di sintesi
- **Cronologia Conversazioni**: Salvata e recuperabile automaticamente
- **UI Moderna**: Frontend React pulito con risposte in streaming in tempo reale

## Prerequisiti

Prima di eseguire LLM Council, devi installare e autenticare tre strumenti CLI:

- **Gemini CLI** (Google)
- **Codex CLI** (OpenAI)
- **Claude CLI** (Anthropic)

Vedi la guida completa all'installazione: [docs/INSTALL_CLI.md](docs/INSTALL_CLI.md)

## Avvio Rapido

### 1. Installa le Dipendenze

Il progetto utilizza Python 3.10+ per il backend e Node.js per il frontend.

**Installa le dipendenze Python:**
```bash
pip install fastapi uvicorn httpx pydantic
```

Oppure usando uv (consigliato):
```bash
uv sync
```

**Installa le dipendenze frontend:**
```bash
cd frontend
npm install
cd ..
```

### 2. Avvia l'Applicazione

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
./start.sh
```

Questo:
- Avvia il backend FastAPI su http://localhost:8001
- Avvia il frontend React su http://localhost:5173
- Apre automaticamente il browser

### 3. Inizia a Fare Domande

Naviga su http://localhost:5173 e inizia una conversazione. Guarda come i tre modelli rispondono indipendentemente, esaminano il lavoro degli altri e producono una risposta finale sintetizzata.

## Utilizzo

### Avviare una Conversazione

1. Clicca "New Conversation" nella barra laterale
2. Digita la tua domanda nel campo di input
3. Premi Invio o clicca Invia

### Visualizzare le Risposte

L'interfaccia mostra tutte e tre le fasi:

- **Schede Fase 1**: Scorri le risposte individuali di Gemini, Codex e Claude
- **Classifiche Fase 2**: Vedi come ogni modello ha classificato gli altri (con punteggi aggregati)
- **Risposta Finale Fase 3**: La risposta sintetizzata del Presidente

### Gestire le Conversazioni

- Clicca qualsiasi conversazione nella barra laterale per visualizzare la cronologia
- Le conversazioni vengono titolate automaticamente in base al tuo primo messaggio
- Tutti i dati sono memorizzati localmente in `data/conversations/`

## Configurazione

### Variabili d'Ambiente

Crea un file `.env` nella root del progetto (opzionale):

```bash
# Configurazione server API
PORT=8001                                    # Porta backend (default: 8001)
CORS_ORIGINS=http://localhost:5173          # Origini CORS consentite

# Configurazione consiglio (avanzato - vedi invece backend/config.py)
```

### Configurazione del Consiglio

Modifica `backend/config.py` per personalizzare il consiglio:

```python
# Membri del consiglio - identificatori CLI
COUNCIL_MODELS = [
    "gemini",   # Google Gemini via Gemini CLI
    "codex",    # OpenAI GPT via Codex CLI
    "claude",   # Anthropic Claude via Claude CLI
]

# Modello presidente - sintetizza la risposta finale
CHAIRMAN_MODEL = "gemini"

# Directory dati per la memorizzazione delle conversazioni
DATA_DIR = "data/conversations"
```

### Configurazione CLI

Il sistema invoca le CLI tramite subprocess. Ogni CLI deve essere:
1. Installata e disponibile nel PATH
2. Autenticata con credenziali valide
3. Funzionante con un prompt di test

Verifica la tua configurazione:
```bash
# Testa ogni CLI
echo "Ciao" | gemini
codex exec "Quanto fa 2+2?"
echo "Ciao" | claude -p
```

## Riferimento API

Il backend espone un'API RESTful sulla porta 8001:

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/` | GET | Controllo di salute |
| `/api/conversations` | GET | Elenca tutte le conversazioni (solo metadata) |
| `/api/conversations` | POST | Crea nuova conversazione |
| `/api/conversations/{id}` | GET | Ottieni conversazione con tutti i messaggi |
| `/api/conversations/{id}/message` | POST | Invia messaggio (risposta completa) |
| `/api/conversations/{id}/message/stream` | POST | Invia messaggio (streaming SSE) |

### Esempio: Inviare un Messaggio

```bash
curl -X POST http://localhost:8001/api/conversations/{id}/message \
  -H "Content-Type: application/json" \
  -d '{"content": "Che cos'\''è il quantum computing?"}'
```

La risposta include tutte e tre le fasi:
```json
{
  "stage1": [
    {"model": "gemini", "response": "..."},
    {"model": "codex", "response": "..."},
    {"model": "claude", "response": "..."}
  ],
  "stage2": [
    {"model": "gemini", "ranking": "...", "parsed_ranking": ["Response A", "Response C", "Response B"]},
    ...
  ],
  "stage3": {
    "model": "gemini",
    "response": "..."
  },
  "metadata": {
    "label_to_model": {"Response A": "gemini", ...},
    "aggregate_rankings": [...]
  }
}
```

## Stack Tecnologico

**Backend:**
- FastAPI (Python 3.10+)
- Esecuzione asincrona di subprocess per invocazione CLI
- Memorizzazione file JSON per conversazioni
- Server-Sent Events (SSE) per streaming

**Frontend:**
- React 19 con Hooks
- Vite per build tooling
- react-markdown per rendering delle risposte
- CSS3 per styling

**Integrazione CLI:**
- Gemini CLI: `echo "prompt" | gemini`
- Codex CLI: `codex exec "prompt"`
- Claude CLI: `echo "prompt" | claude -p`

## Struttura del Progetto

```
llm-council-master/
├── backend/
│   ├── main.py           # Applicazione FastAPI
│   ├── council.py        # Logica orchestrazione 3 fasi
│   ├── cli_bridge.py     # Esecuzione subprocess CLI
│   ├── config.py         # Configurazione
│   └── storage.py        # Memorizzazione file JSON
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Applicazione principale
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx  # UI chat principale
│   │   │   ├── Sidebar.jsx        # Lista conversazioni
│   │   │   ├── Stage1.jsx         # Risposte individuali
│   │   │   ├── Stage2.jsx         # Classifiche
│   │   │   └── Stage3.jsx         # Sintesi finale
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── docs/
│   ├── INSTALL_CLI.md    # Guida installazione CLI
│   ├── ARCHITECTURE.md   # Architettura del sistema
│   └── PLAN_TDD.md       # Piani di sviluppo
├── data/
│   └── conversations/    # Conversazioni memorizzate (JSON)
├── start.bat             # Script avvio Windows
├── start.sh              # Script avvio Unix
├── pyproject.toml        # Dipendenze Python
└── README.md             # File principale (inglese)
```

## Risoluzione Problemi

### Il backend non si avvia
- Controlla versione Python: `python --version` (serve 3.10+)
- Installa dipendenze: `pip install fastapi uvicorn httpx pydantic`
- Controlla che porta 8001 sia disponibile: `netstat -an | grep 8001`

### Il frontend non si avvia
- Controlla versione Node.js: `node --version` (serve 14+)
- Installa dipendenze: `cd frontend && npm install`
- Controlla che porta 5173 sia disponibile

### Errori CLI non trovata
- Verifica installazione CLI: `which gemini` / `which codex` / `which claude`
- Assicurati che le CLI siano nel PATH
- Vedi [docs/INSTALL_CLI.md](docs/INSTALL_CLI.md) per aiuto installazione

### Timeout dei modelli
- Timeout predefinito è 120 secondi per chiamata CLI
- Controlla connessione di rete
- Verifica autenticazione CLI: esegui comandi di test manualmente
- Aumenta timeout in `backend/cli_bridge.py` se necessario

### Risposte vuote o errori
- Controlla stato autenticazione CLI
- Esegui CLI manualmente per verificare che funzionino: `echo "test" | gemini`
- Controlla log backend per messaggi di errore dettagliati
- Verifica di avere abbonamenti attivi per tutti e tre i servizi

## Contribuire

Questo progetto è fornito così com'è per ispirazione e apprendimento. Sentiti libero di fare fork e modificarlo per le tue esigenze. Il codice è progettato per essere leggibile e modificabile - chiedi al tuo LLM preferito di aiutarti a personalizzarlo!

### Sviluppo

Esegui backend in modalità sviluppo:
```bash
python -m backend.main
```

Esegui frontend in modalità sviluppo:
```bash
cd frontend
npm run dev
```

Esegui test:
```bash
# Test backend
python -m pytest backend/tests/

# Testa CLI manualmente
python -m backend.tests.test_cli_bridge
```

## Licenza

Licenza MIT - vedi il codice e usalo come preferisci. Questo progetto è stato creato come hack di fine settimana per esplorare la collaborazione tra più modelli AI.

## Ringraziamenti

- Concetto originale ispirato dalla necessità di confrontare più LLM fianco a fianco
- Costruito con ispirazione dall'approccio di Andrej Karpathy alla lettura di libri con gli LLM
- Ringraziamenti speciali ai team di Google, OpenAI e Anthropic per i loro eccellenti strumenti CLI

---

**Nota**: Questo è uno strumento di sviluppo locale. Per uso in produzione, considera di aggiungere autenticazione, rate limiting e gestione errori appropriata.
