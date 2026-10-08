from __future__ import annotations

from canonical_claim import match_known_fact
from claim_extractor import extract_claims
from validator import (
    Claim,
    ClaimStatus,
    evaluate_claims,
)


def evaluate_answer(answer: str) -> None:
    print("\nOriginal Answer:")
    print(answer)

    extraction = extract_claims(answer)

    print("\nExtracted Claims:")

    claims: list[Claim] = []

    for index, claim_text in enumerate(
        extraction.claims,
        start=1,
    ):
        print(f"{index}. {claim_text}")

        result = match_known_fact(claim_text)

        if result.fact_id is not None:
            status = ClaimStatus.SUPPORTED
            fact = result.fact_id
        else:
            status = ClaimStatus.UNSUPPORTED
            fact = "None"

        print(f"   Fact ID: {fact}")
        print(f"   Status: {status.value}")

        claims.append(
            Claim(
                text=claim_text,
                status=status,
            )
        )

    evaluation = evaluate_claims(claims)

    print("\nEvaluation Summary:")
    print(f"Total Claims: {evaluation.total_claims}")
    print(
        f"Supported Claims: "
        f"{evaluation.supported_claims}"
    )
    print(
        f"Unsupported Claims: "
        f"{evaluation.unsupported_claims}"
    )
    print(
        f"Contradicted Claims: "
        f"{evaluation.contradicted_claims}"
    )
    print(
        "Grounded Claim Ratio: "
        f"{evaluation.grounded_claim_ratio:.1%}"
    )

    print("\nPolicy Decision:")
    print(
        "ALLOW"
        if evaluation.allowed
        else "REJECT"
    )


TEST_CASES = [
    (
        "EN-01 supported claim - original wording",
        (
            "サービスは2026年10月1日から提供されています。"
        ),
    ),
    (
        "EN-02 supported claim - paraphrase",
        (
            "サービスは2026年10月1日から提供されている。"
        ),
    ),
    (
        "EN-03 supported claim - another paraphrase",
        (
            "2026年10月1日にサービスが開始されました。"
        ),
    ),
    (
        "EN-04 supported + unsupported",
        (
            "サービスは2026年10月1日から提供されており、"
            "利用期間は30日間です。"
        ),
    ),
    (
        "EN-05 unsupported only",
        (
            "利用期間は30日間です。"
        ),
    ),
    (
        "EN-06 multiple supported claims",
        (
            "サービスは2026年10月1日から提供されており、"
            "図書館カードが必要で、"
            "電子書籍やデジタル資料を検索できます。"
        ),
    ),
    (
        "EN-07 supported + unsupported reason",
        (
            "図書館カードが必要なのは本人確認のためです。"
        ),
    ),
    (
        "EN-08 supported + unsupported consequence",
        (
            "電子書籍やデジタル資料を検索できるため、"
            "利用者はすべての資料を30日間借りることができます。"
        ),
    ),
]


for name, answer in TEST_CASES:
    print("=" * 70)
    print(name)
    print("=" * 70)

    evaluate_answer(answer)
    print()

