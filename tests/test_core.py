import unittest

from agent_insure import Book, quote


class QuoteTests(unittest.TestCase):
    def test_guardrails_reduce_premium(self):
        bare = quote(10_000, ["payments"], [], 250_000).annual_premium
        safe = quote(10_000, ["payments"], ["human_approval", "spend_caps", "audit_log"], 250_000).annual_premium
        self.assertLess(safe, bare * 0.5)

    def test_riskier_actions_cost_more(self):
        self.assertLess(
            quote(1000, ["read_only"], [], 100_000).annual_premium, quote(1000, ["trading"], [], 100_000).annual_premium
        )

    def test_validation(self):
        with self.assertRaises(ValueError):
            quote(1, ["teleport"], [], 1000)


class ClaimTests(unittest.TestCase):
    def setUp(self):
        self.book = Book()
        self.p = self.book.bind("acme", "ap-bot", 10_000, ["payments"], ["human_approval"], 20_000, deductible=1000)

    def test_paid_with_deductible_and_cap(self):
        r = self.book.claim(self.p.policy_id, "wrong_payment", 15_000, ["human_approval"])
        self.assertEqual(r.payout, 14_000)
        r2 = self.book.claim(self.p.policy_id, "wrong_payment", 15_000, ["human_approval"])
        self.assertEqual(r2.payout, 6_000)  # aggregate limit 20k

    def test_warranty_breach_and_exclusions(self):
        r = self.book.claim(self.p.policy_id, "wrong_payment", 5000, [])
        self.assertFalse(r.approved)
        self.assertIn("warranty breach", r.reasons[0])
        r = self.book.claim(self.p.policy_id, "alien_invasion", 5000, ["human_approval"], cause="intentional_misuse")
        self.assertEqual(len(r.reasons), 2)

    def test_zero_or_negative_limits_and_negative_claims_history_are_rejected(self):
        for kwargs in ({"limit": 0}, {"limit": -50_000}, {"spend_limit": -1}, {"prior_claims": -3}):
            args = {"spend_limit": 1000, "actions": ["email"], "guardrails": [], "limit": 100_000, **kwargs}
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                quote(**args)

    def test_listing_a_guardrail_twice_is_not_double_credit(self):
        once = quote(1000, ["payments"], ["human_approval"], 500_000).annual_premium
        twice = quote(1000, ["payments"], ["human_approval", "human_approval"], 500_000).annual_premium
        self.assertEqual(once, twice)

    def test_nan_or_negative_loss_is_rejected(self):
        b = Book()
        p = b.bind("acme", "bot", 1000, ["payments"], [], 100_000)
        for loss in (float("nan"), -10_000):
            with self.subTest(loss=loss), self.assertRaises(ValueError):
                b.claim(p.policy_id, "wrong_payment", loss, [])


if __name__ == "__main__":
    unittest.main()
