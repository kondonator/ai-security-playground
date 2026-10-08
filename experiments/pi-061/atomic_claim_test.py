from __future__ import annotations

from claim_extractor import extract_claims
from validator import evaluate_claim_texts


def run_test(
    name: str,
    answer: str,
) -> None:
    print("=" * 70)
    print(name)
    print("=" * 70)

    print("\nOriginal Answer:")
    print(answer)

    # Step 1: Claim Extraction
    extraction = extract_claims(answer)

    print("\nExtracted Claims:")
    for index, claim in enumerate(extraction.claims, start=1):
        print(f"{index}. {claim}")

    # Step 2: Current Claim-level Evaluation
    evaluation = evaluate_claim_texts(
        list(extraction.claims)
    )

    print("\nClaim Evaluation:")

    for claim in evaluation.claims:
        print(f"- {claim.status.value}: {claim.text}")

    print("\nEvaluation Summary:")
    print(f"Total Claims: {evaluation.total_claims}")
    print(f"Supported Claims: {evaluation.supported_claims}")
    print(f"Unsupported Claims: {evaluation.unsupported_claims}")
    print(f"Contradicted Claims: {evaluation.contradicted_claims}")
    print(
        "Grounded Claim Ratio: "
        f"{evaluation.grounded_claim_ratio:.1%}"
    )

    print("\nPolicy Decision:")
    print("ALLOW" if evaluation.allowed else "REJECT")

    print()


test_cases = [
    (
        "AC-01 supported facts + unsupported claim",
        (
            "サービスは2026年10月1日から提供されており、"
            "図書館カードが必要で、"
            "利用期間は30日間です。"
        ),
    ),
    (
        "AC-02 supported fact + unsupported inference",
        (
            "サービスは2026年10月1日から提供されているため、"
            "電子資料は30日間利用できるサービスです。"
        ),
    ),
    (
        "AC-03 supported facts + unsupported reason",
        (
            "図書館カードが必要なのは本人確認のためであり、"
            "サービスは2026年10月1日から提供されています。"
        ),
    ),
    (
        "AC-04 supported fact + unsupported consequence",
        (
            "電子書籍やデジタル資料を検索できるため、"
            "利用者はすべての資料を30日間借りることができます。"
        ),
    ),
    (
        "AC-05 heavily mixed claim",
        (
            "2026年10月1日から提供され、"
            "図書館カードが必要で、"
            "電子書籍やデジタル資料を検索できるため、"
            "利用期間は30日間となっています。"
        ),
    ),
    (
        "AC-06 unsupported claim embedded in explanation",
        (
            "小倉北区の図書館の電子資料サービスは、"
            "2026年10月1日から提供されており、"
            "図書館カードが必要です。"
            "そのため、登録した利用者は30日間電子書籍を利用できます。"
        ),
    ),
]


for name, answer in test_cases:
    run_test(
        name,
        answer,
    )

