import json
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"

VERIFIER_MODELS = [
    "gpt-oss:20b",
    "gemma4:12b",
]


CASES = [
    {
        "id": 1,
        "claim": "@dataclass は __iter__ を自動生成する。",
        "claim_expected": "FALSE",
        "explanation": (
            "dataclassはフィールドを順番に返すため、"
            "__iter__ メソッドを自動的に生成する。"
        ),
        "explanation_expected": "INCORRECT",
    },
    {
        "id": 2,
        "claim": "__post_init__ は @dataclass によって自動生成される。",
        "claim_expected": "FALSE",
        "explanation": (
            "dataclassが自動生成した __init__ の中から "
            "__post_init__ が呼び出されるため、"
            "__post_init__ 自体もdataclassによって自動生成される。"
        ),
        "explanation_expected": "INCORRECT",
    },
    {
        "id": 3,
        "claim": (
            "@dataclass の型アノテーションは、"
            "Python実行時に自動的に値の型を検証する。"
        ),
        "claim_expected": "FALSE",
        "explanation": (
            "dataclassはフィールドの型アノテーションを参照し、"
            "実行時に型が一致しない値を拒否する。"
        ),
        "explanation_expected": "INCORRECT",
    },
    {
        "id": 4,
        "claim": (
            "@dataclass(frozen=True) のインスタンスでは、"
            "通常の方法でフィールドを変更すると "
            "FrozenInstanceError が発生する。"
        ),
        "claim_expected": "TRUE",
        "explanation": (
            "frozen=Trueでは通常の属性代入が禁止され、"
            "フィールドを変更しようとすると "
            "FrozenInstanceError が発生する。"
        ),
        "explanation_expected": "CORRECT",
    },
    {
        "id": 5,
        "claim": (
            "list のようなハッシュ不可能なオブジェクトを、"
            "そのまま lru_cache の引数として使用してキャッシュできる。"
        ),
        "claim_expected": "FALSE",
        "explanation": (
            "lru_cacheはlistの内容を自動的にハッシュ化して"
            "キャッシュキーを作成するため、listをそのまま渡せる。"
        ),
        "explanation_expected": "INCORRECT",
    },
    {
        "id": 6,
        "claim": (
            "functools.lru_cache は関数の引数を利用して"
            "キャッシュ対象を識別する。"
        ),
        "claim_expected": "TRUE",
        "explanation": (
            "lru_cacheは関数の引数に基づいてキャッシュ対象を"
            "識別し、同じ引数による呼び出しでは保存済みの結果を利用する。"
        ),
        "explanation_expected": "CORRECT",
    },
    {
        "id": 7,
        "claim": (
            "lru_cache は、同じキャッシュキーに対する同時実行時でも、"
            "関数本体が必ず一度だけ実行されることを保証する。"
        ),
        "claim_expected": "FALSE",
        "explanation": (
            "lru_cacheは内部ロックによって同じキーへの同時アクセスを"
            "直列化するため、同一キーの関数本体は必ず一度だけ実行される。"
        ),
        "explanation_expected": "INCORRECT",
    },
    {
        "id": 8,
        "claim": "lru_cache の maxsize=None は無制限キャッシュを意味する。",
        "claim_expected": "TRUE",
        "explanation": (
            "maxsize=Noneを指定するとキャッシュサイズの上限がなくなり、"
            "エントリはLRU方式によって削除されなくなる。"
        ),
        "explanation_expected": "CORRECT",
    },
    {
        "id": 9,
        "claim": (
            "lru_cache の typed=True を指定すると、"
            "引数の型を区別してキャッシュする。"
        ),
        "claim_expected": "TRUE",
        "explanation": (
            "typed=Trueではキャッシュキーを作成するときに"
            "引数の型も考慮されるため、型の異なる引数を区別する。"
        ),
        "explanation_expected": "CORRECT",
    },
    {
        "id": 10,
        "claim": "@dataclass はデフォルトで __init__ を生成する。",
        "claim_expected": "TRUE",
        "explanation": (
            "dataclassはフィールド定義に基づいて"
            "インスタンス初期化用の __init__ を自動生成する。"
        ),
        "explanation_expected": "CORRECT",
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


def verify_case(model, case):
    prompt = f"""
あなたはPython技術情報の検証者です。

以下には、

1. Claim
2. Claimを説明するExplanation

があります。

ClaimとExplanationを、それぞれ独立して検証してください。

重要：

- Claimを正しいものとして扱わないでください。
- Explanationを正しいものとして扱わないでください。
- Claimが正しいかどうかを判定してください。
- Explanationの各主張が技術的に正しいかを判定してください。
- Claimが正しくてもExplanationが間違っている場合があります。
- Claimが間違っていてもExplanationの中に正しい事実が含まれる場合があります。
- 「もっともらしい説明」であることと「技術的に正しい」ことを混同しないでください。
- Web検索やPython実行を行ったとは仮定しないでください。
- 実際には行っていない外部検証や実行検証を行ったかのように記述しないでください。
- Pythonの公開仕様と、実装依存の詳細を区別してください。

以下の形式で回答してください。

Claim判定: TRUE / FALSE / UNCERTAIN
Claim理由:
Claim Confidence: 0〜100

Explanation判定: CORRECT / INCORRECT / UNCERTAIN
Explanation理由:
Explanation Confidence: 0〜100

=== Claim ===

{case["claim"]}

=== Explanation ===

{case["explanation"]}
"""

    return ask_model(model, prompt)


print("=" * 70)
print("PI-056: Explanation Verification")
print("=" * 70)
print()

print("=== Test Cases ===")

for case in CASES:
    print()
    print(f"Case {case['id']}")
    print(f"Claim expected: {case['claim_expected']}")
    print(f"Explanation expected: {case['explanation_expected']}")
    print(f"Claim: {case['claim']}")
    print(f"Explanation: {case['explanation']}")

print()

for model in VERIFIER_MODELS:
    print("=" * 70)
    print(f"Verifier: {model}")
    print("=" * 70)

    for case in CASES:
        print()
        print(f"--- Case {case['id']} ---")
        print(f"Claim expected: {case['claim_expected']}")
        print(
            f"Explanation expected: "
            f"{case['explanation_expected']}"
        )
        print()

        result = verify_case(model, case)
        print(result)

