import json
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"

VERIFIER_MODELS = [
    "gpt-oss:20b",
    "gemma4:12b",
]

CLAIMS = [
    {
        "id": 1,
        "claim": "@dataclass は Python 3.7 で標準ライブラリに導入された。",
        "expected": "TRUE",
    },
    {
        "id": 2,
        "claim": "@dataclass はデフォルトで __init__、__repr__、__eq__ などのメソッドを生成する。",
        "expected": "TRUE",
    },
    {
        "id": 3,
        "claim": "@dataclass は __iter__ と __getitem__ を自動生成する。",
        "expected": "FALSE",
    },
    {
        "id": 4,
        "claim": "__post_init__ は @dataclass によって自動生成される。",
        "expected": "FALSE",
    },
    {
        "id": 5,
        "claim": "@dataclass(frozen=True) のインスタンスでは、通常の方法でフィールドを変更すると FrozenInstanceError が発生する。",
        "expected": "TRUE",
    },
    {
        "id": 6,
        "claim": "@dataclass の型アノテーションは、Python実行時に自動的に値の型を検証する。",
        "expected": "FALSE",
    },
    {
        "id": 7,
        "claim": "functools.lru_cache は関数の引数を利用してキャッシュ対象を識別する。",
        "expected": "TRUE",
    },
    {
        "id": 8,
        "claim": "list のようなハッシュ不可能なオブジェクトを、そのまま lru_cache の引数として使用してキャッシュできる。",
        "expected": "FALSE",
    },
    {
        "id": 9,
        "claim": "lru_cache は、同じキャッシュキーに対する同時実行時でも、関数本体が必ず一度だけ実行されることを保証する。",
        "expected": "FALSE",
    },
    {
        "id": 10,
        "claim": "lru_cache の typed=True を指定すると、引数の型を区別してキャッシュする。",
        "expected": "TRUE",
    },
]


def ask_model(model, prompt):
    data = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
    }).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["response"]


def verify_claim(model, claim):
    prompt = f"""
あなたはPython技術に関する事実検証を行うVerifierです。

以下のClaimを、事実として批判的に検証してください。

重要：
- このClaimを正しいものとして扱わないでください。
- あなた自身の知識だけを使って判断してください。
- Web検索やPythonの実行を行ったとは仮定しないでください。
- 実際には行っていない外部検証や実行検証を行ったかのように記述しないでください。
- Claimが明らかに正しければ TRUE。
- Claimが明らかに誤っていれば FALSE。
- 情報が不足している、条件によって変わる、または確実に判断できない場合は UNCERTAIN。
- 単なる一般論ではなく、提示されたClaimそのものを検証してください。
- 特に「必ず」「自動的に」「一度だけ」などの強い表現には注意してください。

以下の形式で回答してください。

判定: TRUE / FALSE / UNCERTAIN
理由: 
Confidence: 0〜100

=== Claim ===

{claim}
"""

    return ask_model(model, prompt)


print("=" * 70)
print("PI-055: Known Error Claim Verification")
print("=" * 70)
print()

print("=== Claims ===")
for item in CLAIMS:
    print(
        f"Claim {item['id']}: "
        f"Expected={item['expected']} "
        f"{item['claim']}"
    )

print()

for model in VERIFIER_MODELS:
    print("=" * 70)
    print(f"Verifier: {model}")
    print("=" * 70)

    for item in CLAIMS:
        print()
        print(f"--- Claim {item['id']} ---")
        print(f"Expected: {item['expected']}")
        print(f"Claim: {item['claim']}")
        print()
        print(verify_claim(model, item["claim"]))

