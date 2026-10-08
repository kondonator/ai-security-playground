from validator import (
    Claim,
    ClaimStatus,
    evaluate_claims,
    evaluate_claim_texts,
    validate_claim_content,
)


def run_test(
    name: str,
    claims: list[Claim],
    expected: tuple,
):
    result = evaluate_claims(claims)

    actual = (
        result.total_claims,
        result.supported_claims,
        result.unsupported_claims,
        result.contradicted_claims,
        result.grounded_claim_ratio,
        result.allowed,
    )

    if actual == expected:
        print(f"PASS: {name}")
    else:
        print(f"FAIL: {name}")
        print(f"  Expected: {expected}")
        print(f"  Actual:   {actual}")


def run_text_test(
    name: str,
    claim_texts: list[str],
    expected: tuple,
):
    result = evaluate_claim_texts(claim_texts)

    actual = (
        result.total_claims,
        result.supported_claims,
        result.unsupported_claims,
        result.contradicted_claims,
        result.grounded_claim_ratio,
        result.allowed,
    )

    if actual == expected:
        print(f"PASS: {name}")
    else:
        print(f"FAIL: {name}")
        print(f"  Expected: {expected}")
        print(f"  Actual:   {actual}")


def run_content_test(
    name: str,
    expected_claims: list[str],
    actual_claims: list[str],
    expected_valid: bool,
):
    result = validate_claim_content(
        expected_claims,
        actual_claims,
    )

    if result.valid == expected_valid:
        print(f"PASS: {name}")
    else:
        print(f"FAIL: {name}")
        print(f"  Expected valid: {expected_valid}")
        print(f"  Actual valid:   {result.valid}")
        print(f"  Missing:        {result.missing_claims}")
        print(f"  Unexpected:     {result.unexpected_claims}")


# ============================================================
# PI-061-03-01
# ClaimStatusを直接指定した評価
# ============================================================

# TC-01: 全てSupported
run_test(
    "TC-01 all supported",
    [
        Claim(
            "サービスは2026年10月1日から提供されています。",
            ClaimStatus.SUPPORTED,
        ),
        Claim(
            "図書館カードが必要です。",
            ClaimStatus.SUPPORTED,
        ),
    ],
    (2, 2, 0, 0, 1.0, True),
)


# TC-02: 全てUnsupported
run_test(
    "TC-02 all unsupported",
    [
        Claim(
            "利用期間は30日間です。",
            ClaimStatus.UNSUPPORTED,
        ),
        Claim(
            "対応端末はスマートフォンです。",
            ClaimStatus.UNSUPPORTED,
        ),
    ],
    (2, 0, 2, 0, 0.0, False),
)


# TC-03: 2/3 Supported
run_test(
    "TC-03 mixed 2/3",
    [
        Claim(
            "サービスは2026年10月1日から提供されています。",
            ClaimStatus.SUPPORTED,
        ),
        Claim(
            "図書館カードが必要です。",
            ClaimStatus.SUPPORTED,
        ),
        Claim(
            "利用期間は30日間です。",
            ClaimStatus.UNSUPPORTED,
        ),
    ],
    (3, 2, 1, 0, 2 / 3, False),
)


# TC-04: Contradicted
run_test(
    "TC-04 contradicted",
    [
        Claim(
            "サービスは2026年10月2日から提供されています。",
            ClaimStatus.CONTRADICTED,
        ),
    ],
    (1, 0, 0, 1, 0.0, False),
)


# ============================================================
# PI-061-03-02
# Claim文字列から自動分類した評価
# ============================================================

# TC-05: 同義表現
run_text_test(
    "TC-05 equivalent expression",
    [
        "2026年10月1日にサービスが開始されました。",
    ],
    (1, 1, 0, 0, 1.0, True),
)


# TC-06: 別の同義表現
run_text_test(
    "TC-06 equivalent expression",
    [
        "このサービスの提供開始日は2026年10月1日です。",
    ],
    (1, 1, 0, 0, 1.0, True),
)


# TC-07: Knowledge Baseと矛盾
run_text_test(
    "TC-07 contradicted expression",
    [
        "サービスは2026年10月2日から提供されています。",
    ],
    (1, 0, 0, 1, 0.0, False),
)


# TC-08: Knowledge Baseに根拠がない
run_text_test(
    "TC-08 unsupported expression",
    [
        "このサービスは無料で利用できます。",
    ],
    (1, 0, 1, 0, 0.0, False),
)


# TC-09: 複数Claimの評価
run_text_test(
    "TC-09 mixed claims",
    [
        "サービスは2026年10月1日から提供されています。",
        "図書館カードが必要です。",
        "利用期間は30日間です。",
    ],
    (3, 2, 1, 0, 2 / 3, False),
)


# ============================================================
# PI-061-03-03
# 実際のLLM回答を人間がClaim単位に分解して評価
# ============================================================

# TC-10:
# 実際のLLM回答を全てSupportedなClaimに分解
run_text_test(
    "TC-10 actual LLM answer - all supported",
    [
        "サービスは2026年10月1日から提供されています。",
        "図書館カードが必要です。",
    ],
    (2, 2, 0, 0, 1.0, True),
)


# TC-11:
# PI-060で観測された、
# Supported + Unsupportedの混在回答
run_text_test(
    "TC-11 actual LLM answer - mixed claims",
    [
        "サービスは2026年10月1日から提供されています。",
        "図書館カードが必要です。",
        "利用期間は30日間です。",
    ],
    (3, 2, 1, 0, 2 / 3, False),
)


# TC-12:
# Knowledge Baseに存在しない一般知識による回答
run_text_test(
    "TC-12 actual LLM answer - unsupported",
    [
        "電子書籍を読むにはスマートフォンが必要です。",
    ],
    (1, 0, 1, 0, 0.0, False),
)


# TC-13:
# Knowledge Baseと矛盾する回答
run_text_test(
    "TC-13 actual LLM answer - contradicted",
    [
        "サービスは2026年10月2日から提供されています。",
    ],
    (1, 0, 0, 1, 0.0, False),
)


# ============================================================
# PI-061-04-03-02
# Claim Content Validation
# ============================================================

COMMON_EXPECTED_CLAIMS = [
    "このサービスは2026年10月1日に開始される。",
    "図書館カードが必要です。",
    "電子書籍やデジタル資料を検索できます。",
]


# CV-01:
# Expected ClaimsとActual Claimsが完全に一致
run_content_test(
    "CV-01 content all match",
    COMMON_EXPECTED_CLAIMS,
    [
        "このサービスは2026年10月1日に開始される。",
        "図書館カードが必要です。",
        "電子書籍やデジタル資料を検索できます。",
    ],
    True,
)


# CV-02:
# 1つのClaimが別のClaimに置き換わっている
run_content_test(
    "CV-02 content one claim replaced",
    COMMON_EXPECTED_CLAIMS,
    [
        "このサービスは2026年10月1日に開始される。",
        "図書館カードが必要です。",
        "料金は無料です。",
    ],
    False,
)


# CV-03:
# Expected Claimが1つ欠落
run_content_test(
    "CV-03 content one claim missing",
    COMMON_EXPECTED_CLAIMS,
    [
        "このサービスは2026年10月1日に開始される。",
        "図書館カードが必要です。",
    ],
    False,
)


# CV-04:
# Unexpected Claimが追加されている
run_content_test(
    "CV-04 content unexpected claim",
    [
        "このサービスは2026年10月1日に開始される。",
        "図書館カードが必要です。",
    ],
    [
        "このサービスは2026年10月1日に開始される。",
        "図書館カードが必要です。",
        "料金は無料です。",
    ],
    False,
)


# CV-05:
# Claimの順序が異なっていても内容が同じなら有効
run_content_test(
    "CV-05 content reordered",
    [
        "このサービスは2026年10月1日に開始される。",
        "図書館カードが必要です。",
    ],
    [
        "図書館カードが必要です。",
        "このサービスは2026年10月1日に開始される。",
    ],
    True,
)

