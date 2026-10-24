import unittest

from agent_insure import Book, quote


class QuoteTests(unittest.TestCase):
    def test_guardrails_reduce_premium(self):
        bare = quote(10_000, ["payments"], [], 250_000).annual_premium
        safe = quote(10_000, ["payments"], ["human_approval", "spend_caps", "audit_log"], 250_000).annual_premium
        self.assertLess(safe, bare * 0.5)

    def test_riskier_actions_cost_more(self):
        self.assertLess(quote(1000, ["read_only"], [], 100_000).annual_premium,
                        quote(1000, ["trading"], [], 100_000).annual_premium)

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


if __name__ == "__main__":
    unittest.main()
