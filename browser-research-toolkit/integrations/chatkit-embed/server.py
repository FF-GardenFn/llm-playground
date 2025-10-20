#!/usr/bin/env python3
"""
ChatKit Embed backend (recommended integration path).

This FastAPI service exposes a single endpoint to create a ChatKit session
via the OpenAI Python SDK and returns the session's client_secret.

- POST /api/chatkit/session -> { "client_secret": "..." }

Environment variables:
- OPENAI_API_KEY: required; your OpenAI API key
- CHATKIT_WORKFLOW_ID: required; workflow ID from Agent Builder (e.g., wf_...)
- CHATKIT_BACKEND_TOKEN: optional; if set, clients must include
  Authorization: Bearer <CHATKIT_BACKEND_TOKEN>

Run (dev):
  export OPENAI_API_KEY=sk-...
  export CHATKIT_WORKFLOW_ID=wf_...
  export CHATKIT_BACKEND_TOKEN=REPLACE_ME   # optional
  uvicorn server:app --host 0.0.0.0 --port 8488

Security notes:
- Keep this service on trusted infrastructure you control. If you expose it
  to browsers, require the backend token and enforce CORS as needed.
- This service does not store client secrets; it simply forwards the value
  from OpenAI to your frontend.
"""
from __future__ import annotations

import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

try:
    from openai import OpenAI  # type: ignore
except Exception as e:  # pragma: no cover
    OpenAI = None  # type: ignore


app = FastAPI(title="BRT ChatKit Embed Backend", version="0.1.0")


class CreateSessionBody(BaseModel):
    user: Optional[str] = None  # deviceId or user ID from your app
    # You can extend with fields you want to pass to the workflow as inputs


def _require_config() -> tuple[str, str]:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    wf_id = os.environ.get("CHATKIT_WORKFLOW_ID", "").strip()
    if not api_key:
        raise HTTPException(500, "OPENAI_API_KEY is not set")
    if not wf_id:
        raise HTTPException(500, "CHATKIT_WORKFLOW_ID is not set")
    if OpenAI is None:  # pragma: no cover
        raise HTTPException(500, "openai package is not installed")
    return api_key, wf_id


def _check_auth(req: Request) -> None:
    token = os.environ.get("CHATKIT_BACKEND_TOKEN", "").strip()
    if not token:
        return
    auth = req.headers.get("authorization") or ""
    if not auth.lower().startswith("bearer "):
        raise HTTPException(401, "Missing token")
    if auth.split(" ", 1)[1].strip() != token:
        raise HTTPException(403, "Bad token")


@app.post("/api/chatkit/session")
async def create_chatkit_session(req: Request, body: CreateSessionBody):
    _check_auth(req)
    api_key, wf_id = _require_config()
    client = OpenAI(api_key=api_key)

    # The SDK signature may evolve; this mirrors current docs where sessions.create
    # accepts a dict-like payload with workflow id and user/device id.
    try:
        session = client.chatkit.sessions.create({
            "workflow": {"id": wf_id},
            "user": (body.user or "anonymous"),
        })
    except Exception as e:  # pragma: no cover
        raise HTTPException(502, f"ChatKit session creation failed: {e}")

    client_secret = getattr(session, "client_secret", None) or session.get("client_secret") if isinstance(session, dict) else None
    if not client_secret:
        # Defensive: try alternate attribute shapes
        try:
            client_secret = session["client_secret"]  # type: ignore[index]
        except Exception:
            pass
    if not client_secret:
        raise HTTPException(502, "client_secret missing in session response")

    return {"client_secret": client_secret}


@app.get("/health")
async def health():
    return {"ok": True}
