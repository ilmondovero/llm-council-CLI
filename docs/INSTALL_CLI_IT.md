# Guida all'Installazione delle CLI

Questa guida ti aiuterà ad installare e configurare i tre strumenti CLI richiesti da LLM Council:

- **Gemini CLI** (Google)
- **Codex CLI** (OpenAI)
- **Claude CLI** (Anthropic)

## Panoramica

LLM Council utilizza strumenti CLI locali per interagire con i modelli AI invece di chiavi API. Questo approccio:
- Utilizza i tuoi abbonamenti esistenti (nessun costo API aggiuntivo)
- Mantiene i tuoi dati locali e privati
- Sfrutta gli strumenti CLI ufficiali di ogni provider
- Fornisce una migliore integrazione con il tuo ambiente di sviluppo

## Prerequisiti

Prima di installare le CLI, assicurati di avere:

- **Node.js 14+** (per l'installazione dei pacchetti npm)
- **Python 3.10+** (per il backend di LLM Council)
- Abbonamenti o crediti attivi con:
  - Google AI Studio / Gemini
  - OpenAI (ChatGPT Plus o accesso API)
  - Anthropic Claude (abbonamento Pro o accesso API)

## 1. Installazione Gemini CLI

### Installa tramite npm

```bash
npm install -g @google/generative-ai-cli
```

**Nome pacchetto alternativo** (se il precedente non funziona):
```bash
npm install -g gemini-cli
```

### Autenticazione

1. Visita [Google AI Studio](https://makersuite.google.com/app/apikey) per ottenere la tua chiave API

2. Configura l'autenticazione:

**Opzione A: Variabile d'ambiente**
```bash
# Windows
set GOOGLE_API_KEY=la_tua_chiave_api

# Linux/Mac
export GOOGLE_API_KEY=la_tua_chiave_api
```

**Opzione B: Login CLI**
```bash
gemini auth login
```

### Verifica Installazione

Testa la Gemini CLI:
```bash
echo "Ciao, Gemini!" | gemini
```

Output atteso: Una risposta da Gemini che ti saluta o risponde al tuo messaggio.

### Risoluzione Problemi Gemini CLI

**Comando non trovato:**
- Controlla la posizione bin globale di npm: `npm config get prefix`
- Aggiungi al PATH se necessario:
  - Windows: Aggiungi `%USERPROFILE%\AppData\Roaming\npm` al PATH
  - Linux/Mac: Aggiungi `$HOME/.npm-global/bin` al PATH

**Errori di autenticazione:**
- Verifica che la chiave API sia valida su [Google AI Studio](https://makersuite.google.com/app/apikey)
- Controlla che la variabile d'ambiente sia impostata: `echo %GOOGLE_API_KEY%` (Windows) o `echo $GOOGLE_API_KEY` (Unix)
- Prova a ri-autenticarti: `gemini auth logout` poi `gemini auth login`

**Rate limiting:**
- Il tier gratuito ha limiti di frequenza - considera l'upgrade se li raggiungi frequentemente
- Aspetta qualche minuto e riprova

## 2. Installazione Codex CLI

### Installa tramite npm

```bash
npm install -g @openai/codex-cli
```

**Installazione alternativa** (se la precedente non funziona):
```bash
npm install -g openai-cli
```

### Autenticazione

1. Ottieni la tua chiave API OpenAI da [OpenAI API Keys](https://platform.openai.com/api-keys)

2. Configura l'autenticazione:

**Opzione A: Variabile d'ambiente**
```bash
# Windows
set OPENAI_API_KEY=sk-proj-...

# Linux/Mac
export OPENAI_API_KEY=sk-proj-...
```

**Opzione B: Configurazione CLI**
```bash
codex config set api-key sk-proj-...
```

### Verifica Installazione

Testa la Codex CLI:
```bash
codex exec "Quanto fa 2+2?"
```

Output atteso: Una risposta che calcola che 2+2=4.

### Risoluzione Problemi Codex CLI

**Comando non trovato:**
- Assicurati che l'installazione globale npm abbia funzionato: `npm list -g --depth=0`
- Controlla che il PATH includa la directory bin di npm
- Prova `npx @openai/codex-cli exec "test"` come alternativa

**Errori di autenticazione:**
- Verifica che la chiave API inizi con `sk-proj-` o `sk-`
- Controlla che la chiave sia attiva su [OpenAI Platform](https://platform.openai.com/api-keys)
- Assicurati di avere crediti/fatturazione abilitata

**Errori di accesso al modello:**
- Alcuni modelli richiedono livelli di accesso specifici
- Il modello predefinito dovrebbe funzionare con qualsiasi account OpenAI
- Controlla [OpenAI Status](https://status.openai.com/) per interruzioni di servizio

**Rate limiting:**
- Il tier gratuito ha limiti stretti
- Considera l'upgrade al tier a pagamento per limiti più alti
- LLM Council effettua 3-6 chiamate per query (fase 1, 2 e opzionalmente fase 3)

## 3. Installazione Claude CLI

### Installa tramite npm

```bash
npm install -g @anthropic-ai/claude-cli
```

**Metodo alternativo** (installer ufficiale Anthropic):
Visita [Anthropic CLI Docs](https://docs.anthropic.com/claude/docs/cli) per il metodo di installazione più recente.

### Autenticazione

1. Ottieni la tua chiave API da [Anthropic Console](https://console.anthropic.com/settings/keys)

2. Configura l'autenticazione:

**Opzione A: Variabile d'ambiente**
```bash
# Windows
set ANTHROPIC_API_KEY=sk-ant-...

# Linux/Mac
export ANTHROPIC_API_KEY=sk-ant-...
```

**Opzione B: Login CLI**
```bash
claude auth login
```

**Opzione C: Prompt interattivo**
La Claude CLI potrebbe chiederti le credenziali al primo utilizzo.

### Verifica Installazione

Testa la Claude CLI:
```bash
echo "Ciao, Claude!" | claude -p
```

Il flag `-p` abilita la modalità "plain" per un output più pulito.

Output atteso: Una risposta amichevole da Claude.

### Risoluzione Problemi Claude CLI

**Comando non trovato:**
- Controlla l'installazione Claude CLI: `npm list -g | grep claude`
- Assicurati che il bin globale di npm sia nel PATH
- Prova a reinstallare: `npm uninstall -g @anthropic-ai/claude-cli && npm install -g @anthropic-ai/claude-cli`

**Errori di autenticazione:**
- Verifica il formato della chiave API (dovrebbe iniziare con `sk-ant-`)
- Controlla che la chiave sia attiva su [Anthropic Console](https://console.anthropic.com/settings/keys)
- Prova ad usare il flag `--api-key` direttamente: `claude --api-key=sk-ant-... -p`

**Errori di permessi:**
- La CLI potrebbe richiedere determinati permessi
- Usa il flag `--dangerously-skip-permissions` se necessario (già configurato in LLM Council)

**Rate limiting:**
- Il tier gratuito potrebbe avere limiti stretti
- L'abbonamento Claude Pro fornisce limiti più alti
- Monitora l'utilizzo su [Anthropic Console](https://console.anthropic.com/settings/usage)

## 4. Verifica Finale

Una volta che tutte e tre le CLI sono installate, verifica che funzionino insieme:

### Script di Test Rapido

Crea un file di test `test_cli.bat` (Windows) o `test_cli.sh` (Unix):

**Windows (test_cli.bat):**
```batch
@echo off
echo Test Gemini CLI...
echo "Test" | gemini
echo.

echo Test Codex CLI...
codex exec "Test"
echo.

echo Test Claude CLI...
echo "Test" | claude -p
echo.

echo Tutte le CLI testate!
pause
```

**Linux/Mac (test_cli.sh):**
```bash
#!/bin/bash

echo "Test Gemini CLI..."
echo "Test" | gemini
echo

echo "Test Codex CLI..."
codex exec "Test"
echo

echo "Test Claude CLI..."
echo "Test" | claude -p
echo

echo "Tutte le CLI testate!"
```

Rendilo eseguibile ed esegui:
```bash
# Linux/Mac
chmod +x test_cli.sh
./test_cli.sh

# Windows
test_cli.bat
```

### Risultati Attesi

Ogni CLI dovrebbe restituire una breve risposta. Se tutte e tre funzionano, sei pronto per eseguire LLM Council!

## 5. Configurazione Avanzata

### Impostare Modelli Predefiniti

Alcune CLI permettono di specificare modelli predefiniti:

**Codex/OpenAI:**
```bash
codex config set model gpt-4o
```

**Gemini:**
```bash
gemini config set model gemini-2.0-flash
```

**Claude:**
La Claude CLI usa il modello più recente disponibile per default.

### Configurazione Timeout

Se riscontri timeout, puoi modificare le impostazioni CLI o modificare `backend/cli_bridge.py` in LLM Council:

```python
# In cli_bridge.py, riga ~48
timeout=240.0  # Aumenta da 120 a 240 secondi
```

### Configurazione Proxy

Se sei dietro un proxy aziendale:

```bash
# Windows
set HTTP_PROXY=http://proxy.esempio.com:8080
set HTTPS_PROXY=http://proxy.esempio.com:8080

# Linux/Mac
export HTTP_PROXY=http://proxy.esempio.com:8080
export HTTPS_PROXY=http://proxy.esempio.com:8080
```

## 6. Aggiornamento delle CLI

Mantieni le tue CLI aggiornate per le migliori prestazioni:

```bash
# Aggiorna tutte le CLI
npm update -g @google/generative-ai-cli
npm update -g @openai/codex-cli
npm update -g @anthropic-ai/claude-cli
```

## 7. Disinstallazione delle CLI

Se devi disinstallare:

```bash
npm uninstall -g @google/generative-ai-cli
npm uninstall -g @openai/codex-cli
npm uninstall -g @anthropic-ai/claude-cli
```

## Problemi Comuni

### Problema: Errori "Modulo non trovato"

**Soluzione:**
- Pulisci la cache npm: `npm cache clean --force`
- Reinstalla le CLI
- Controlla la versione Node.js: `node --version` (serve 14+)

### Problema: Le CLI funzionano singolarmente ma non in LLM Council

**Soluzione:**
- Verifica che il PATH sia impostato nella shell da cui esegui LLM Council
- Controlla i log del backend per errori specifici: guarda il terminale che esegue `backend.main`
- Testa l'esecuzione subprocess manualmente:
  ```python
  import subprocess
  result = subprocess.run(['gemini'], input='test', capture_output=True, text=True)
  print(result.stdout)
  ```

### Problema: Fallimenti intermittenti

**Soluzione:**
- Controlla la connettività di rete
- Verifica lo stato dei servizi API:
  - [Google AI Status](https://status.cloud.google.com/)
  - [OpenAI Status](https://status.openai.com/)
  - [Anthropic Status](https://status.anthropic.com/)
- Aumenta il timeout in `backend/cli_bridge.py`
- Controlla i limiti di frequenza sui tuoi account

### Problema: Errori di encoding/Unicode

**Soluzione:**
- Assicurati che il terminale supporti UTF-8:
  - Windows: `chcp 65001`
  - Linux/Mac: `export LANG=it_IT.UTF-8`
- Aggiorna Python e Node.js alle versioni più recenti
- Controlla che `backend/cli_bridge.py` usi `encoding='utf-8'`

## Prossimi Passi

Una volta che tutte le CLI sono installate e verificate:

1. Torna al [README_IT.md](../README_IT.md) principale
2. Segui la guida Avvio Rapido
3. Esegui `start.bat` (Windows) o `start.sh` (Unix)
4. Inizia a fare domande al tuo LLM Council!

## Supporto

Per problemi specifici delle CLI:
- **Gemini**: [Google AI Documentation](https://ai.google.dev/docs)
- **Codex/OpenAI**: [OpenAI Documentation](https://platform.openai.com/docs)
- **Claude**: [Anthropic Documentation](https://docs.anthropic.com/)

Per problemi con LLM Council:
- Controlla la [sezione Risoluzione Problemi](../README_IT.md#risoluzione-problemi) nel README principale
- Esamina i log del backend per messaggi di errore dettagliati
- Testa ogni CLI individualmente per isolare il problema

---

**Nota**: Gli strumenti CLI e i loro nomi pacchetto possono cambiare. Se riscontri problemi, controlla la documentazione ufficiale di ogni provider per i metodi di installazione più recenti.
