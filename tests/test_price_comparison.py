"""
ProfinD — Unit Tests for DAA Price Comparison Engine
Tests Section 6 and Section 12 requirements:
- Linear scan minimum detection
- Delivery charge vs base price evaluation
- Equal minimum prices (ties)
- Empty lists and invalid price inputs
"""

import unittest
from price_comparison import calculate_total_paise, find_lowest_offer, analyze_offers


class TestPriceComparison(unittest.TestCase):

    def setUp(self):
        # Sample realistic offers
        self.sample_offers = [
            {'id': 101, 'store_name': 'Store A', 'price_paise': 5000000, 'delivery_charge_paise': 0, 'is_active': 1},
            {'id': 102, 'store_name': 'Store B', 'price_paise': 4900000, 'delivery_charge_paise': 200000, 'is_active': 1}, # Total = 5100000
            {'id': 103, 'store_name': 'Store C', 'price_paise': 4950000, 'delivery_charge_paise': 0, 'is_active': 1},      # Total = 4950000 (Lowest!)
            {'id': 104, 'store_name': 'Store D', 'price_paise': 5200000, 'delivery_charge_paise': 50000, 'is_active': 1}
        ]

    def test_calculate_total_paise_valid(self):
        """Test exact calculation of base price + delivery charge in paise."""
        offer = {'price_paise': 6599900, 'delivery_charge_paise': 4900}
        self.assertEqual(calculate_total_paise(offer), 6604800)

    def test_calculate_total_paise_free_delivery(self):
        """Test free delivery defaults to 0."""
        offer = {'price_paise': 6599900, 'delivery_charge_paise': 0}
        self.assertEqual(calculate_total_paise(offer), 6599900)

    def test_calculate_total_paise_invalid(self):
        """Test rejection of negative and malformed prices."""
        self.assertIsNone(calculate_total_paise({'price_paise': -100}))
        self.assertIsNone(calculate_total_paise({'price_paise': None}))
        self.assertIsNone(calculate_total_paise({'price_paise': 'abc'}))

    def test_find_lowest_offer_delivery_edge_case(self):
        """
        Critical Test:
        Store B has a lower base price (49,000) than Store A (50,000).
        However, Store B charges 2,000 for shipping (Total = 51,000).
        Store C has base 49,500 + FREE shipping (Total = 49,500).
        Store C must be chosen as the true lowest offer!
        """
        lowest, comparisons = find_lowest_offer(self.sample_offers)
        self.assertIsNotNone(lowest)
        self.assertEqual(lowest['id'], 103)
        self.assertEqual(lowest['store_name'], 'Store C')
        self.assertEqual(comparisons, 4)

    def test_equal_minimum_prices_ties(self):
        """Test when multiple stores offer the identical lowest price."""
        tied_offers = [
            {'id': 1, 'store_name': 'Amazon', 'price_paise': 2699000, 'delivery_charge_paise': 0, 'is_active': 1},
            {'id': 2, 'store_name': 'Croma', 'price_paise': 2699000, 'delivery_charge_paise': 0, 'is_active': 1},
            {'id': 3, 'store_name': 'Reliance', 'price_paise': 2799000, 'delivery_charge_paise': 0, 'is_active': 1}
        ]
        analysis = analyze_offers(tied_offers)
        self.assertEqual(analysis['lowest_total_paise'], 2699000)
        # Both Amazon (id=1) and Croma (id=2) must be recognized in lowest_ids
        self.assertEqual(analysis['lowest_ids'], {1, 2})
        self.assertEqual(analysis['max_savings_paise'], 100000) # 27,990 - 26,990 = 1,000

    def test_empty_offers_list(self):
        """Test graceful handling of empty lists."""
        lowest, comparisons = find_lowest_offer([])
        self.assertIsNone(lowest)
        self.assertEqual(comparisons, 0)

        analysis = analyze_offers([])
        self.assertIsNone(analysis['lowest_offer'])
        self.assertEqual(analysis['lowest_ids'], set())
        self.assertEqual(analysis['valid_offers_count'], 0)

    def test_linear_time_complexity_comparisons(self):
        """
        Verify that for n valid offers, exactly n-1 comparisons are made
        in the minimum scan (O(n) time complexity).
        """
        n = 8
        offers = [
            {'id': i, 'price_paise': (10000 + i * 500) * 100, 'delivery_charge_paise': 0, 'is_active': 1}
            for i in range(n)
        ]
        analysis = analyze_offers(offers)
        self.assertEqual(analysis['comparisons_count'], n - 1)
        self.assertEqual(analysis['daa_notes']['time_complexity'], 'O(n)')


if __name__ == '__main__':
    unittest.main()
