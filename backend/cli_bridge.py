"""
CLI Bridge - Invoca Gemini CLI, Codex CLI e Claude CLI via subprocess.

Questo modulo sostituisce openrouter.py per usare le CLI locali invece delle API.
Mantiene la stessa interfaccia per compatibilità con council.py.

OODA Loop Implementation:
- Observe: Raccoglie il prompt dai messaggi
- Orient: Determina quale CLI usare
- Decide: Costruisce il comando appropriato
- Act: Esegue e processa l'output
"""

import asyncio
import subprocess
import os
import tempfile
import shutil
from typing import List, Dict, Any, Optional


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """
    Query un modello via CLI subprocess.

    Args:
        model: Identificatore del modello/CLI (gemini, codex, claude)
        messages: Lista di messaggi con 'role' e 'content'
        timeout: Timeout in secondi per la richiesta

    Returns:
        Dict con 'content' e 'reasoning_details', o None se fallito
    """
    # OBSERVE: Costruisci il prompt completo
    prompt = build_prompt_from_messages(messages)

    # ORIENT: Determina la CLI da usare
    cli_type = determine_cli(model)

    # DECIDE & ACT: Esegui con la CLI appropriata
    try:
        result = await asyncio.wait_for(
            run_cli_with_prompt(cli_type, prompt),
            timeout=timeout
        )

        # Verifica errori nel risultato
        if result.startswith("Error:"):
            print(f"CLI error for {model}: {result}")
            return None

        # Verifica che ci sia contenuto
        if not result.strip():
            print(f"Empty response from {model}")
            return None

        return {"content": result, "reasoning_details": None}

    except asyncio.TimeoutError:
        print(f"Timeout querying {model} after {timeout}s")
        return None
    except Exception as e:
        print(f"Error querying {model}: {e}")
        return None


async def run_cli_with_prompt(cli_type: str, prompt: str) -> str:
    """
    Esegue una CLI con il prompt dato.
    Usa file temporanei per passare prompt lunghi in modo sicuro.
    """
    return await asyncio.to_thread(_run_cli_sync, cli_type, prompt)


def _find_cli_path(cli_name: str) -> Optional[str]:
    """Trova il percorso completo della CLI."""
    # Prima prova con shutil.which
    path = shutil.which(cli_name)
    if path:
        return path

    # Su Windows, prova anche con .cmd
    if os.name == 'nt':
        path = shutil.which(f"{cli_name}.cmd")
        if path:
            return path

    return None


def _run_cli_sync(cli_type: str, prompt: str) -> str:
    """
    Esecuzione sincrona della CLI.

    Per prompt lunghi, usa file temporanei per evitare problemi con escape
    di caratteri speciali su Windows.
    """
    try:
        cwd = os.getcwd()

        if cli_type == "gemini":
            return _run_gemini(prompt, cwd)
        elif cli_type == "codex":
            return _run_codex(prompt, cwd)
        elif cli_type == "claude":
            return _run_claude(prompt, cwd)
        else:
            return f"Error: Unknown CLI type: {cli_type}"

    except subprocess.TimeoutExpired:
        return "Error: CLI timeout (5 minutes exceeded)"
    except FileNotFoundError as e:
        return f"Error: CLI not found - {e}"
    except Exception as e:
        return f"Error: {str(e)}"


def _run_gemini(prompt: str, cwd: str) -> str:
    """Esegue Gemini CLI."""
    # Salva il prompt in un file temporaneo per evitare problemi di escape
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(prompt)
        prompt_file = f.name

    try:
        # Usa shell=True su Windows per trovare il comando
        if os.name == 'nt':
            # Legge dal file e passa a gemini via pipe
            cmd = f'type "{prompt_file}" | gemini'
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=cwd,
                shell=True,
                encoding='utf-8',
                errors='replace'
            )
        else:
            # Su Unix, usa cat | gemini
            cmd = f'cat "{prompt_file}" | gemini'
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=cwd,
                shell=True,
                encoding='utf-8',
                errors='replace'
            )

        output = result.stdout or ""

        if result.returncode != 0 and not output.strip():
            stderr = result.stderr or ""
            if stderr.strip():
                return f"Error: {stderr.strip()}"
            return f"Error: Gemini returned code {result.returncode}"

        return clean_cli_output(output, "gemini")

    finally:
        if os.path.exists(prompt_file):
            os.unlink(prompt_file)


def _run_codex(prompt: str, cwd: str) -> str:
    """Esegue Codex CLI."""
    # Salva il prompt in un file temporaneo
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(prompt)
        prompt_file = f.name

    try:
        # Codex exec legge il prompt come argomento, ma per prompt lunghi
        # dobbiamo usare un approccio diverso
        # Proviamo con stdin via pipe

        if os.name == 'nt':
            # Su Windows, usa type per passare il contenuto
            cmd = f'type "{prompt_file}" | codex exec -'
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=cwd,
                shell=True,
                encoding='utf-8',
                errors='replace'
            )

            # Se fallisce, prova direttamente con il prompt (troncato se necessario)
            if result.returncode != 0 or not result.stdout.strip():
                # Tronca il prompt se troppo lungo per la command line
                short_prompt = prompt[:2000] if len(prompt) > 2000 else prompt
                # Escape virgolette
                short_prompt = short_prompt.replace('"', '\\"')
                cmd = f'codex exec "{short_prompt}"'
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=cwd,
                    shell=True,
                    encoding='utf-8',
                    errors='replace'
                )
        else:
            cmd = f'cat "{prompt_file}" | codex exec -'
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=cwd,
                shell=True,
                encoding='utf-8',
                errors='replace'
            )

        output = result.stdout or ""

        if result.returncode != 0 and not output.strip():
            stderr = result.stderr or ""
            if stderr.strip():
                return f"Error: {stderr.strip()}"
            return f"Error: Codex returned code {result.returncode}"

        return clean_cli_output(output, "codex")

    finally:
        if os.path.exists(prompt_file):
            os.unlink(prompt_file)


def _run_claude(prompt: str, cwd: str) -> str:
    """Esegue Claude CLI."""
    # Salva il prompt in un file temporaneo
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(prompt)
        prompt_file = f.name

    try:
        if os.name == 'nt':
            # Su Windows, usa type per passare il contenuto via pipe
            cmd = f'type "{prompt_file}" | claude -p --dangerously-skip-permissions'
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=cwd,
                shell=True,
                encoding='utf-8',
                errors='replace'
            )
        else:
            cmd = f'cat "{prompt_file}" | claude -p --dangerously-skip-permissions'
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=cwd,
                shell=True,
                encoding='utf-8',
                errors='replace'
            )

        output = result.stdout or ""

        if result.returncode != 0 and not output.strip():
            stderr = result.stderr or ""
            if stderr.strip():
                return f"Error: {stderr.strip()}"
            return f"Error: Claude returned code {result.returncode}"

        return clean_cli_output(output, "claude")

    finally:
        if os.path.exists(prompt_file):
            os.unlink(prompt_file)


def build_prompt_from_messages(messages: List[Dict[str, str]]) -> str:
    """
    Converte lista messaggi in prompt singolo per le CLI.

    Le CLI non supportano il formato chat nativo, quindi concateniamo
    i messaggi in un unico prompt testuale.
    """
    parts = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if role == "system":
            parts.append(f"System: {content}")
        elif role == "assistant":
            parts.append(f"Assistant: {content}")
        else:
            # User message - aggiungi direttamente
            parts.append(content)

    return "\n\n".join(parts)


def determine_cli(model: str) -> str:
    """
    Determina quale CLI usare basandosi sul nome del modello.

    Mapping:
    - gemini, google -> gemini CLI
    - codex, openai, gpt, o1, o3 -> codex CLI
    - claude, anthropic -> claude CLI
    """
    model_lower = model.lower()

    if "gemini" in model_lower or "google" in model_lower:
        return "gemini"
    elif any(x in model_lower for x in ["codex", "openai", "gpt", "o1", "o3"]):
        return "codex"
    elif "claude" in model_lower or "anthropic" in model_lower:
        return "claude"

    # Default: usa il nome stesso come CLI type
    return model_lower


def clean_cli_output(output: str, cli_type: str) -> str:
    """
    Pulisce l'output CLI rimuovendo metadata non necessari.

    Ogni CLI ha un formato di output diverso che va normalizzato.
    """
    if not output:
        return ""

    if cli_type == "gemini":
        # Gemini CLI aggiunge "Loaded cached credentials." all'inizio
        lines = output.split('\n')
        cleaned = []
        for line in lines:
            # Salta linee di sistema di Gemini
            if line.startswith('Loaded cached'):
                continue
            if line.startswith('Using model:'):
                continue
            cleaned.append(line)
        return '\n'.join(cleaned).strip()

    elif cli_type == "codex":
        # Codex CLI ha un header verbose:
        # OpenAI Codex v0.65.0 (research preview)
        # --------
        # workdir: ...
        # model: ...
        # ...
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

        # Fallback: cerca di rimuovere l'header
        lines = output.split('\n')
        # Trova la linea "codex" e prendi tutto dopo
        for i, line in enumerate(lines):
            if line.strip() == "codex":
                remaining = '\n'.join(lines[i+1:])
                if "tokens used" in remaining:
                    remaining = remaining.split("tokens used")[0]
                return remaining.strip()

        return output.strip()

    elif cli_type == "claude":
        # Claude CLI con -p dovrebbe dare output relativamente pulito
        # Ma potrebbe avere warning o linee vuote iniziali
        lines = output.split('\n')
        cleaned = []
        started = False

        for line in lines:
            # Salta linee vuote e warning prima del contenuto
            if not started:
                if not line.strip():
                    continue
                if line.startswith('Warning'):
                    continue
                if line.startswith('Note:'):
                    continue

            started = True
            cleaned.append(line)

        return '\n'.join(cleaned).strip()

    return output.strip()


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]]
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Query multipli modelli in parallelo.

    Usa asyncio.gather per eseguire tutte le query contemporaneamente,
    riducendo il tempo totale al tempo della query più lenta.

    Args:
        models: Lista di identificatori modello/CLI
        messages: Lista di messaggi da inviare

    Returns:
        Dict che mappa ogni modello alla sua risposta (o None se fallito)
    """
    # Crea task per tutti i modelli
    tasks = [query_model(model, messages) for model in models]

    # Esegui tutti in parallelo
    responses = await asyncio.gather(*tasks)

    # Mappa modelli alle risposte
    return {model: response for model, response in zip(models, responses)}
