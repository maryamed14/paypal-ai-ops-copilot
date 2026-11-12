# PayPal AI Operations Copilot

A sandbox-only FastAPI prototype that creates PayPal orders and explains their status using an LLM (with a deterministic fallback). **Not production-ready.** No live payments or automatic refunds.

## Windows setup

```powershell
cd D:\Projects\paypal-ai-ops-copilot
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` with your **Sandbox** Client ID and Secret. Optionally add an OpenAI API key; without it, the app uses a deterministic explanation fallback. Never commit `.env`.

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1
```

Open http://127.0.0.1:8000/docs. For a local OAuth test only, add `ENABLE_LOCAL_AUTH_TEST=1` to `.env`, restart, and call `GET /paypal/test-auth`. Disable this endpoint before any public deployment.

## Test a Sandbox payment

1. `POST /orders` with `{"amount":"10.00","currency":"EUR"}`.
2. Open the returned link with `rel: approve` in a browser. Log in with a **Sandbox personal buyer** account (not your real PayPal credentials).
3. After buyer approval, call `POST /orders/{order_id}/capture`.
4. Call `GET /orders/{order_id}` and `GET /orders/{order_id}/analysis`.

OAuth and API requests are made server-side. No token or secret is intentionally returned by the authentication test endpoint.

## Tests

```powershell
python -m pytest -q
```

## Scope and limitations

- All PayPal requests are hardcoded to `https://api-m.sandbox.paypal.com`.
- No database, webhook processing, frontend, user authentication, or rate limiting yet.
- LLM output is advisory only. The application does not execute AI-suggested actions.
- The analysis endpoint sends limited order fields (status, ID, intent) to the configured LLM provider when an API key is set. Use synthetic Sandbox data only.
- `/orders/{id}/capture` is a manual test operation. It is not AI-controlled.
- **Do not publicly deploy this starter as-is**; protect API endpoints and implement durable idempotency, webhook verification, audit logging, and abuse controls first.

## Hackathon next steps

Add webhook verification, PostgreSQL persistence, an operator dashboard, automated integration tests, and a short demo video. A public GitHub repository must include an open-source license and runnable instructions.
