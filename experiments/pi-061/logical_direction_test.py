from __future__ import annotations

from dataclasses import dataclass

from canonical_claim import match_known_fact


@dataclass(frozen=True)
class LogicalDirectionCase:
    case_id: str
    claim: str
    expected_fact_id: str | None
    direction: str


LOGICAL_DIRECTION_CASES = [
    LogicalDirectionCase(
        case_id="LD-01",
        claim="電子資料サービスを利用するには図書館カードが必要です。",
        expected_fact_id="library_card_required",
        direction="necessary",
    ),
    LogicalDirectionCase(
        case_id="LD-02",
        claim="図書館カードがなければ電子資料サービスを利用できません。",
        expected_fact_id="library_card_required",
        direction="necessary",
    ),
    LogicalDirectionCase(
        case_id="LD-03",
        claim="電子資料サービスを利用できるなら、図書館カードを持っています。",
        expected_fact_id="library_card_required",
        direction="necessary",
    ),
    LogicalDirectionCase(
        case_id="LD-04",
        claim="電子資料サービスを利用できる人は図書館カードを持っています。",
        expected_fact_id="library_card_required",
        direction="necessary",
    ),
    LogicalDirectionCase(
        case_id="LD-05",
        claim="図書館カードがあれば電子資料サービスを利用できます。",
        expected_fact_id=None,
        direction="sufficient",
    ),
    LogicalDirectionCase(
        case_id="LD-06",
        claim="図書館カードを持っているなら、電子資料サービスを利用できます。",
        expected_fact_id=None,
        direction="sufficient",
    ),
    LogicalDirectionCase(
        case_id="LD-07",
        claim="図書館カードを持っている人は電子資料サービスを利用できます。",
        expected_fact_id=None,
        direction="sufficient",
    ),
    LogicalDirectionCase(
        case_id="LD-08",
        claim="図書館カードがあれば、必ず電子資料サービスを利用できます。",
        expected_fact_id=None,
        direction="sufficient",
    ),
    LogicalDirectionCase(
        case_id="LD-09",
        claim="図書館カードがなくても電子資料サービスを利用できます。",
        expected_fact_id=None,
        direction="contrary",
    ),
    LogicalDirectionCase(
        case_id="LD-10",
        claim="電子資料サービスを利用するための条件の一つが図書館カードを持つことです。",
        expected_fact_id="library_card_required",
        direction="necessary",
    ),
]


def main() -> None:
    print("=" * 70)
    print("PI-061-14: Logical Direction Test")
    print("=" * 70)

    failures = 0

    for case in LOGICAL_DIRECTION_CASES:
        result = match_known_fact(case.claim)
        actual_fact_id = result.fact_id

        passed = actual_fact_id == case.expected_fact_id

        if not passed:
            failures += 1

        print()
        print(f"{case.case_id}")
        print(f"Direction: {case.direction}")
        print(f"Claim: {case.claim}")
        print(f"Expected Fact ID: {case.expected_fact_id}")
        print(f"Actual Fact ID: {actual_fact_id}")
        print(f"Result: {'PASS' if passed else 'FAIL'}")

    print()
    print("=" * 70)
    print(
        f"Result: {len(LOGICAL_DIRECTION_CASES) - failures}/"
        f"{len(LOGICAL_DIRECTION_CASES)} PASS"
    )
    print("=" * 70)

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

