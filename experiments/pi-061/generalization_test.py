from __future__ import annotations

from dataclasses import dataclass

from canonical_claim import match_known_fact


@dataclass(frozen=True)
class GeneralizationCase:
    case_id: str
    claim: str
    expected_fact_id: str | None
    direction: str


GENERALIZATION_CASES = [
    GeneralizationCase(
        case_id="GEN-01",
        claim="電子資料サービスを利用できるなら、図書館カードを所持しているはずです。",
        expected_fact_id="library_card_required",
        direction="necessary",
    ),
    GeneralizationCase(
        case_id="GEN-02",
        claim="電子資料サービスを利用できる人は、図書館カードを所持しています。",
        expected_fact_id="library_card_required",
        direction="necessary",
    ),
    GeneralizationCase(
        case_id="GEN-03",
        claim="図書館カードを所持していない人は、電子資料サービスを利用できません。",
        expected_fact_id="library_card_required",
        direction="necessary",
    ),
    GeneralizationCase(
        case_id="GEN-04",
        claim="図書館カードの所持は、電子資料サービスを利用するための前提です。",
        expected_fact_id="library_card_required",
        direction="necessary",
    ),
    GeneralizationCase(
        case_id="GEN-05",
        claim="図書館カードを所持していれば、電子資料サービスの利用資格があります。",
        expected_fact_id=None,
        direction="sufficient",
    ),
    GeneralizationCase(
        case_id="GEN-06",
        claim="図書館カードを持つ人なら、電子資料サービスを利用できます。",
        expected_fact_id=None,
        direction="sufficient",
    ),
    GeneralizationCase(
        case_id="GEN-07",
        claim="電子資料サービスを利用するには、図書館カードがあれば十分です。",
        expected_fact_id=None,
        direction="sufficient",
    ),
    GeneralizationCase(
        case_id="GEN-08",
        claim="図書館カードの所持だけで、電子資料サービスを利用できます。",
        expected_fact_id=None,
        direction="sufficient",
    ),
    GeneralizationCase(
        case_id="GEN-09",
        claim="図書館カードを持っていなくても、電子資料サービスを利用できます。",
        expected_fact_id=None,
        direction="contrary",
    ),
    GeneralizationCase(
        case_id="GEN-10",
        claim="電子資料サービスの利用者は、図書館カードを所持している必要があります。",
        expected_fact_id="library_card_required",
        direction="necessary",
    ),
]


def main() -> None:
    print("=" * 70)
    print("PI-061-16: Generalization Test")
    print("=" * 70)

    failures = 0

    for case in GENERALIZATION_CASES:
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
        f"Result: {len(GENERALIZATION_CASES) - failures}/"
        f"{len(GENERALIZATION_CASES)} PASS"
    )
    print("=" * 70)

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

