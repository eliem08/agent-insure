import argparse
import sys

from .core import ACTION_RISK, GUARDRAIL_CREDITS, Book, quote


def _risk_args(p):
    p.add_argument("--spend-limit", type=float, required=True)
    p.add_argument("--actions", nargs="+", required=True, choices=sorted(ACTION_RISK))
    p.add_argument("--guardrails", nargs="*", default=[], choices=sorted(GUARDRAIL_CREDITS))
    p.add_argument("--limit", type=float, required=True, help="coverage limit")
    p.add_argument("--deductible", type=int, default=1000)
    p.add_argument("--prior-claims", type=int, default=0)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="agent-insure")
    ap.add_argument("--book", default="policies.json")
    sub = ap.add_subparsers(dest="cmd", required=True)
    _risk_args(sub.add_parser("quote"))
    b = sub.add_parser("bind")
    b.add_argument("--holder", required=True)
    b.add_argument("--agent", required=True)
    _risk_args(b)
    c = sub.add_parser("claim")
    c.add_argument("policy_id")
    c.add_argument("--type", required=True)
    c.add_argument("--loss", type=float, required=True)
    c.add_argument("--guardrails-active", nargs="*", default=[])
    c.add_argument("--cause")
    a = ap.parse_args(argv)

    if a.cmd == "quote":
        q = quote(a.spend_limit, a.actions, a.guardrails, a.limit, a.deductible, a.prior_claims)
        for k, v in q.worksheet.items():
            print(f"  {k:<22} {v}")
        print(f"Annual premium: ${q.annual_premium:,.2f}  (${q.annual_premium / 12:,.2f}/mo)")
        return 0
    book = Book(a.book)
    if a.cmd == "bind":
        p = book.bind(a.holder, a.agent, a.spend_limit, a.actions, a.guardrails, a.limit, a.deductible, a.prior_claims)
        print(f"Bound {p.policy_id} for {p.holder}/{p.agent}: limit ${p.limit:,.0f}, premium ${p.premium:,.2f}")
    else:
        r = book.claim(a.policy_id, a.type, a.loss, a.guardrails_active, a.cause)
        print(("APPROVED" if r.approved else "DENIED") + f"  payout ${r.payout:,.2f}")
        for reason in r.reasons:
            print(f"  - {reason}")
    book.save()
    return 0


if __name__ == "__main__":
    sys.exit(main())
