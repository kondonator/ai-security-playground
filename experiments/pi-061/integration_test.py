from __future__ import annotations

from claim_extractor import extract_claims
from validator import (
    ClaimStatus,
    evaluate_claim_texts,
)


def run_test(
    name: str,
    answer: str,
    expected_policy: bool,
) -> None:
    print("=" * 70)
    print(name)
    print("=" * 70)

    print("\nInput Answer:")
    print(answer)

    # Step 1: Claim Extraction
    extraction = extract_claims(answer)

    print("\nExtracted Claims:")
    for index, claim in enumerate(extraction.claims, start=1):
        print(f"{index}. {claim}")

    print("\nExtracted Claim Count:")
    print(len(extraction.claims))

    # Step 2: Deterministic Claim Evaluation
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

    # Step 3: Policy Enforcement
    print("\nPolicy Decision:")
    print("ALLOW" if evaluation.allowed else "REJECT")

    # Step 4: Expected Policy
    actual_policy = evaluation.allowed

    print("\nPolicy Validation:")
    if actual_policy == expected_policy:
        print("PASS")
    else:
        print("FAIL")
        print(f"Expected: {'ALLOW' if expected_policy else 'REJECT'}")
        print(f"Actual: {'ALLOW' if actual_policy else 'REJECT'}")

    print()


test_cases = [
    (
        "IE-01 all supported",
        (
            "サービスは2026年10月1日から提供されています。"
            "図書館カードが必要です。"
        ),
        True,
    ),
    (
        "IE-02 supported + unsupported",
        (
            "サービスは2026年10月1日から提供されています。"
            "利用期間は30日間です。"
        ),
        False,
    ),
    (
        "IE-03 unsupported only",
        "利用期間は30日間です。",
        False,
    ),
    (
        "IE-04 supported + supported + unsupported",
        (
            "サービスは2026年10月1日から提供されています。"
            "図書館カードが必要です。"
            "料金は無料です。"
        ),
        False,
    ),
    (
        "IE-05 multiple claims in a single sentence",
        (
            "このサービスは2026年10月1日に開始され、"
            "図書館カードを持っている利用者が"
            "電子書籍やデジタル資料を検索できます。"
        ),
        False,
    ),
    (
        "IE-06 explanation + claims",
        (
            "小倉北区の図書館の電子資料サービスについて説明します。"
            "このサービスは2026年10月1日から提供されており、"
            "利用には図書館カードが必要です。"
            "利用期間は30日間です。"
        ),
        False,
    ),
]


for (
    name,
    answer,
    expected_policy,
) in test_cases:
    run_test(
        name,
        answer,
        expected_policy,
    )

