from __future__ import annotations

from claim_extractor import extract_claims


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

    print("\nExpected Atomic Claims:")
    for index, claim in enumerate(expected_claims, start=1):
        print(f"{index}. {claim}")

    extraction = extract_claims(answer)

    print("\nExtracted Claims:")
    for index, claim in enumerate(extraction.claims, start=1):
        print(f"{index}. {claim}")

    actual = list(extraction.claims)

    expected_set = set(expected_claims)
    actual_set = set(actual)

    missing = expected_set - actual_set
    unexpected = actual_set - expected_set

    print("\nAtomicity Evaluation:")

    if not missing and not unexpected:
        print("PASS")
    else:
        print("FAIL")

        if missing:
            print("\nMissing Claims:")
            for claim in sorted(missing):
                print(f"- {claim}")

        if unexpected:
            print("\nUnexpected Claims:")
            for claim in sorted(unexpected):
                print(f"- {claim}")

    print()


test_cases = [
    (
        "AT-01 single atomic fact",
        "サービスは2026年10月1日から提供されています。",
        [
            "サービスは2026年10月1日から提供されています。",
        ],
    ),
    (
        "AT-02 two independent facts",
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
        "AT-03 fact and reason",
        "図書館カードが必要なのは本人確認のためです。",
        [
            "図書館カードが必要である。",
            "図書館カードが必要な理由は本人確認である。",
        ],
    ),
    (
        "AT-04 fact and consequence",
        (
            "電子書籍やデジタル資料を検索できるため、"
            "利用期間は30日間です。"
        ),
        [
            "電子書籍やデジタル資料を検索できる。",
            "利用期間は30日間である。",
        ],
    ),
    (
        "AT-05 three independent facts",
        (
            "サービスは2026年10月1日から提供され、"
            "図書館カードが必要で、"
            "電子書籍やデジタル資料を検索できます。"
        ),
        [
            "サービスは2026年10月1日から提供される。",
            "図書館カードが必要である。",
            "電子書籍やデジタル資料を検索できる。",
        ],
    ),
    (
        "AT-06 fact plus unsupported reason",
        (
            "サービスは2026年10月1日から提供されており、"
            "図書館カードが必要なのは本人確認のためです。"
        ),
        [
            "サービスは2026年10月1日から提供されている。",
            "図書館カードが必要である。",
            "図書館カードが必要な理由は本人確認である。",
        ],
    ),
    (
        "AT-07 fact plus condition",
        (
            "図書館カードがあれば、"
            "電子書籍やデジタル資料を検索できます。"
        ),
        [
            "図書館カードがあれば利用できる。",
            "電子書籍やデジタル資料を検索できる。",
        ],
    ),
    (
        "AT-08 fact plus unsupported inference",
        (
            "サービスは2026年10月1日から提供されているため、"
            "電子資料は30日間利用できます。"
        ),
        [
            "サービスは2026年10月1日から提供されている。",
            "電子資料は30日間利用できる。",
        ],
    ),
    (
        "AT-09 multiple facts with reason and consequence",
        (
            "図書館カードが必要なのは本人確認のためであり、"
            "電子書籍やデジタル資料を検索できるため、"
            "利用期間は30日間です。"
        ),
        [
            "図書館カードが必要である。",
            "図書館カードが必要な理由は本人確認である。",
            "電子書籍やデジタル資料を検索できる。",
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

