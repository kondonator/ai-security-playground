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

    # Step 2: Deterministic Evaluation
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
        "BP-01 simple unsupported addition",
        (
            "サービスは2026年10月1日から提供されています。"
            "利用期間は30日間です。"
        ),
    ),
    (
        "BP-02 supported facts + unsupported subordinate clause",
        (
            "サービスは2026年10月1日から提供されており、"
            "図書館カードが必要で、"
            "利用期間は30日間です。"
        ),
    ),
    (
        "BP-03 supported facts + unsupported reason",
        (
            "サービスは2026年10月1日から提供されています。"
            "図書館カードが必要なのは、"
            "本人確認のためであり、利用期間は30日間です。"
        ),
    ),
    (
        "BP-04 supported facts + unsupported parenthetical",
        (
            "サービスは2026年10月1日から提供されています。"
            "図書館カードが必要です"
            "（利用期間は30日間です）。"
        ),
    ),
    (
        "BP-05 supported facts + unsupported relative clause",
        (
            "2026年10月1日から提供されているサービスで、"
            "図書館カードを持つ利用者は利用期間30日間で"
            "電子書籍やデジタル資料を検索できます。"
        ),
    ),
]
    

for name, answer in test_cases:
    run_test(
        name,
        answer,
    )

