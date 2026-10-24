"""Underwriting, policies and claims adjudication for agent E&O cover."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict

__all__ = ["ACTION_RISK", "GUARDRAIL_CREDITS", "COVERED_INCIDENTS", "Quote", "Policy", "ClaimResult", "quote", "Book"]

BASE_RATE = 0.012  # annual premium as share of the coverage limit, before modifiers
ACTION_RISK = {"read_only": 0.5, "email": 1.1, "payments": 1.6, "code_deploy": 1.5, "data_delete": 1.7, "trading": 2.0, "customer_chat": 1.2}
GUARDRAIL_CREDITS = {"human_approval": 0.30, "spend_caps": 0.15, "sandbox": 0.15, "audit_log": 0.10, "rollback": 0.10}
COVERED_INCIDENTS = {"wrong_payment", "duplicate_payment", "data_loss", "erroneous_communication", "bad_trade", "service_outage"}
EXCLUSIONS = {"intentional_misuse", "known_unpatched_vuln", "fines_penalties"}
DEDUCTIBLE_CREDIT = {0: 1.0, 1000: 0.92, 5000: 0.82, 25000: 0.70}


@dataclass
class Quote:
    annual_premium: float
    worksheet: dict


def quote(spend_limit: float, actions: list[str], guardrails: list[str], limit: float,
          deductible: int = 1000, prior_claims: int = 0) -> Quote:
    unknown = [a for a in actions if a not in ACTION_RISK]
    if unknown:
        raise ValueError(f"unknown actions {unknown}")
    if deductible not in DEDUCTIBLE_CREDIT:
        raise ValueError(f"deductible must be one of {sorted(DEDUCTIBLE_CREDIT)}")
    base = limit * BASE_RATE
    action_mult = max(ACTION_RISK[a] for a in actions) * (1 + 0.1 * (len(actions) - 1)) if actions else 0.5
    authority_mult = 1 + min(spend_limit / limit, 1.0)
    credit = min(sum(GUARDRAIL_CREDITS.get(g, 0) for g in guardrails), 0.6)
    claims_mult = 1 + 0.25 * prior_claims
    premium = base * action_mult * authority_mult * (1 - credit) * claims_mult * DEDUCTIBLE_CREDIT[deductible]
    ws = {
        "base (limit x rate)": round(base, 2),
        "action exposure x": round(action_mult, 3),
        "spend authority x": round(authority_mult, 3),
        "guardrail credit -": round(credit, 3),
        "claims history x": claims_mult,
        "deductible x": DEDUCTIBLE_CREDIT[deductible],
    }
    return Quote(round(max(premium, 250.0), 2), ws)


@dataclass
class Policy:
    policy_id: str
    holder: str
    agent: str
    limit: float
    deductible: int
    actions: list
    guardrails: list
    premium: float
    paid_out: float = 0.0
    active: bool = True
    claims: list = field(default_factory=list)


@dataclass
class ClaimResult:
    approved: bool
    payout: float
    reasons: list


class Book:
    def __init__(self, path: str | None = None):
        self.path = path
        self.policies: dict[str, Policy] = {}
        if path and os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                self.policies = {p["policy_id"]: Policy(**p) for p in json.load(fh)}

    def save(self):
        if self.path:
            with open(self.path, "w", encoding="utf-8") as fh:
                json.dump([asdict(p) for p in self.policies.values()], fh, indent=2)

    def bind(self, holder, agent, spend_limit, actions, guardrails, limit, deductible=1000, prior_claims=0) -> Policy:
        q = quote(spend_limit, actions, guardrails, limit, deductible, prior_claims)
        pid = f"POL-{len(self.policies) + 1:04d}"
        self.policies[pid] = Policy(pid, holder, agent, limit, deductible, list(actions), list(guardrails), q.annual_premium)
        return self.policies[pid]

    def claim(self, policy_id: str, incident: str, loss: float, guardrails_active: list[str], cause: str | None = None) -> ClaimResult:
        p = self.policies.get(policy_id)
        if not p:
            return ClaimResult(False, 0, ["policy not found"])
        reasons = []
        if not p.active:
            reasons.append("policy inactive")
        if incident not in COVERED_INCIDENTS:
            reasons.append(f"incident type {incident!r} not covered")
        if cause in EXCLUSIONS:
            reasons.append(f"excluded cause: {cause}")
        breached = sorted(set(p.guardrails) - set(guardrails_active))
        if breached:
            reasons.append(f"warranty breach: declared guardrails off at time of loss: {breached}")
        if reasons:
            result = ClaimResult(False, 0, reasons)
        else:
            remaining = p.limit - p.paid_out
            payout = max(0.0, min(loss - p.deductible, remaining))
            notes = [f"loss {loss:,.2f} - deductible {p.deductible:,}"]
            if loss - p.deductible > remaining:
                notes.append(f"capped at remaining aggregate limit {remaining:,.2f}")
            p.paid_out += payout
            result = ClaimResult(payout > 0, round(payout, 2), notes if payout > 0 else ["loss below deductible"])
        p.claims.append({"incident": incident, "loss": loss, "approved": result.approved, "payout": result.payout})
        return result
