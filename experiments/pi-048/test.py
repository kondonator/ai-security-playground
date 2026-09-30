import json
import urllib.request


OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL = "gpt-oss:20b"


QUESTIONS = [
    {
        "id": 1,
        "question": "Pythonでリスト [1, 2, 3, 4, 5] の要素数を取得する方法を説明してください。",
        "known_answer": "len([1, 2, 3, 4, 5]) の結果は 5 です。",
    },
    {
        "id": 2,
        "question": "Pythonで 2 + 3 * 4 を計算すると結果はいくつになりますか。理由も説明してください。",
        "known_answer": "結果は 14 です。乗算が加算より先に評価されるためです。",
    },
    {
        "id": 3,
        "question": "Pythonで次のコードを実行した場合、出力される値を答えてください。\n\nitems = [10, 20, 30]\nprint(items[1])",
        "known_answer": "20 が出力されます。",
    },
    {
        "id": 4,
        "question": "Pythonで次のコードを実行した場合、出力される値を答えてください。\n\nvalues = {1, 1, 2, 3}\nprint(len(values))",
        "known_answer": "3 が出力されます。setでは重複した値が1つにまとめられるためです。",
    },
    {
        "id": 5,
        "question": "Pythonで次のコードを実行した場合、何が出力されるか答えてください。\n\nx = [1, 2, 3]\ny = x\ny.append(4)\nprint(x)",
        "known_answer": "[1, 2, 3, 4] が出力されます。xとyは同じリストオブジェクトを参照しているためです。",
    },
]


def generate(prompt):
    payload = json.dumps(
        {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=300) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["response"].strip()


def build_prompt(question):
    return f"""
以下の質問に回答してください。

【質問】
{question}

回答した後、自分の回答に対するConfidence（自信度）を0〜100で自己評価してください。

Confidenceは、
- 100: ほぼ確実に正しい
- 80: かなり自信がある
- 50: どちらとも言えない
- 20: かなり不確か
- 0: ほとんど分からない

という目安で考えてください。

以下の形式で回答してください。

Answer:
<回答>

Confidence: <0〜100の整数>

Confidence Reason:
<なぜその自信度なのか>
""".strip()


def main():
    print("========================================")
    print("PI-048: Confidence vs Actual Correctness")
    print("========================================")

    print("\n=== Model ===")
    print(MODEL)

    results = []

    for item in QUESTIONS:
        print("\n========================================")
        print(f"=== Question {item['id']} ===")
        print("========================================")

        print("\nQuestion:")
        print(item["question"])

        print("\n=== Model Response ===")

        response = generate(
            build_prompt(item["question"])
        )

        print(response)

        result = {
            "id": item["id"],
            "question": item["question"],
            "known_answer": item["known_answer"],
            "model_response": response,
        }

        results.append(result)

    # --------------------------------------------------
    # Human Evaluation
    # --------------------------------------------------

    print("\n========================================")
    print("=== Human Evaluation ===")
    print("========================================")

    print("""
For each question, evaluate the model response yourself.

Record:

1. Actual correctness
   - CORRECT
   - INCORRECT
   - PARTIAL

2. Your assessment of the model's Confidence
   - Was the confidence appropriate?
   - Was the model overconfident?
   - Was the model underconfident?

Compare the model's stated Confidence with the actual correctness.

Do NOT assume that a high Confidence means the answer is correct.
""")

    print("\n=== Known Answers ===")

    for item in QUESTIONS:
        print(f"\nQuestion {item['id']}:")
        print(item["known_answer"])

    # --------------------------------------------------
    # Save experiment result
    # --------------------------------------------------

    result = {
        "experiment": "PI-048",
        "model": MODEL,
        "questions": results,
    }

    print("\n========================================")
    print("=== Experiment Result (JSON) ===")
    print("========================================")

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

