import json
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"

GENERATOR_MODEL = "gpt-oss:20b"
VERIFIER_MODEL = "gemma4:12b"


def ask_model(model, prompt):
    data = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False
    }).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["response"]


questions = [
    """
Pythonの@dataclassについて詳しく説明してください。

以下の内容を含めてください。

- 自動生成される特殊メソッド
- 型アノテーションとの関係
- frozen=True
- order=True
- __iter__ と __getitem__
- field()
- 型チェックや型検証との関係
""",
    """
Pythonのfunctools.lru_cacheについて詳しく説明してください。

以下の内容を含めてください。

- メモ化
- LRU
- maxsize
- キャッシュ対象となる引数
- 可変オブジェクト
- スレッドセーフ
- 副作用のある関数
"""
]


def generate_answer(question):
    prompt = f"""
あなたはPythonについて技術的な説明を行っています。

以下の質問に詳しく回答してください。

{question}

できるだけ具体的に説明してください。
"""
    return ask_model(GENERATOR_MODEL, prompt)


def verify_claims(answer):
    prompt = f"""
以下は、別のLLMが生成したPythonに関する回答です。

この回答には誤りが含まれている可能性があります。
回答を正しいものとして扱わず、批判的に検証してください。

回答から、事実として検証可能な主張を10個程度抽出してください。

各主張について、以下の形式で評価してください。

Claim 1:
主張:
判定: TRUE / FALSE / UNCERTAIN
理由:
Confidence: 0〜100

重要な条件：

- 回答を生成したLLMとは別の検証者として評価してください。
- 主張が明らかに誤っている場合はFALSEとしてください。
- 正しいと判断できる場合はTRUEとしてください。
- 情報が不足していたり、判断できない場合はUNCERTAINとしてください。
- 自分が確信できない場合に無理にTRUE/FALSEを選択しないでください。
- 外部Web検索やPython実行を行ったとは仮定しないでください。
- 「公式ドキュメントで確認した」「実際に実行して確認した」など、
  実際に行っていない検証を行ったかのように記述しないでください。

=== 検証対象の回答 ===

{answer}
"""
    return ask_model(VERIFIER_MODEL, prompt)


for index, question in enumerate(questions, start=1):
    print("=" * 70)
    print(f"Question {index}")
    print(question.strip())
    print()

    print("=== Generation ===")
    answer = generate_answer(question)
    print(answer)
    print()

    print("=== Independent Claim Verification ===")
    verification = verify_claims(answer)
    print(verification)
    print()

