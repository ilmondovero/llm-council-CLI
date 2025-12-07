# CLI Installation Guide

This guide will help you install and configure the three CLI tools required by LLM Council:

- **Gemini CLI** (Google)
- **Codex CLI** (OpenAI)
- **Claude CLI** (Anthropic)

## Overview

LLM Council uses local CLI tools to interact with AI models instead of API keys. This approach:
- Uses your existing subscriptions (no additional API costs)
- Keeps your data local and private
- Leverages official CLI tools from each provider
- Provides better integration with your development environment

## Prerequisites

Before installing the CLIs, ensure you have:

- **Node.js 14+** (for npm package installation)
- **Python 3.10+** (for the LLM Council backend)
- Active subscriptions or credits with:
  - Google AI Studio / Gemini
  - OpenAI (ChatGPT Plus or API access)
  - Anthropic Claude (Pro subscription or API access)

## 1. Gemini CLI Installation

### Install via npm

```bash
npm install -g @google/generative-ai-cli
```

**Alternative package name** (if the above doesn't work):
```bash
npm install -g gemini-cli
```

### Authentication

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to get your API key

2. Set up authentication:

**Option A: Environment variable**
```bash
# Windows
set GOOGLE_API_KEY=your_api_key_here

# Linux/Mac
export GOOGLE_API_KEY=your_api_key_here
```

**Option B: CLI login**
```bash
gemini auth login
```

### Verify Installation

Test the Gemini CLI:
```bash
echo "Hello, Gemini!" | gemini
```

Expected output: A response from Gemini welcoming you back or answering your greeting.

### Troubleshooting Gemini CLI

**Command not found:**
- Check npm global bin location: `npm config get prefix`
- Add to PATH if needed:
  - Windows: Add `%USERPROFILE%\AppData\Roaming\npm` to PATH
  - Linux/Mac: Add `$HOME/.npm-global/bin` to PATH

**Authentication errors:**
- Verify API key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)
- Check environment variable is set: `echo %GOOGLE_API_KEY%` (Windows) or `echo $GOOGLE_API_KEY` (Unix)
- Try re-authenticating: `gemini auth logout` then `gemini auth login`

**Rate limiting:**
- Free tier has rate limits - consider upgrading if you hit them frequently
- Wait a few minutes and try again

## 2. Codex CLI Installation

### Install via npm

```bash
npm install -g @openai/codex-cli
```

**Alternative installation** (if above doesn't work):
```bash
npm install -g openai-cli
```

### Authentication

1. Get your OpenAI API key from [OpenAI API Keys](https://platform.openai.com/api-keys)

2. Set up authentication:

**Option A: Environment variable**
```bash
# Windows
set OPENAI_API_KEY=sk-proj-...

# Linux/Mac
export OPENAI_API_KEY=sk-proj-...
```

**Option B: CLI configuration**
```bash
codex config set api-key sk-proj-...
```

### Verify Installation

Test the Codex CLI:
```bash
codex exec "What is 2+2?"
```

Expected output: A response calculating that 2+2=4.

### Troubleshooting Codex CLI

**Command not found:**
- Ensure npm global installation worked: `npm list -g --depth=0`
- Check PATH includes npm bin directory
- Try `npx @openai/codex-cli exec "test"` as alternative

**Authentication errors:**
- Verify API key starts with `sk-proj-` or `sk-`
- Check key is active at [OpenAI Platform](https://platform.openai.com/api-keys)
- Ensure you have credits/billing enabled

**Model access errors:**
- Some models require specific access levels
- Default model should work with any OpenAI account
- Check [OpenAI Status](https://status.openai.com/) for outages

**Rate limiting:**
- Free tier has strict rate limits
- Consider upgrading to paid tier for higher limits
- LLM Council makes 3-6 calls per query (stage 1, 2, and optional stage 3)

## 3. Claude CLI Installation

### Install via npm

```bash
npm install -g @anthropic-ai/claude-cli
```

**Alternative method** (official Anthropic installer):
Visit [Anthropic CLI Docs](https://docs.anthropic.com/claude/docs/cli) for the latest installation method.

### Authentication

1. Get your API key from [Anthropic Console](https://console.anthropic.com/settings/keys)

2. Set up authentication:

**Option A: Environment variable**
```bash
# Windows
set ANTHROPIC_API_KEY=sk-ant-...

# Linux/Mac
export ANTHROPIC_API_KEY=sk-ant-...
```

**Option B: CLI login**
```bash
claude auth login
```

**Option C: Interactive prompt**
The Claude CLI may prompt you for credentials on first use.

### Verify Installation

Test the Claude CLI:
```bash
echo "Hello, Claude!" | claude -p
```

The `-p` flag enables "plain" mode for cleaner output.

Expected output: A friendly response from Claude.

### Troubleshooting Claude CLI

**Command not found:**
- Check Claude CLI installation: `npm list -g | grep claude`
- Ensure npm global bin is in PATH
- Try reinstalling: `npm uninstall -g @anthropic-ai/claude-cli && npm install -g @anthropic-ai/claude-cli`

**Authentication errors:**
- Verify API key format (should start with `sk-ant-`)
- Check key is active at [Anthropic Console](https://console.anthropic.com/settings/keys)
- Try using `--api-key` flag directly: `claude --api-key=sk-ant-... -p`

**Permission errors:**
- The CLI may require certain permissions
- Use `--dangerously-skip-permissions` flag if needed (already configured in LLM Council)

**Rate limiting:**
- Free tier may have strict limits
- Claude Pro subscription provides higher limits
- Monitor usage at [Anthropic Console](https://console.anthropic.com/settings/usage)

## 4. Final Verification

Once all three CLIs are installed, verify they all work together:

### Quick Test Script

Create a test file `test_clis.bat` (Windows) or `test_clis.sh` (Unix):

**Windows (test_clis.bat):**
```batch
@echo off
echo Testing Gemini CLI...
echo "Test" | gemini
echo.

echo Testing Codex CLI...
codex exec "Test"
echo.

echo Testing Claude CLI...
echo "Test" | claude -p
echo.

echo All CLIs tested!
pause
```

**Linux/Mac (test_clis.sh):**
```bash
#!/bin/bash

echo "Testing Gemini CLI..."
echo "Test" | gemini
echo

echo "Testing Codex CLI..."
codex exec "Test"
echo

echo "Testing Claude CLI..."
echo "Test" | claude -p
echo

echo "All CLIs tested!"
```

Make it executable and run:
```bash
# Linux/Mac
chmod +x test_clis.sh
./test_clis.sh

# Windows
test_clis.bat
```

### Expected Results

Each CLI should return a brief response. If all three work, you're ready to run LLM Council!

## 5. Advanced Configuration

### Setting Default Models

Some CLIs allow you to specify default models:

**Codex/OpenAI:**
```bash
codex config set model gpt-4o
```

**Gemini:**
```bash
gemini config set model gemini-2.0-flash
```

**Claude:**
Claude CLI uses the latest available model by default.

### Timeout Configuration

If you experience timeouts, you can adjust CLI settings or modify `backend/cli_bridge.py` in LLM Council:

```python
# In cli_bridge.py, line ~48
timeout=240.0  # Increase from 120 to 240 seconds
```

### Proxy Configuration

If you're behind a corporate proxy:

```bash
# Windows
set HTTP_PROXY=http://proxy.example.com:8080
set HTTPS_PROXY=http://proxy.example.com:8080

# Linux/Mac
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

## 6. Updating CLIs

Keep your CLIs up to date for best performance:

```bash
# Update all CLIs
npm update -g @google/generative-ai-cli
npm update -g @openai/codex-cli
npm update -g @anthropic-ai/claude-cli
```

## 7. Uninstalling CLIs

If you need to uninstall:

```bash
npm uninstall -g @google/generative-ai-cli
npm uninstall -g @openai/codex-cli
npm uninstall -g @anthropic-ai/claude-cli
```

## Common Issues

### Issue: "Module not found" errors

**Solution:**
- Clear npm cache: `npm cache clean --force`
- Reinstall CLIs
- Check Node.js version: `node --version` (need 14+)

### Issue: CLIs work individually but not in LLM Council

**Solution:**
- Verify PATH is set in the shell LLM Council runs from
- Check backend logs for specific errors: Look at terminal running `backend.main`
- Test subprocess execution manually:
  ```python
  import subprocess
  result = subprocess.run(['gemini'], input='test', capture_output=True, text=True)
  print(result.stdout)
  ```

### Issue: Intermittent failures

**Solution:**
- Check network connectivity
- Verify API service status:
  - [Google AI Status](https://status.cloud.google.com/)
  - [OpenAI Status](https://status.openai.com/)
  - [Anthropic Status](https://status.anthropic.com/)
- Increase timeout in `backend/cli_bridge.py`
- Check rate limits on your accounts

### Issue: Encoding/Unicode errors

**Solution:**
- Ensure terminal supports UTF-8:
  - Windows: `chcp 65001`
  - Linux/Mac: `export LANG=en_US.UTF-8`
- Update Python and Node.js to latest versions
- Check `backend/cli_bridge.py` uses `encoding='utf-8'`

## Next Steps

Once all CLIs are installed and verified:

1. Return to the main [README.md](../README.md)
2. Follow the Quick Start guide
3. Run `start.bat` (Windows) or `start.sh` (Unix)
4. Start asking questions to your LLM Council!

## Support

For CLI-specific issues:
- **Gemini**: [Google AI Documentation](https://ai.google.dev/docs)
- **Codex/OpenAI**: [OpenAI Documentation](https://platform.openai.com/docs)
- **Claude**: [Anthropic Documentation](https://docs.anthropic.com/)

For LLM Council issues:
- Check the [Troubleshooting section](../README.md#troubleshooting) in the main README
- Review backend logs for detailed error messages
- Test each CLI individually to isolate the problem

---

**Note**: CLI tools and their package names may change. If you encounter issues, check each provider's official documentation for the latest installation methods.
