from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gpt-oss:20b"


SYSTEM_PROMPT = """\
あなたはClaimをCanonical Claimに正規化するアシスタントです。

入力されたClaimの意味を変えずに、表現を正規化してください。

ルール:
- Claimの意味を変更しないでください。
- 新しい情報を追加しないでください。
- 入力されていない情報を推測しないでください。
- 同じ意味のClaimは、同じCanonical Claimになるようにしてください。
- 日付、数量、条件、理由などの重要な情報を保持してください。
- 条件付きClaimは条件を失わないでください。
- 理由を含むClaimは理由を失わないでください。
- Claimを複数のClaimに分割しないでください。
- 1つの入力Claimに対して、1つのCanonical Claimを返してください。
- 説明は追加しないでください。

必ず以下のJSON形式で回答してください。

{
  "canonical_claim": "Canonical Claim"
}
"""


@dataclass(frozen=True)
class NormalizationResult:
    original_claim: str
    canonical_claim: str
    raw_response: str


def normalize_claim(
    claim: str,
) -> NormalizationResult:
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": claim,
            },
        ],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0,
        },
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request) as response:
        raw_response = response.read().decode("utf-8")

    response_data = json.loads(raw_response)

    content = response_data["message"]["content"]
    result = json.loads(content)

    canonical_claim = result["canonical_claim"]

    return NormalizationResult(
        original_claim=claim,
        canonical_claim=canonical_claim,
        raw_response=raw_response,
    )


def run_test(
    name: str,
    claims: list[str],
) -> None:
    print("=" * 70)
    print(name)
    print("=" * 70)

    for index, claim in enumerate(claims, start=1):
        result = normalize_claim(claim)

        print(f"\nClaim {index}:")
        print(f"Original:   {result.original_claim}")
        print(f"Canonical:  {result.canonical_claim}")


test_cases = [
    (
        "CN-01 same fact, different endings",
        [
            "サービスは2026年10月1日から提供されています。",
            "サービスは2026年10月1日から提供されている。",
            "サービスは2026年10月1日から開始されました。",
        ],
    ),
    (
        "CN-02 same fact, different wording",
        [
            "図書館カードが必要です。",
            "利用には図書館カードが必要です。",
            "このサービスを利用するには図書館カードが必要です。",
        ],
    ),
    (
        "CN-03 same search capability",
        [
            "電子書籍やデジタル資料を検索できます。",
            "電子書籍やデジタル資料を検索できる。",
            "利用者は電子書籍やデジタル資料を検索できます。",
        ],
    ),
    (
        "CN-04 different facts",
        [
            "サービスは2026年10月1日から提供されています。",
            "サービスは2026年10月2日から提供されています。",
        ],
    ),
    (
        "CN-05 quantity must be preserved",
        [
            "利用期間は30日間です。",
            "利用期間は7日間です。",
        ],
    ),
    (
        "CN-06 condition must be preserved",
        [
            "図書館カードがあれば、電子書籍やデジタル資料を検索できます。",
            "電子書籍やデジタル資料を検索できます。",
        ],
    ),
    (
        "CN-07 reason must be preserved",
        [
            "図書館カードが必要なのは本人確認のためです。",
            "図書館カードが必要です。",
        ],
    ),
    (
        "CN-08 unsupported inference must not disappear",
        [
            "サービスは2026年10月1日から提供されているため、電子資料は30日間利用できます。",
        ],
    ),
]


for name, claims in test_cases:
    run_test(
        name,
        claims,
    )

