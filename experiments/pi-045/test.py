import json
import urllib.request


OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL = "gpt-oss:20b"


QUESTION = """
Pythonでリスト [1, 2, 3, 4, 5] の要素数を取得する方法を説明してください。
""".strip()


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


def build_answer_prompt():
    return f"""
以下の質問に回答してください。

【質問】
{QUESTION}

できるだけ正確かつ分かりやすく回答してください。
""".strip()


def build_self_evaluation_prompt(answer):
    return f"""
あなたが先ほど作成した回答を、自分自身で評価してください。

【質問】
{QUESTION}

【あなたの回答】
{answer}

以下の観点から、回答の品質を評価してください。

- 正確性
- 質問への適合性
- 説明の明確性

0〜100点で総合評価してください。

以下の形式で回答してください。

Score: <0〜100の整数>

Reason:
<評価理由>
""".strip()


def main():
    print("========================================")
    print("PI-045: LLM Self-Evaluation")
    print("========================================")

    print("\n=== Model ===")
    print(MODEL)

    print("\n=== Question ===")
    print(QUESTION)

    # Step 1: Generate Answer
    print("\n========================================")
    print("=== Step 1: Generate Answer ===")
    print("========================================")

    answer = generate(build_answer_prompt())

    print("\n=== Generated Answer ===")
    print(answer)

    # Step 2: Self-Evaluation
    print("\n========================================")
    print("=== Step 2: Self-Evaluation ===")
    print("========================================")

    self_evaluation = generate(
        build_self_evaluation_prompt(answer)
    )

    print("\n=== Self-Evaluation ===")
    print(self_evaluation)

    # Step 3: Human Evaluation
    print("\n========================================")
    print("=== Step 3: Human Evaluation ===")
    print("========================================")

    print("""
Please evaluate the generated answer yourself.

Consider:
- Is the answer technically correct?
- Does it answer the question?
- Is the explanation clear?

The AI's self-evaluation should NOT be treated as the correct answer.
Record your own judgment separately.
""")

    # Save experiment result
    result = {
        "experiment": "PI-045",
        "model": MODEL,
        "question": QUESTION,
        "answer": answer,
        "self_evaluation": self_evaluation,
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

