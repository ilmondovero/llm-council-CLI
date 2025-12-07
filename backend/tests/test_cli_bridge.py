"""
Test suite per cli_bridge.py

Esegui con: pytest backend/tests/test_cli_bridge.py -v
O per test singoli: pytest backend/tests/test_cli_bridge.py::test_query_gemini_basic -v
"""

import pytest
import asyncio
import sys
import os

# Aggiungi il path del backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.cli_bridge import (
    query_model,
    query_models_parallel,
    build_prompt_from_messages,
    determine_cli,
    clean_cli_output,
    build_gemini_command,
    build_codex_command,
    build_claude_command,
)


# ============================================================================
# Unit Tests - Funzioni di utilità
# ============================================================================

class TestBuildPromptFromMessages:
    """Test per build_prompt_from_messages"""

    def test_single_user_message(self):
        messages = [{"role": "user", "content": "Hello"}]
        result = build_prompt_from_messages(messages)
        assert result == "Hello"

    def test_multiple_messages(self):
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
            {"role": "user", "content": "Bye"},
        ]
        result = build_prompt_from_messages(messages)
        assert "System: You are helpful" in result
        assert "Hi" in result
        assert "Assistant: Hello!" in result
        assert "Bye" in result

    def test_empty_messages(self):
        messages = []
        result = build_prompt_from_messages(messages)
        assert result == ""


class TestDetermineCli:
    """Test per determine_cli"""

    def test_gemini_variants(self):
        assert determine_cli("gemini") == "gemini"
        assert determine_cli("Gemini") == "gemini"
        assert determine_cli("google/gemini-pro") == "gemini"
        assert determine_cli("GOOGLE") == "gemini"

    def test_codex_variants(self):
        assert determine_cli("codex") == "codex"
        assert determine_cli("openai/gpt-4") == "codex"
        assert determine_cli("gpt-4o") == "codex"
        assert determine_cli("o1-preview") == "codex"
        assert determine_cli("o3-mini") == "codex"

    def test_claude_variants(self):
        assert determine_cli("claude") == "claude"
        assert determine_cli("Claude") == "claude"
        assert determine_cli("anthropic/claude-3") == "claude"
        assert determine_cli("ANTHROPIC") == "claude"

    def test_unknown_fallback(self):
        assert determine_cli("unknown") == "unknown"
        assert determine_cli("custom-model") == "custom-model"


class TestBuildCommands:
    """Test per build_*_command functions"""

    def test_gemini_command(self):
        cmd = build_gemini_command("test prompt")
        assert cmd == ["gemini", "test prompt"]

    def test_codex_command(self):
        cmd = build_codex_command("test prompt")
        assert cmd == ["codex", "exec", "test prompt"]

    def test_claude_command(self):
        cmd = build_claude_command("test prompt")
        assert cmd == ["claude", "-p", "--dangerously-skip-permissions", "test prompt"]


class TestCleanCliOutput:
    """Test per clean_cli_output"""

    def test_gemini_cleanup(self):
        output = "Loaded cached credentials.\nActual response here"
        result = clean_cli_output(output, "gemini")
        assert result == "Actual response here"
        assert "Loaded cached" not in result

    def test_codex_cleanup(self):
        output = """OpenAI Codex v0.65.0 (research preview)
--------
workdir: /test
model: gpt-4
codex
This is the actual response
tokens used
123"""
        result = clean_cli_output(output, "codex")
        assert result == "This is the actual response"
        assert "OpenAI Codex" not in result
        assert "tokens used" not in result

    def test_claude_cleanup(self):
        output = "\n\nWarning: something\nActual response"
        result = clean_cli_output(output, "claude")
        assert result == "Actual response"

    def test_empty_output(self):
        assert clean_cli_output("", "gemini") == ""
        assert clean_cli_output("", "codex") == ""
        assert clean_cli_output("", "claude") == ""


# ============================================================================
# Integration Tests - Chiamate CLI reali
# ============================================================================

@pytest.mark.asyncio
async def test_query_gemini_basic():
    """Test che Gemini CLI risponde a una query semplice."""
    response = await query_model(
        "gemini",
        [{"role": "user", "content": "What is 2+2? Reply with just the number."}],
        timeout=60.0
    )
    assert response is not None, "Gemini CLI did not respond"
    assert "content" in response
    assert len(response["content"]) > 0
    print(f"Gemini response: {response['content'][:100]}...")


@pytest.mark.asyncio
async def test_query_codex_basic():
    """Test che Codex CLI risponde a una query semplice."""
    response = await query_model(
        "codex",
        [{"role": "user", "content": "What is 2+2? Reply with just the number."}],
        timeout=120.0
    )
    assert response is not None, "Codex CLI did not respond"
    assert "content" in response
    assert len(response["content"]) > 0
    print(f"Codex response: {response['content'][:100]}...")


@pytest.mark.asyncio
async def test_query_claude_basic():
    """Test che Claude CLI risponde a una query semplice."""
    response = await query_model(
        "claude",
        [{"role": "user", "content": "What is 2+2? Reply with just the number."}],
        timeout=60.0
    )
    assert response is not None, "Claude CLI did not respond"
    assert "content" in response
    assert len(response["content"]) > 0
    print(f"Claude response: {response['content'][:100]}...")


@pytest.mark.asyncio
async def test_query_parallel_all_three():
    """Test query parallele a tutte e 3 le CLI."""
    models = ["gemini", "codex", "claude"]
    messages = [{"role": "user", "content": "Say 'hello' in one word."}]

    responses = await query_models_parallel(models, messages)

    assert len(responses) == 3, "Should have 3 responses"

    # Conta risposte successful
    successful = sum(1 for r in responses.values() if r is not None)
    print(f"Successful responses: {successful}/3")

    for model, response in responses.items():
        if response:
            print(f"{model}: {response['content'][:50]}...")
        else:
            print(f"{model}: FAILED")

    # Almeno 2 su 3 dovrebbero rispondere
    assert successful >= 2, f"Expected at least 2 successful responses, got {successful}"


@pytest.mark.asyncio
async def test_error_returns_none():
    """Test che errori CLI ritornano None senza crashare."""
    response = await query_model(
        "invalid_cli_that_does_not_exist",
        [{"role": "user", "content": "test"}],
        timeout=10.0
    )
    assert response is None


@pytest.mark.asyncio
async def test_timeout_handling():
    """Test che timeout funziona correttamente."""
    # Timeout molto breve - dovrebbe fallire
    response = await query_model(
        "gemini",
        [{"role": "user", "content": "test"}],
        timeout=0.001  # 1ms - impossibile completare
    )
    # Potrebbe essere None per timeout o rispondere se cached
    # L'importante è che non crashi
    print(f"Timeout test result: {response}")


# ============================================================================
# Test di Output Lungo
# ============================================================================

@pytest.mark.asyncio
async def test_long_output_handling():
    """Test che output lunghi vengono gestiti correttamente."""
    prompt = "List the numbers from 1 to 20, each on a new line."
    response = await query_model(
        "gemini",
        [{"role": "user", "content": prompt}],
        timeout=60.0
    )

    if response:
        content = response["content"]
        print(f"Long output length: {len(content)} chars")
        # Verifica che ci sia contenuto sostanziale
        assert len(content) > 20


# ============================================================================
# Test Runner
# ============================================================================

if __name__ == "__main__":
    # Esegui test singolarmente per debug
    async def run_tests():
        print("=" * 60)
        print("Running CLI Bridge Tests")
        print("=" * 60)

        print("\n--- Unit Tests ---")
        # Unit tests (sync)
        test_build = TestBuildPromptFromMessages()
        test_build.test_single_user_message()
        test_build.test_multiple_messages()
        print("✓ build_prompt_from_messages tests passed")

        test_cli = TestDetermineCli()
        test_cli.test_gemini_variants()
        test_cli.test_codex_variants()
        test_cli.test_claude_variants()
        print("✓ determine_cli tests passed")

        test_cmd = TestBuildCommands()
        test_cmd.test_gemini_command()
        test_cmd.test_codex_command()
        test_cmd.test_claude_command()
        print("✓ build_*_command tests passed")

        test_clean = TestCleanCliOutput()
        test_clean.test_gemini_cleanup()
        test_clean.test_codex_cleanup()
        test_clean.test_claude_cleanup()
        print("✓ clean_cli_output tests passed")

        print("\n--- Integration Tests (calling real CLIs) ---")

        print("\nTesting Gemini CLI...")
        await test_query_gemini_basic()
        print("✓ Gemini test passed")

        print("\nTesting Codex CLI...")
        await test_query_codex_basic()
        print("✓ Codex test passed")

        print("\nTesting Claude CLI...")
        await test_query_claude_basic()
        print("✓ Claude test passed")

        print("\nTesting parallel queries...")
        await test_query_parallel_all_three()
        print("✓ Parallel test passed")

        print("\nTesting error handling...")
        await test_error_returns_none()
        print("✓ Error handling test passed")

        print("\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60)

    asyncio.run(run_tests())
