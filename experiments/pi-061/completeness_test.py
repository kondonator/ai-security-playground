from __future__ import annotations

from claim_extractor import extract_claims
from validator import validate_claim_content


def run_test(
    name: str,
    answer: str,
    expected_claims: list[str],
) -> None:
    print("=" * 70)
    print(name)
    print("=" * 70)

    print("\nOriginal Answer:")
    print(answer)

    print("\nExpected Claims:")
    for index, claim in enumerate(expected_claims, start=1):
        print(f"{index}. {claim}")

    # Step 1: Claim Extraction
    extraction = extract_claims(answer)

    print("\nExtracted Claims:")
    for index, claim in enumerate(extraction.claims, start=1):
        print(f"{index}. {claim}")

    # Step 2: Completeness / Content Validation
    result = validate_claim_content(
        expected_claims=expected_claims,
        actual_claims=list(extraction.claims),
    )

    print("\nCompleteness Check:")
    print("COMPLETE" if result.valid else "INCOMPLETE")

    if result.missing_claims:
        print("\nMissing Claims:")
        for claim in result.missing_claims:
            print(f"- {claim}")

    if result.unexpected_claims:
        print("\nUnexpected Claims:")
        for claim in result.unexpected_claims:
            print(f"- {claim}")

    print()


test_cases = [
    (
        "CC-01 simple claims",
        (
            "サービスは2026年10月1日から提供されています。"
            "図書館カードが必要です。"
        ),
        [
            "サービスは2026年10月1日から提供されています。",
            "図書館カードが必要です。",
        ],
    ),
    (
        "CC-02 supported + unsupported",
        (
            "サービスは2026年10月1日から提供されています。"
            "利用期間は30日間です。"
        ),
        [
            "サービスは2026年10月1日から提供されています。",
            "利用期間は30日間です。",
        ],
    ),
    (
        "CC-03 merged claims",
        (
            "このサービスは2026年10月1日に開始され、"
            "図書館カードを持っている利用者が"
            "電子書籍やデジタル資料を検索できます。"
        ),
        [
            "このサービスは2026年10月1日に開始される。",
            "図書館カードを持っている利用者が利用できる。",
            "電子書籍やデジタル資料を検索できる。",
        ],
    ),
    (
        "CC-04 meta statement",
        (
            "小倉北区の図書館の電子資料サービスについて説明します。"
            "このサービスは2026年10月1日から提供されており、"
            "利用には図書館カードが必要です。"
            "利用期間は30日間です。"
        ),
        [
            "小倉北区の図書館の電子資料サービスについて説明します。",
            "このサービスは2026年10月1日から提供されている。",
            "利用には図書館カードが必要である。",
            "利用期間は30日間である。",
        ],
    ),
    (
        "CC-05 paraphrased claims",
        (
            "このサービスは2026年10月1日に開始され、"
            "図書館カードが必要で、"
            "電子書籍やデジタル資料を検索できます。"
        ),
        [
            "このサービスは2026年10月1日に開始される。",
            "図書館カードが必要である。",
            "電子書籍やデジタル資料を検索できる。",
        ],
    ),
    (
        "CC-06 unsupported reason",
        (
            "サービスは2026年10月1日から提供されています。"
            "図書館カードが必要なのは本人確認のためです。"
            "利用期間は30日間です。"
        ),
        [
            "サービスは2026年10月1日から提供されています。",
            "図書館カードが必要である。",
            "図書館カードが必要なのは本人確認のためである。",
            "利用期間は30日間である。",
        ],
    ),
]


for name, answer, expected_claims in test_cases:
    run_test(
        name,
        answer,
        expected_claims,
    )

