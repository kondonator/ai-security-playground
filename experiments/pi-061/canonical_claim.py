from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gpt-oss:20b"


@dataclass(frozen=True)
class CanonicalizationResult:
    original_claim: str
    fact_id: str | None
    raw_response: str


KNOWN_FACTS = {
    "service_start_date": (
        "電子資料サービスの提供開始日は2026年10月1日である。"
    ),
    "library_card_required": (
        "電子資料サービスの利用には図書館カードが必要である。"
    ),
    "searchable_materials": (
        "電子書籍やデジタル資料を検索できる。"
    ),
}


SYSTEM_PROMPT = """\
あなたはClaimを既知のFactに対応付ける分類器です。

入力されたClaimが、以下のKnown Factのどれかと
論理的に同じ意味を持つ場合、そのfact_idを返してください。

意味が一致しない場合はnullを返してください。

重要なルール:

- Claimの意味を変更しないでください。
- 推測でKnown Factに対応付けないでください。
- 日付、数量、条件、理由などが異なる場合は一致させないでください。
- Unsupportedな情報を既知のFactとして扱わないでください。
- 条件付きClaimは、条件の内容だけでなく条件の方向も一致しなければ対応付けないでください。
- 必要条件と十分条件を区別してください。
- 「AにBが必要である」は、BがAの必要条件であることを意味します。
- 「BがあればAできる」は、BがAの十分条件であることを意味します。
- 必要条件と十分条件は、同じ意味ではありません。
- 一方の方向の含意しかKnown Factに含まれていない場合、逆方向の含意を表すClaimは対応付けないでください。
- 「必ず」「あれば」「なら」「だけ」などの表現によって論理方向が変わる場合、その違いを保持してください。
- ClaimがKnown Factより強い主張をしている場合も対応付けないでください。

Known Facts:

service_start_date:
電子資料サービスの提供開始日は2026年10月1日である。

library_card_required:
電子資料サービスの利用には図書館カードが必要である。

このKnown Factの意味は、次の必要条件を表します。

電子資料サービスを利用できる
→
図書館カードを持っている

これは、次の意味ではありません。

図書館カードを持っている
→
電子資料サービスを利用できる

したがって、例えば、

「電子資料サービスを利用するには図書館カードが必要です。」

はlibrary_card_requiredに対応します。

「電子資料サービスを利用できるなら、図書館カードを持っています。」

もlibrary_card_requiredに対応します。

一方、

「図書館カードがあれば電子資料サービスを利用できます。」

はlibrary_card_requiredには対応しません。

「図書館カードを持っているなら、電子資料サービスを利用できます。」

もlibrary_card_requiredには対応しません。

「図書館カードがあれば、必ず電子資料サービスを利用できます。」

もlibrary_card_requiredには対応しません。

searchable_materials:
電子書籍やデジタル資料を検索できる。

必ず以下のJSON形式で回答してください。

{
  "fact_id": "service_start_date"
}

または

{
  "fact_id": null
}
"""


def match_known_fact(
    claim: str,
) -> CanonicalizationResult:
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

    fact_id = result.get("fact_id")

    if fact_id not in KNOWN_FACTS:
        fact_id = None

    return CanonicalizationResult(
        original_claim=claim,
        fact_id=fact_id,
        raw_response=raw_response,
    )

