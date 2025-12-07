# Browser Test Instructions for LLM Council

## Prerequisites
1. Start the LLM Council platform using `start.bat`
2. Ensure Playwright MCP is configured: `claude mcp list`

## Test Scenarios

### Test 1: Basic Page Load
1. Open browser to http://localhost:5173
2. Verify the LLM Council interface loads
3. Check that the sidebar shows "New Conversation" button

### Test 2: Create Conversation
1. Click "New Conversation" button
2. Verify a new conversation appears in the sidebar

### Test 3: Send Message
1. Type a test query in the input field
2. Click send or press Enter
3. Wait for Stage 1, Stage 2, and Stage 3 to complete
4. Verify all 3 models (Gemini, Codex, Claude) responded

### Test 4: View Stages
1. Click on Stage 1 tab to see individual responses
2. Click on Stage 2 tab to see peer rankings
3. Click on Stage 3 tab to see chairman synthesis

## Expected Results
- Stage 1: 3 responses from gemini, codex, claude
- Stage 2: 3 rankings with parsed_ranking arrays
- Stage 3: 1 synthesized response from chairman (gemini)
- Aggregate rankings should show model performance
