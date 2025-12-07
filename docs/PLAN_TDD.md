# Piano TDD: Adattamento LLM Council da API a CLI

## Obiettivo
Sostituire le chiamate API OpenRouter con invocazioni dirette delle 3 CLI (Gemini CLI, Codex CLI, Claude CLI) per sfruttare gli abbonamenti esistenti senza costi API aggiuntivi.

---

## Analisi delle Modifiche Necessarie

### File da Modificare
1. `backend/config.py` - Configurazione modelli e CLI mapping
2. `backend/openrouter.py` → `backend/cli_bridge.py` - Nuovo modulo CLI
3. `backend/council.py` - Import del nuovo modulo (minima modifica)

### File da Creare
1. `backend/cli_bridge.py` - Bridge per le 3 CLI con ciclo OODA
2. `backend/tests/test_cli_bridge.py` - Test unitari

---

## Schema Architetturale

```
                    ┌─────────────────────┐
                    │    council.py       │
                    │  (orchestrazione)   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   cli_bridge.py     │
                    │  (interfaccia CLI)  │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
 ┌──────▼──────┐       ┌───────▼───────┐      ┌──────▼──────┐
 │ Gemini CLI  │       │  Codex CLI    │      │ Claude CLI  │
 │  subprocess │       │  subprocess   │      │  subprocess │
 │   gemini    │       │  codex exec   │      │ claude -p   │
 └─────────────┘       └───────────────┘      └─────────────┘
```

---

## Le 3 CLI

### 1. Gemini CLI
- **Comando**: `gemini "prompt"`
- **Output**: Testo diretto con prefisso "Loaded cached credentials."
- **Timeout**: ~2-5 secondi

### 2. Codex CLI (OpenAI)
- **Comando**: `codex exec "prompt"`
- **Requisito**: Deve essere eseguito in una directory git
- **Output**: Verbose con header, risposta dopo "codex\n"
- **Timeout**: ~3-8 secondi

### 3. Claude CLI
- **Comando**: `claude -p --dangerously-skip-permissions "prompt"`
- **Flag**:
  - `-p` / `--print`: Output non interattivo
  - `--dangerously-skip-permissions`: Bypassa tutti i check di permessi
- **Output**: Testo diretto della risposta
- **Timeout**: ~2-5 secondi

---

## Fase 1: Test First (Red)

### Test 1.1: Query Singola Gemini
```python
async def test_query_gemini_basic():
    """Test che Gemini CLI risponde a una query semplice."""
    response = await query_model("gemini", [{"role": "user", "content": "What is 2+2?"}])
    assert response is not None
    assert "content" in response
    assert len(response["content"]) > 0
```

### Test 1.2: Query Singola Codex
```python
async def test_query_codex_basic():
    """Test che Codex CLI risponde a una query semplice."""
    response = await query_model("codex", [{"role": "user", "content": "What is 2+2?"}])
    assert response is not None
    assert "content" in response
```

### Test 1.3: Query Singola Claude
```python
async def test_query_claude_basic():
    """Test che Claude CLI risponde a una query semplice."""
    response = await query_model("claude", [{"role": "user", "content": "What is 2+2?"}])
    assert response is not None
    assert "content" in response
```

### Test 1.4: Query Parallele 3 CLI
```python
async def test_query_parallel_all_three():
    """Test query parallele a tutte e 3 le CLI."""
    models = ["gemini", "codex", "claude"]
    messages = [{"role": "user", "content": "Explain recursion in one sentence"}]
    responses = await query_models_parallel(models, messages)
    assert len(responses) == 3
    # Almeno 2 su 3 dovrebbero rispondere
    successful = sum(1 for r in responses.values() if r is not None)
    assert successful >= 2
```

### Test 1.5: Gestione Errori Graceful
```python
async def test_error_returns_none():
    """Test che errori CLI ritornano None senza crashare."""
    response = await query_model("invalid_cli", [{"role": "user", "content": "test"}])
    assert response is None
```

---

## Fase 2: Implementazione (Green)

### 2.1: Configurazione (`config.py`)

```python
# Council members - le 3 CLI
COUNCIL_MODELS = [
    "gemini",   # Google Gemini via CLI
    "codex",    # OpenAI via Codex CLI
    "claude",   # Anthropic via Claude CLI
]

# Chairman model - sintetizza la risposta finale
CHAIRMAN_MODEL = "gemini"

# Working directory per Codex (richiede git repo)
import os
WORKING_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data directory for conversation storage
DATA_DIR = "data/conversations"
```

### 2.2: CLI Bridge (`cli_bridge.py`)

```python
"""CLI Bridge - Invoca Gemini CLI, Codex CLI e Claude CLI via subprocess."""

import asyncio
import subprocess
import os
from typing import List, Dict, Any, Optional


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """
    Query un modello via CLI subprocess.

    OODA Loop:
    - Observe: Raccoglie il prompt dai messaggi
    - Orient: Determina quale CLI usare
    - Decide: Costruisce il comando
    - Act: Esegue e processa l'output
    """
    # OBSERVE: Costruisci il prompt completo
    prompt = build_prompt_from_messages(messages)

    # ORIENT: Determina la CLI
    cli_type = determine_cli(model)

    # DECIDE: Costruisci comando
    if cli_type == "gemini":
        cmd = build_gemini_command(prompt)
    elif cli_type == "codex":
        cmd = build_codex_command(prompt)
    elif cli_type == "claude":
        cmd = build_claude_command(prompt)
    else:
        print(f"Unknown CLI type: {cli_type}")
        return None

    # ACT: Esegui con gestione output grande
    try:
        result = await asyncio.wait_for(
            run_cli_command(cmd, cli_type),
            timeout=timeout
        )
        if result.startswith("Error:"):
            print(f"CLI error for {model}: {result}")
            return None
        return {"content": result, "reasoning_details": None}
    except asyncio.TimeoutError:
        print(f"Timeout querying {model}")
        return None
    except Exception as e:
        print(f"Error querying {model}: {e}")
        return None


async def run_cli_command(cmd: List[str], cli_type: str) -> str:
    """Esegue comando CLI in modo async-safe."""
    return await asyncio.to_thread(_run_sync, cmd, cli_type)


def _run_sync(cmd: List[str], cli_type: str) -> str:
    """Esecuzione sincrona del subprocess."""
    try:
        # Determina working directory
        cwd = os.getcwd()

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minuti max
            cwd=cwd,
            shell=(os.name == 'nt')  # shell=True su Windows per trovare i comandi npm
        )

        # Combina stdout e stderr
        output = result.stdout
        if result.returncode != 0 and result.stderr:
            # Se c'è un errore, includi stderr
            if not output.strip():
                return f"Error: {result.stderr}"

        # Pulisci output specifico per CLI
        output = clean_cli_output(output, cli_type)

        return output

    except subprocess.TimeoutExpired:
        return "Error: CLI timeout (5 minutes exceeded)"
    except FileNotFoundError as e:
        return f"Error: CLI not found - {e}"
    except Exception as e:
        return f"Error: {str(e)}"


def build_prompt_from_messages(messages: List[Dict[str, str]]) -> str:
    """Converte lista messaggi in prompt singolo."""
    parts = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            parts.append(f"System: {content}")
        elif role == "assistant":
            parts.append(f"Assistant: {content}")
        else:
            parts.append(content)
    return "\n\n".join(parts)


def determine_cli(model: str) -> str:
    """Determina quale CLI usare per il modello."""
    model_lower = model.lower()
    if "gemini" in model_lower or "google" in model_lower:
        return "gemini"
    elif "codex" in model_lower or "openai" in model_lower or "gpt" in model_lower:
        return "codex"
    elif "claude" in model_lower or "anthropic" in model_lower:
        return "claude"
    # Default: usa il nome come CLI type
    return model_lower


def build_gemini_command(prompt: str) -> List[str]:
    """Costruisce comando Gemini CLI."""
    # gemini "prompt"
    return ["gemini", prompt]


def build_codex_command(prompt: str) -> List[str]:
    """Costruisce comando Codex CLI."""
    # codex exec "prompt"
    return ["codex", "exec", prompt]


def build_claude_command(prompt: str) -> List[str]:
    """Costruisce comando Claude CLI con skip permissions."""
    # claude -p --dangerously-skip-permissions "prompt"
    return ["claude", "-p", "--dangerously-skip-permissions", prompt]


def clean_cli_output(output: str, cli_type: str) -> str:
    """Pulisce l'output CLI rimuovendo metadata non necessari."""
    if not output:
        return ""

    if cli_type == "gemini":
        # Rimuovi "Loaded cached credentials." e simili
        lines = output.split('\n')
        cleaned = [l for l in lines if not l.startswith('Loaded cached')]
        return '\n'.join(cleaned).strip()

    elif cli_type == "codex":
        # Rimuovi header Codex (tutto prima dell'ultimo "codex\n")
        # L'output di Codex ha questa struttura:
        # OpenAI Codex v0.65.0 ...
        # --------
        # ... header info ...
        # codex
        # <actual response>
        # tokens used
        # <number>
        if "codex\n" in output:
            parts = output.split("codex\n")
            if len(parts) > 1:
                # Prendi l'ultima parte dopo l'ultimo "codex\n"
                response = parts[-1]
                # Rimuovi "tokens used\n<number>" alla fine
                if "tokens used" in response:
                    response = response.split("tokens used")[0]
                return response.strip()
        return output.strip()

    elif cli_type == "claude":
        # Claude CLI con -p dovrebbe dare output pulito
        # Ma potrebbe avere prefissi di warning, rimuovili
        lines = output.split('\n')
        # Rimuovi linee vuote iniziali e warning
        cleaned = []
        started = False
        for line in lines:
            if not started and (not line.strip() or line.startswith('Warning')):
                continue
            started = True
            cleaned.append(line)
        return '\n'.join(cleaned).strip()

    return output.strip()


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]]
) -> Dict[str, Optional[Dict[str, Any]]]:
    """Query multipli modelli in parallelo."""
    tasks = [query_model(model, messages) for model in models]
    responses = await asyncio.gather(*tasks)
    return {model: response for model, response in zip(models, responses)}
```

---

## Fase 3: Refactoring

### 3.1: Aggiornare gli Import in `council.py`

```python
# Cambiare da:
from .openrouter import query_models_parallel, query_model

# A:
from .cli_bridge import query_models_parallel, query_model
```

### 3.2: Aggiornare `config.py`

```python
# RIMUOVERE queste righe:
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# SOSTITUIRE COUNCIL_MODELS con:
COUNCIL_MODELS = [
    "gemini",   # Google Gemini via CLI
    "codex",    # OpenAI via Codex CLI
    "claude",   # Anthropic via Claude CLI
]

# SOSTITUIRE CHAIRMAN_MODEL con:
CHAIRMAN_MODEL = "gemini"
```

### 3.3: Aggiornare `generate_conversation_title` in `council.py`

```python
# Cambiare da:
response = await query_model("google/gemini-2.5-flash", messages, timeout=30.0)

# A:
response = await query_model("gemini", messages, timeout=30.0)
```

---

## Fase 4: Test di Integrazione

### Test E2E del Council Completo
```python
async def test_full_council_with_cli():
    """Test completo del flow council con 3 CLI."""
    query = "What is the capital of France?"
    stage1, stage2, stage3, metadata = await run_full_council(query)

    # Almeno 2 modelli su 3 devono rispondere
    assert len(stage1) >= 2
    assert len(stage2) >= 2
    assert "response" in stage3
    assert len(stage3["response"]) > 0
```

---

## Considerazioni Importanti

### 1. Limitazioni delle CLI
- **Gemini CLI**: Richiede credenziali Google configurate
- **Codex CLI**: Richiede directory git inizializzata
- **Claude CLI**: Il flag `--dangerously-skip-permissions` bypassa i permessi

### 2. Performance
- Le CLI sono più lente delle API dirette (~2-8s vs ~0.5-1s)
- Il parallelismo mitiga significativamente (3 CLI in parallelo ≈ tempo della più lenta)
- Timeout di 120s per default, 300s max per subprocess

### 3. Output Parsing
Ogni CLI ha output diverso che va pulito:
- **Gemini**: "Loaded cached credentials." da rimuovere
- **Codex**: Header verbose, risposta dopo "codex\n", "tokens used" da rimuovere
- **Claude**: Output generalmente pulito con `-p`

### 4. Graceful Degradation
Se una CLI fallisce, le altre continuano. Il council funziona anche con 2 membri su 3.

---

## Ordine di Esecuzione

1. [x] Aggiornare PLAN_TDD.md con Claude CLI
2. [ ] Creare `backend/cli_bridge.py` con implementazione 3 CLI
3. [ ] Creare `backend/tests/test_cli_bridge.py` con test
4. [ ] Eseguire test e verificare funzionamento CLI singole
5. [ ] Aggiornare `backend/config.py`
6. [ ] Aggiornare import in `backend/council.py`
7. [ ] Test integrazione council completo
8. [ ] Test frontend end-to-end

---

## Rollback Plan

Il file `openrouter.py` originale viene mantenuto. Per tornare indietro:
```python
# In council.py, ripristinare:
from .openrouter import query_models_parallel, query_model
```

E ripristinare `config.py` originale con le variabili OpenRouter.

---

## Note Finali

Questo piano segue TDD (Test-Driven Development):
1. **Red**: Scrivi test che falliscono
2. **Green**: Implementa il minimo per passare i test
3. **Refactor**: Migliora il codice mantenendo i test verdi

La separazione in `cli_bridge.py` mantiene la stessa interfaccia di `openrouter.py`:
- `query_model(model, messages, timeout)` → `Optional[Dict]`
- `query_models_parallel(models, messages)` → `Dict[str, Optional[Dict]]`

Questo rende la modifica trasparente al resto del sistema.
