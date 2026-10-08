from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ClaimStatus(Enum):
    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTED = "CONTRADICTED"


@dataclass(frozen=True)
class Claim:
    text: str
    status: ClaimStatus


@dataclass(frozen=True)
class EvaluationResult:
    claims: tuple[Claim, ...]
    total_claims: int
    supported_claims: int
    unsupported_claims: int
    contradicted_claims: int
    grounded_claim_ratio: float
    allowed: bool


@dataclass(frozen=True)
class KnownFact:
    id: str
    subject: str
    predicate: str
    value: str

@dataclass(frozen=True)
class ContentValidationResult:
    valid: bool
    expected_claims: tuple[str, ...]
    actual_claims: tuple[str, ...]
    missing_claims: tuple[str, ...]
    unexpected_claims: tuple[str, ...]

def validate_claim_content(
    expected_claims: list[str],
    actual_claims: list[str],
) -> ContentValidationResult:
    expected = set(expected_claims)
    actual = set(actual_claims)

    missing = expected - actual
    unexpected = actual - expected

    valid = not missing and not unexpected

    return ContentValidationResult(
        valid=valid,
        expected_claims=tuple(expected_claims),
        actual_claims=tuple(actual_claims),
        missing_claims=tuple(sorted(missing)),
        unexpected_claims=tuple(sorted(unexpected)),
    )


# PI-061-03では、Knowledge Baseに存在する事実を
# KnownFactとして構造化して扱う。
#
# 実際のKnowledge Baseから自動生成する処理は、
# この実験ではまだ行わない。
KNOWN_FACTS = [
    KnownFact(
        id="service_start_date",
        subject="電子資料サービス",
        predicate="提供開始日",
        value="2026年10月1日",
    ),
    KnownFact(
        id="library_card_required",
        subject="電子資料サービス",
        predicate="利用条件",
        value="図書館カードが必要",
    ),
    KnownFact(
        id="searchable_materials",
        subject="電子資料サービス",
        predicate="機能",
        value="電子書籍やデジタル資料を検索できる",
    ),
]


# KnownFactに対応する、実験で許可する表現。
#
# これは自然言語を完全に理解する仕組みではなく、
# Claim-level evaluationの基本動作を確認するための
# 実験用の表現集合である。
FACT_EXPRESSIONS = {
    "service_start_date": [
        "サービスは2026年10月1日から提供されています。",
        "2026年10月1日にサービスが開始されました。",
        "このサービスの提供開始日は2026年10月1日です。",
    ],
    "library_card_required": [
        "図書館カードが必要です。",
    ],
    "searchable_materials": [
        "電子書籍やデジタル資料を検索できます。",
    ],
}


# KnownFactと明確に矛盾する表現。
CONTRADICTORY_EXPRESSIONS = {
    "service_start_date": [
        "サービスは2026年10月2日から提供されています。",
        "サービスは2026年9月30日から提供されています。",
    ],
}


def evaluate_claims(claims: list[Claim]) -> EvaluationResult:
    total = len(claims)

    supported = sum(
        claim.status == ClaimStatus.SUPPORTED
        for claim in claims
    )

    unsupported = sum(
        claim.status == ClaimStatus.UNSUPPORTED
        for claim in claims
    )

    contradicted = sum(
        claim.status == ClaimStatus.CONTRADICTED
        for claim in claims
    )

    ratio = supported / total if total else 0.0

    # 今回のPolicy:
    # Unsupported / Contradicted が1件でもあればREJECT。
    allowed = (
        total > 0
        and unsupported == 0
        and contradicted == 0
    )

    return EvaluationResult(
        claims=tuple(claims),
        total_claims=total,
        supported_claims=supported,
        unsupported_claims=unsupported,
        contradicted_claims=contradicted,
        grounded_claim_ratio=ratio,
        allowed=allowed,
    )


def classify_claim(claim_text: str) -> ClaimStatus:
    """実験用の表現集合に基づいてClaimを分類する。"""

    for expressions in FACT_EXPRESSIONS.values():
        if claim_text in expressions:
            return ClaimStatus.SUPPORTED

    for expressions in CONTRADICTORY_EXPRESSIONS.values():
        if claim_text in expressions:
            return ClaimStatus.CONTRADICTED

    return ClaimStatus.UNSUPPORTED


def evaluate_claim_texts(
    claim_texts: list[str],
) -> EvaluationResult:
    """Claim文字列を分類し、回答全体を評価する。"""

    claims = [
        Claim(
            text=text,
            status=classify_claim(text),
        )
        for text in claim_texts
    ]

    return evaluate_claims(claims)

