"""
ProfinD — Price Comparison & DAA Algorithmic Engine
Implements Design and Analysis of Algorithms (DAA) optimal Linear Scan Minimum detection.

Time Complexity: O(n)
Auxiliary Space Complexity: O(1)
"""

from typing import List, Dict, Any, Optional, Tuple


def calculate_total_paise(offer: Any) -> Optional[int]:
    """
    Calculates the comparable total price (Base Price + Delivery Charge) in paise.
    Supports standard dicts, sqlite3.Row, and custom objects.
    Returns None if price data is invalid or negative.
    """
    try:
        # Extract price_paise
        if hasattr(offer, 'keys'):
            # sqlite3.Row or dict
            price = offer['price_paise'] if 'price_paise' in offer.keys() else None
            delivery = offer['delivery_charge_paise'] if 'delivery_charge_paise' in offer.keys() else 0
        else:
            price = getattr(offer, 'price_paise', None)
            delivery = getattr(offer, 'delivery_charge_paise', 0)

        if price is None or price < 0:
            return None
        if delivery is None or delivery < 0:
            delivery = 0

        return int(price) + int(delivery)
    except (TypeError, ValueError, KeyError):
        return None


def find_lowest_offer(offers: List[Any]) -> Tuple[Optional[Dict[str, Any]], int]:
    """
    DAA Linear Scan Algorithm:
    Identifies the single lowest comparable offer from a collection of store offers.
    
    Algorithm:
        1. Initialize min_offer = None, min_total = infinity.
        2. Iterate through each offer in the list sequentially (linear scan).
        3. Calculate total = base_price + delivery_charge.
        4. If total < min_total:
               min_total = total
               min_offer = offer
        5. Return min_offer and the number of comparisons performed.
        
    Complexity Analysis:
        - Time Complexity: O(n), where n is the number of offers.
          Each element is examined once.
        - Space Complexity: O(1) auxiliary space.
        - Robustness: Safely ignores invalid, inactive, or malformed prices.
    """
    if not offers:
        return None, 0

    min_offer = None
    min_total = float('inf')
    comparisons = 0

    for raw in offers:
        offer = dict(raw) if hasattr(raw, 'keys') else raw
        if offer.get('is_active', 1) == 0:
            continue

        total = calculate_total_paise(offer)
        if total is None:
            continue

        comparisons += 1
        if total < min_total:
            min_total = total
            min_offer = offer

    return min_offer, comparisons


def analyze_offers(offers: List[Any]) -> Dict[str, Any]:
    """
    Performs comprehensive price analysis for a product across all stores.
    Identifies:
      - Lowest comparable offer
      - All offer IDs tied for lowest price (handles equal minimum prices)
      - Highest comparable offer
      - Maximum potential user savings (Highest Total - Lowest Total)
      - Algorithmic metadata for DAA examination defense
    """
    if not offers:
        return {
            'lowest_offer': None,
            'lowest_ids': set(),
            'lowest_total_paise': None,
            'highest_total_paise': None,
            'max_savings_paise': 0,
            'valid_offers_count': 0,
            'comparisons_count': 0,
            'daa_notes': {
                'algorithm': 'Linear Scan Minimum',
                'time_complexity': 'O(n)',
                'space_complexity': 'O(1)',
                'rationale': 'Sorting takes O(n log n). A single linear pass finds the minimum in O(n) without reordering data.'
            }
        }

    valid_offers = []
    for raw in offers:
        tot = calculate_total_paise(raw)
        if tot is not None:
            d = dict(raw) if hasattr(raw, 'keys') else dict(raw.__dict__)
            d['computed_total_paise'] = tot
            valid_offers.append(d)

    if not valid_offers:
        return {
            'lowest_offer': None,
            'lowest_ids': set(),
            'lowest_total_paise': None,
            'highest_total_paise': None,
            'max_savings_paise': 0,
            'valid_offers_count': 0,
            'comparisons_count': 0,
            'daa_notes': {
                'algorithm': 'Linear Scan Minimum',
                'time_complexity': 'O(n)',
                'space_complexity': 'O(1)',
                'rationale': 'No valid prices found.'
            }
        }

    # Pass 1: Find minimum and maximum total price using Linear Scan
    min_offer = valid_offers[0]
    min_total = min_offer['computed_total_paise']
    max_total = min_total
    comparisons = 0

    for offer in valid_offers[1:]:
        comparisons += 1
        curr_total = offer['computed_total_paise']
        if curr_total < min_total:
            min_total = curr_total
            min_offer = offer
        if curr_total > max_total:
            max_total = curr_total

    # Pass 2: Collect all offer IDs matching the minimum total (handles ties)
    lowest_ids = {
        offer.get('id')
        for offer in valid_offers
        if offer['computed_total_paise'] == min_total and offer.get('id') is not None
    }

    max_savings = max(0, max_total - min_total)

    return {
        'lowest_offer': min_offer,
        'lowest_ids': lowest_ids,
        'lowest_total_paise': min_total,
        'highest_total_paise': max_total,
        'max_savings_paise': max_savings,
        'valid_offers_count': len(valid_offers),
        'comparisons_count': comparisons,
        'daa_notes': {
            'algorithm': 'Linear Scan Minimum',
            'time_complexity': 'O(n)',
            'space_complexity': 'O(1)',
            'comparisons': comparisons,
            'rationale': (
                f'Evaluated {len(valid_offers)} offers with {comparisons} comparisons. '
                f'Linear scan runs in O(n) time, strictly better than sorting which takes O(n log n).'
            )
        }
    }


def analyze_price_history(history_rows: List[Any]) -> Dict[str, Any]:
    """
    Analyzes chronological historical price checkpoints for a product.
    Implements price change estimation and directional trend calculation.
    """
    if not history_rows or len(history_rows) < 2:
        return {
            'has_history': False,
            'timeline': [],
            'trend_status': 'INSUFFICIENT_DATA',
            'trend_description': 'Insufficient historical checkpoints recorded for trend analysis.'
        }

    timeline = []
    for r in history_rows:
        d = dict(r) if hasattr(r, 'keys') else r
        timeline.append(d)

    initial = timeline[0]['price_paise']
    latest = timeline[-1]['price_paise']
    diff = latest - initial
    pct = round((diff / initial) * 100, 1) if initial > 0 else 0.0

    if pct < -1.0:
        status = 'DROPPED'
        desc = f"Price has dropped by {abs(pct)}% over the observation window (Favorable time to purchase)."
    elif pct > 1.0:
        status = 'INCREASED'
        desc = f"Price has increased by {pct}% compared to earliest recorded checkpoint."
    else:
        status = 'STABLE'
        desc = "Price has remained stable across recorded checkpoints."

    return {
        'has_history': True,
        'timeline': timeline,
        'initial_price_paise': initial,
        'latest_price_paise': latest,
        'price_change_paise': diff,
        'percent_change': pct,
        'trend_status': status,
        'trend_description': desc
    }
