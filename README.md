<!-- sell-kit:start -->
# Agent Insure

[![CI](https://github.com/eliem08/agent-insure/actions/workflows/ci.yml/badge.svg)](https://github.com/eliem08/agent-insure/actions/workflows/ci.yml)

> **Price and adjudicate insurance for the expensive mistakes AI agents make.**

**Who it's for:** MGAs, brokers and insurtechs building errors-and-omissions cover for AI agents.

**The problem:** Underwriters have no rating model for agent risk and no consistent way to decide agent-caused claims.

**What you get:** A transparent underwriting worksheet with guardrail credits, plus claims adjudication covering warranties, exclusions, deductibles and aggregate limits.

## Quickstart

Customers receive a release archive with the wheel and the examples. Python 3.10+ and no other dependencies.

```bash
pip install agent_insure-0.1.0-py3-none-any.whl
agent-insure quote --spend-limit 10000 --actions payments email --guardrails human_approval audit_log --limit 250000
agent-insure --book book.json bind --holder acme --agent ap --spend-limit 5000 --actions payments --guardrails human_approval --limit 50000
agent-insure --book book.json claim POL-0001 --type wrong_payment --loss 8000 --guardrails-active human_approval
```

## Web app and API

Every command is also a JSON API endpoint and a browser form, served by the built-in web app.

```bash
agent-insure-web --port 8000          # then open http://127.0.0.1:8000
docker build -t agent-insure . && docker run -p 8000:8000 -v agent-insure-data:/data agent-insure
```

Endpoints: `POST /api/quote`, `POST /api/bind`, `POST /api/claim`, plus `GET /healthz` and `GET /api/spec` (machine-readable field list).
Files are sent as `{"name": ..., "content": ...}`, folders as `{"files": [...]}` or a base64 zip.

## Pricing

Every plan starts with a 14-day free trial. Prices in USD, billed monthly unless noted.

| Plan | Price | Includes |
|---|---|---|
| **Broker** | $199 per month | Unlimited quotes; Quote worksheets; Policy book |
| **Carrier** | $999 per month | Claims adjudication; Custom rating factors; Portfolio reports |
| **Enterprise** | $5,000 per month | Model customisation; Actuarial support; On-prem |

To start a trial or buy a plan, email **sales@YOUR-DOMAIN.com**.

## Licence

Proprietary. Copyright (c) 2026 eliem08. All rights reserved. Use requires a paid plan or an active trial; see [LICENSE](LICENSE).
<!-- sell-kit:end -->

## What it does

- **Quote**: premium from risk exposure — authority (spend limit, actions it
  can take), guardrails (human approval, spend caps, sandboxing, audit
  logging), prior claims, and coverage limit / deductible chosen
- **Bind** a policy (stored in a JSON book of business)
- **Claims**: file an incident → automatic adjudication:
  - coverage check (incident type covered?), policy active?
  - **warranty breach**: declared guardrails must have been on at loss time
  - exclusions (intentional misuse, prompt injection on an unpatched known CVE, …)
  - deductible + aggregate limit → payout
- Itemised rating worksheet so every premium is explainable

## Quickstart

```bash
pip install -e .
agent-insure quote --spend-limit 10000 --actions payments email --guardrails human_approval spend_caps audit_log --limit 250000
agent-insure bind --holder acme --agent ap-bot --spend-limit 10000 --actions payments --guardrails human_approval audit_log --limit 250000
agent-insure claim POL-0001 --type wrong_payment --loss 18000 --guardrails-active human_approval audit_log
```

## Roadmap

- Pricing from live telemetry (agent-tracer / agent-alarm) — usage-based premiums
- Reinsurance treaty export, loss-ratio dashboards
- Embedded cover at checkout for agent purchases (pairs with agent-buyer-protection)

## Development

Zero runtime dependencies; Python 3.10+.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m unittest discover -s tests -t .           # unit + CLI smoke tests
ruff check . && ruff format --check .               # lint + format
```

```
agent_insure/core.py       domain logic (pure, importable, fully tested)
agent_insure/__main__.py   CLI (`agent-insure ...` / `python -m agent_insure ...`)
tests/                unit tests + generated CLI smoke tests
```

CI runs lint and tests on Ubuntu and Windows across Python 3.10, 3.12 and 3.13.
Design, data model, trade-offs and production path: **[ARCHITECTURE.md](ARCHITECTURE.md)**.

Part of the [agent-economy](https://github.com/eliem08/agent-economy) portfolio (idea #7).
