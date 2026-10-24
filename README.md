# agent-insure

[![CI](https://github.com/eliem08/agent-insure/actions/workflows/ci.yml/badge.svg)](https://github.com/eliem08/agent-insure/actions/workflows/ci.yml)

> **Geico for agents** — insurance for when an agent makes an expensive mistake.

An agent wires $40k to the wrong vendor, deletes a production table or
emails the whole customer list. Who pays? `agent-insure` is the underwriting
and claims engine for agent errors & omissions cover.

## What the MVP does

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
