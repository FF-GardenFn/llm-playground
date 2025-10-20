ChatKit Embed Backend (Recommended Integration)

Purpose
- Provide a minimal FastAPI backend that creates ChatKit sessions using the OpenAI Python SDK so you can embed ChatKit in your frontend.
- This follows the "OpenAI-hosted ChatKit" path from the docs: your frontend loads ChatKit UI and calls this backend to retrieve a short‑lived client secret bound to your workflow ID.

Endpoints
- POST /api/chatkit/session  →  { "client_secret": "..." }
- GET  /health               →  { "ok": true }

Quick start (local dev)
1) Create a virtualenv and install deps:

   cd claude_in_browser/browser-research-toolkit/integrations/chatkit-embed
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt

2) Export required environment variables:

   export OPENAI_API_KEY=sk-...               # required
   export CHATKIT_WORKFLOW_ID=wf_...          # required (from Agent Builder)
   export CHATKIT_BACKEND_TOKEN=REPLACE_ME    # optional; enables Bearer auth

3) Run the server:

   uvicorn server:app --host 0.0.0.0 --port 8488

4) Frontend: fetch client secret and render ChatKit.
   Example (TypeScript helper):

   // chatkit.ts
   export async function getChatKitClientSecret(deviceId: string): Promise<string> {
     const res = await fetch("/api/chatkit/session", {
       method: "POST",
       headers: {
         "Content-Type": "application/json",
         // If CHATKIT_BACKEND_TOKEN is set, add:
         // Authorization: `Bearer ${import.meta.env.VITE_CHATKIT_BACKEND_TOKEN}`
       },
       body: JSON.stringify({ user: deviceId }),
     });
     if (!res.ok) {
       throw new Error(`session failed: ${res.status}`);
     }
     const data = await res.json();
     return data.client_secret;
   }

   // index.html
   // <script src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js" async></script>

   // React example
   // import { ChatKit, useChatKit } from '@openai/chatkit-react';
   // const { control } = useChatKit({
   //   api: { getClientSecret: () => getChatKitClientSecret(deviceId) }
   // });
   // return <ChatKit control={control} className="h-[600px] w-[320px]" />;

Notes
- This backend does not persist or log the client secret; it simply forwards the value from OpenAI to your client.
- Keep this service on trusted infra you control. If exposed to browsers, enable the backend token and configure CORS appropriately.
- For full control (advanced integration), see the openai-chatkit-advanced-samples in this repo, which runs a ChatKit‑compatible server and UI locally.

Security
- Recommended: set CHATKIT_BACKEND_TOKEN and require Authorization: Bearer <token> on requests.
- Do not expose this service on the public internet without appropriate controls (CORS, WAF, rate limits).
