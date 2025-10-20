Siri Shortcut → Browser Research Toolkit Daemon

This small FastAPI service lets you speak a request to Siri and trigger the local BRT orchestrators with one sentence.

What it does
- Runs a local server on your Mac (http://<your-mac>.local:8373)
- Endpoint /siri parses utterances like:
  - "Research API migration audit on stripe.com/docs, github.com/stripe/*"
  - "triage API migration audit"
  - "open https://docs.google.com/document/d/..."
- Calls your configured orchestrator:
  - orchestrators/chrome-extension/orchestrator.py
  - orchestrators/mcp-clients/runner.py (stub included)
- Returns clean JSON for Shortcuts to display.

Quick start
1) Create a venv and install deps

    cd claude_in_browser/browser-research-toolkit/integrations/siri-daemon
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt

2) Configure

    cp config.example.yaml config.yaml
    # Edit token and (optionally) paths. Defaults point to the orchestrators in this repo.

3) Run

    uvicorn daemon:app --host 0.0.0.0 --port 8373

Shortcut (iPhone/Mac)
1. New Shortcut → name: Research Cell
2. Ask for Input ("What should I do?")
3. Get Contents of URL
   - URL: http://<your-mac>.local:8373/siri
   - Method: POST
   - Headers:
       - Authorization: Bearer <your-token>
       - Content-Type: application/json
   - Body (JSON):

        {
          "utterance": "{{Provided Input}}",
          "playbook": "chrome"
        }

4. Show Result

Examples you can literally say
- "research CLS mitigation on developers.chrome.com, web.dev"
- "triage CLS mitigation"
- "open https://docs.google.com/document/d/..."

Autostart (macOS)
- Edit launchd/com.hyper.brt.siri.plist paths
- Copy to ~/Library/LaunchAgents/
- launchctl load ~/Library/LaunchAgents/com.hyper.brt.siri.plist

Security defaults
- Bearer token required (rejects unauth'd calls)
- Local network only; don't expose to WAN
- Daemon only runs your configured orchestrators—no arbitrary shell

Notes
- The MCP runner is a minimal stub. Replace with your client integration when ready.
- The Chrome orchestrator will emit CHARTER.md and COMMANDS.json to ~/.tab_orchestrator/tasks/<slug>.
