"""
PI-061-17: Stronger Claim Test

Purpose:
    Test whether the classifier incorrectly matches a claim to
    library_card_required when the claim contains the Known Fact
    but adds stronger requirements, additional conditions, or
    additional claims.

This experiment intentionally does not modify canonical_claim.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

from canonical_claim import match_known_fact


EXPECTED_TARGET = "library_card_required"


TEST_CASES = [
    {
        "id": "SC-01",
        "direction": "necessary",
        "claim": "電子資料サービスの利用には図書館カードが必要である。",
        "expected": EXPECTED_TARGET,
    },
    {
        "id": "SC-02",
        "direction": "stronger",
        "claim": (
            "電子資料サービスを利用するには、"
            "図書館カードと本人確認書類の両方が必要である。"
        ),
        "expected": None,
    },
    {
        "id": "SC-03",
        "direction": "additional_claim",
        "claim": (
            "電子資料サービスを利用するには図書館カードが必要であり、"
            "利用には事前登録も必要である。"
        ),
        "expected": None,
    },
    {
        "id": "SC-04",
        "direction": "additional_condition",
        "claim": (
            "電子資料サービスを利用するには図書館カードが必要で、"
            "さらに18歳以上でなければならない。"
        ),
        "expected": None,
    },
    {
        "id": "SC-05",
        "direction": "sufficient",
        "claim": (
            "図書館カードを持っていれば、"
            "電子資料サービスを利用できる。"
        ),
        "expected": None,
    },
    {
        "id": "SC-06",
        "direction": "additional_requirement",
        "claim": (
            "電子資料サービスを利用するには図書館カードだけでなく、"
            "利用者登録も必要である。"
        ),
        "expected": None,
    },
    {
        "id": "SC-07",
        "direction": "condition",
        "claim": (
            "電子資料サービスを利用するには図書館カードが必要だが、"
            "利用できるのは開館時間内に限られる。"
        ),
        "expected": None,
    },
    {
        "id": "SC-08",
        "direction": "reason",
        "claim": (
            "電子資料サービスを利用するには図書館カードが必要であり、"
            "その理由は利用者を識別するためである。"
        ),
        "expected": None,
    },
    {
        "id": "SC-09",
        "direction": "stronger",
        "claim": (
            "電子資料サービスを利用するためには、"
            "図書館カードを持っているだけでは不十分で、"
            "図書館への来館も必要である。"
        ),
        "expected": None,
    },
    {
        "id": "SC-10",
        "direction": "necessary",
        "claim": (
            "図書館カードを所持していなければ、"
            "電子資料サービスを利用することはできない。"
        ),
        "expected": EXPECTED_TARGET,
    },
]


def run_test(case: dict) -> bool:
    result = match_known_fact(case["claim"])
    actual = result.fact_id

    passed = actual == case["expected"]

    print(case["id"])
    print(f"Direction: {case['direction']}")
    print(f"Claim:    {case['claim']}")
    print(f"Expected: {case['expected']}")
    print(f"Actual:   {actual}")
    print(f"Result:   {'PASS' if passed else 'FAIL'}")
    print()


    if not passed:
        print("Raw response:")
        print(result.raw_response)
        print()

    return passed


def main() -> int:
    print("=" * 70)
    print("PI-061-17: Stronger Claim Test")
    print("=" * 70)
    print()

    results = [run_test(case) for case in TEST_CASES]

    passed = sum(results)
    total = len(results)

    print("=" * 70)
    print(f"RESULT: {passed}/{total} PASS")
    print("=" * 70)

    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
