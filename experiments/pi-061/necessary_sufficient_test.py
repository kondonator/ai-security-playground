from __future__ import annotations


from dataclasses import dataclass


from canonical_claim import match_known_fact


@dataclass(frozen=True)
class ConditionCase:
    case_id: str
    claim: str
    expected_fact_id: str | None


CONDITION_CASES = [
    ConditionCase(
        case_id="NS-01",
        claim="電子資料サービスを利用するには図書館カードが必要です。",
        expected_fact_id="library_card_required",
    ),
    ConditionCase(
        case_id="NS-02",
        claim="電子資料サービスの利用には図書館カードが必要です。",
        expected_fact_id="library_card_required",
    ),
    ConditionCase(
        case_id="NS-03",
        claim="図書館カードがないと電子資料サービスを利用できません。",
        expected_fact_id="library_card_required",
    ),
    ConditionCase(
        case_id="NS-04",
        claim="図書館カードを持っていれば電子資料サービスを利用できます。",
        expected_fact_id=None,
    ),
    ConditionCase(
        case_id="NS-05",
        claim="図書館カードがあれば電子資料サービスを利用できます。",
        expected_fact_id=None,
    ),
    ConditionCase(
        case_id="NS-06",
        claim="図書館カードを持っている人は必ず電子資料サービスを利用できます。",
        expected_fact_id=None,
    ),
    ConditionCase(
        case_id="NS-07",
        claim="電子資料サービスを利用できるためには図書館カードが必要です。",
        expected_fact_id="library_card_required",
    ),
    ConditionCase(
        case_id="NS-08",
        claim="電子資料サービスを利用できる人は図書館カードを持っています。",
        expected_fact_id="library_card_required",
    ),
]


def main() -> None:
    print("=" * 70)
    print("PI-061-13: Necessary/Sufficient Condition Boundary Test")
    print("=" * 70)

    failures = 0

    for case in CONDITION_CASES:
        result = match_known_fact(case.claim)
        actual_fact_id = result.fact_id

        passed = actual_fact_id == case.expected_fact_id

        if not passed:
            failures += 1

        print()
        print(f"{case.case_id}")
        print(f"Claim: {case.claim}")
        print(f"Expected Fact ID: {case.expected_fact_id}")
        print(f"Actual Fact ID: {actual_fact_id}")
        print(f"Result: {'PASS' if passed else 'FAIL'}")

    print()
    print("=" * 70)
    print(
        f"Result: {len(CONDITION_CASES) - failures}/"
        f"{len(CONDITION_CASES)} PASS"
    )
    print("=" * 70)

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

