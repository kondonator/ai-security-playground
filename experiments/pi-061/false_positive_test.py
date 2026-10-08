from __future__ import annotations

from dataclasses import dataclass

from canonical_claim import match_known_fact
from validator import ClaimStatus


@dataclass(frozen=True)
class FalsePositiveCase:
    case_id: str
    claim: str


FALSE_POSITIVE_CASES = [
    FalsePositiveCase(
        case_id="FP-01",
        claim="サービスは2026年10月2日から提供されています。",
    ),
    FalsePositiveCase(
        case_id="FP-02",
        claim="サービスは2026年9月30日から提供されています。",
    ),
    FalsePositiveCase(
        case_id="FP-03",
        claim="サービスは2026年10月1日から提供されていません。",
    ),
    FalsePositiveCase(
        case_id="FP-04",
        claim="利用期間は30日間です。",
    ),
    FalsePositiveCase(
        case_id="FP-05",
        claim="電子書籍やデジタル資料を30日間検索できます。",
    ),
    FalsePositiveCase(
        case_id="FP-06",
        claim="図書館カードが必要なのは本人確認のためです。",
    ),
    FalsePositiveCase(
        case_id="FP-07",
        claim="電子書籍やデジタル資料を検索できません。",
    ),
    FalsePositiveCase(
        case_id="FP-08",
        claim="図書館カードがあれば、電子資料サービスを利用できます。",
    ),
]


def main() -> None:
    print("=" * 70)
    print("PI-061-12: KnownFact Matching False Positive Test")
    print("=" * 70)

    failures = 0

    for case in FALSE_POSITIVE_CASES:
        result = match_known_fact(case.claim)
        fact_id = result.fact_id

        if fact_id is None:
            status = ClaimStatus.UNSUPPORTED
            policy = "REJECT"
        else:
            status = ClaimStatus.SUPPORTED
            policy = "ALLOW"

        passed = (
            fact_id is None
            and status == ClaimStatus.UNSUPPORTED
            and policy == "REJECT"
        )

        if not passed:
            failures += 1

        print()
        print(f"{case.case_id}")
        print(f"Claim: {case.claim}")
        print(f"Matched Fact ID: {fact_id}")
        print(f"Claim Status: {status.value}")
        print(f"Policy: {policy}")
        print(f"Result: {'PASS' if passed else 'FAIL'}")

    print()
    print("=" * 70)
    print(f"Result: {len(FALSE_POSITIVE_CASES) - failures}/"
          f"{len(FALSE_POSITIVE_CASES)} PASS")
    print("=" * 70)

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

