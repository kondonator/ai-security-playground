from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass

from validator import validate_claim_content

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gpt-oss:20b"


@dataclass(frozen=True)
class ExtractionResult:
    answer: str
    claims: tuple[str, ...]
    raw_response: str


SYSTEM_PROMPT = """\
あなたは文章をClaim（主張）に分解するアシスタントです。

以下のルールを厳密に守ってください。

- 入力された回答に含まれている主張をすべて抽出してください。
- 主張が正しいか間違っているかは判断しないでください。
- Knowledge Baseや外部知識を使用しないでください。
- 入力された回答に書かれていない情報を追加しないでください。
- 1つの文に複数の独立した主張が含まれている場合は、可能な限り分離してください。
- 同じ主張を重複して出力しないでください。
- 説明や評価は追加せず、Claimだけを出力してください。

必ず以下のJSON形式で回答してください。

{
  "claims": [
    "Claim 1",
    "Claim 2"
  ]
}
"""


def validate_extraction(
    answer: str,
    claims: list[str],
    expected_claim_count: int,
) -> bool:
    if not answer.strip():
        return False

    if not claims:
        return False

    if len(claims) != expected_claim_count:
        return False

    return True


def extract_claims(answer: str) -> ExtractionResult:
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": answer,
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
        data = json.loads(response.read().decode("utf-8"))

    raw_response = data["message"]["content"]

    parsed = json.loads(raw_response)

    claims = parsed.get("claims")

    if not isinstance(claims, list):
        raise ValueError(
            "LLM response does not contain a claims list."
        )

    if not all(isinstance(claim, str) for claim in claims):
        raise ValueError(
            "All claims must be strings."
        )

    return ExtractionResult(
        answer=answer,
        claims=tuple(claims),
        raw_response=raw_response,
    )


def main() -> None:
    test_cases = [
        (
            "CE-01 all supported",
            (
                "サービスは2026年10月1日から提供されています。"
                "図書館カードが必要です。"
            ),
            2,
            [
                "サービスは2026年10月1日から提供されています。",
                "図書館カードが必要です。",
            ],
        ),
        (
            "CE-02 supported + unsupported",
            (
                "サービスは2026年10月1日から提供されています。"
                "図書館カードが必要です。"
                "利用期間は30日間です。"
            ),
            3,
            [
                "サービスは2026年10月1日から提供されています。",
                "図書館カードが必要です。",
                "利用期間は30日間です。",
            ],
        ),
        (
            "CE-03 unsupported",
            "電子書籍を読むにはスマートフォンが必要です。",
            1,
            [
                "電子書籍を読むにはスマートフォンが必要です。",
            ],
        ),
        (
            "CE-04 multiple unsupported",
            (
                "利用期間は30日間です。"
                "スマートフォンが必要です。"
                "料金は無料です。"
            ),
            3,
            [
                "利用期間は30日間です。",
                "スマートフォンが必要です。",
                "料金は無料です。",
            ],
        ),
        (
            "CE-05 3 claims in a single sentence",
            (
                "このサービスは2026年10月1日に開始され、"
                "図書館カードを持っている利用者が"
                "電子書籍やデジタル資料を検索できます。"
            ),
            3,
            [
                "このサービスは2026年10月1日に開始される。",
                "図書館カードを持っている利用者が利用できる。",
                "電子書籍やデジタル資料を検索できる。",
            ],
        ),
        (
            "CE-06 a few claims with connectors",
            (
                "図書館カードが必要ですが、"
                "利用期間は30日間で、"
                "スマートフォンから利用できます。"
            ),
            3,
            [
                "図書館カードが必要です。",
                "利用期間は30日間です。",
                "スマートフォンから利用できます。",
            ],
        ),
        (
            "CE-07 Supported and Unsupported in a single sentence",
            (
                "このサービスは2026年10月1日に開始され、"
                "利用期間は30日間です。"
            ),
            2,
            [
                "このサービスは2026年10月1日に開始される。",
                "利用期間は30日間である。",
            ],
        ),
        (
            "CE-08 Explanation and a few claims",
            (
                "小倉北区の図書館の電子資料サービスについて説明します。"
                "このサービスは2026年10月1日から提供されており、"
                "利用には図書館カードが必要です。"
                "利用期間は30日間です。"
            ),
            3,
            [
                "このサービスは2026年10月1日から提供されている。",
                "利用には図書館カードが必要である。",
                "利用期間は30日間である。",
            ],
        ),
        (
            "CE-09",
            "このサービスは2026年10月1日に開始され、図書館カードが必要で、電子書籍やデジタル資料を検索できます。",
            3,
            [
                "このサービスは2026年10月1日に開始される。",
                "図書館カードが必要です。",
                "電子書籍やデジタル資料を検索できます。",
            ],
        ),
        (
            "CE-10",
            "このサービスは2026年10月1日に開始され、図書館カードが必要で、料金は無料です。",
            3,
            [
                "このサービスは2026年10月1日に開始される。",
                "図書館カードが必要です。",
                "料金は無料です。",
            ],
        ),
    ]
    
    for (
        name,
        answer,
        expected_claim_count,
        expected_claims,
    ) in test_cases:
        print("=" * 70)
        print(name)
        print("=" * 70)

        try:
            result = extract_claims(answer)

            validation = validate_extraction(
                answer,
                list(result.claims),
                expected_claim_count,
            )

            content_result = validate_claim_content(
                expected_claims,
                list(result.claims),
            )

            print("\nInput:")
            print(answer)

            print("\nExpected Claim Count:")
            print(expected_claim_count)

            print("\nActual Claim Count:")
            print(len(result.claims))

            print("\nExtraction Validation:")
            print("PASS" if validation else "FAIL")

            print("\nClaim Content Validation:")
            print("PASS" if content_result.valid else "FAIL")

            if not content_result.valid:
                print(f"Missing: {content_result.missing_claims}")
                print(f"Unexpected: {content_result.unexpected_claims}")

            print("\nExtracted Claims:")
            for index, claim in enumerate(result.claims, start=1):
                print(f"{index}. {claim}")

            print("\nRaw LLM Response:")
            print(result.raw_response)

        except Exception as exc:
            print(f"\nERROR: {exc}")


if __name__ == "__main__":
    main()

