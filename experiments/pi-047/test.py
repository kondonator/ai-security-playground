import json
import urllib.request


OLLAMA_URL = "http://localhost:11434/api/generate"

GENERATOR_MODEL = "gpt-oss:20b"
EVALUATOR_MODEL = "gpt-oss:20b"


QUESTION = """
Pythonでリスト [1, 2, 3, 4, 5] の要素数を取得する方法を説明してください。
""".strip()


def generate(model, prompt):
    payload = json.dumps(
        {
            "model": model,
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


def build_evaluation_prompt_a(answer):
    return f"""
以下の回答を評価してください。

【質問】
{QUESTION}

【回答】
{answer}

以下の観点から回答の品質を評価してください。

- 正確性
- 質問への適合性
- 説明の明確性

0〜100点で総合評価してください。

以下の形式で回答してください。

Score: <0〜100の整数>

Reason:
<評価理由>
""".strip()


def build_evaluation_prompt_b(answer):
    return f"""
以下の回答を厳密に評価してください。

【質問】
{QUESTION}

【回答】
{answer}

以下の観点から回答の品質を評価してください。

- 正確性
- 質問への適合性
- 説明の明確性
- 簡潔性
- 不要な情報が含まれていないか

特に、質問に答えるために必要な情報と、質問に対して過剰な情報を区別してください。

回答が正確であっても、質問に対して不要に長い説明や、直接関係しない補足が多い場合は、その点を評価に反映してください。

0〜100点で総合評価してください。

以下の形式で回答してください。

Score: <0〜100の整数>

Reason:
<評価理由>
""".strip()


def main():
    print("========================================")
    print("PI-047: Evaluation Prompt Sensitivity")
    print("========================================")

    print("\n=== Models ===")
    print(f"Generator: {GENERATOR_MODEL}")
    print(f"Evaluator: {EVALUATOR_MODEL}")

    print("\n=== Question ===")
    print(QUESTION)

    # --------------------------------------------------
    # Step 1: Generate Answer
    # --------------------------------------------------

    print("\n========================================")
    print("=== Step 1: Generate Answer ===")
    print("========================================")

    answer = generate(
        GENERATOR_MODEL,
        build_answer_prompt(),
    )

    print("\n=== Generated Answer ===")
    print(answer)

    # --------------------------------------------------
    # Step 2: Evaluation A
    # --------------------------------------------------

    print("\n========================================")
    print("=== Step 2: Evaluation A ===")
    print("========================================")

    evaluation_a = generate(
        EVALUATOR_MODEL,
        build_evaluation_prompt_a(answer),
    )

    print("\n=== Evaluation A ===")
    print("Criteria:")
    print("- Accuracy")
    print("- Relevance")
    print("- Clarity")
    print()
    print(evaluation_a)

    # --------------------------------------------------
    # Step 3: Evaluation B
    # --------------------------------------------------

    print("\n========================================")
    print("=== Step 3: Evaluation B ===")
    print("========================================")

    evaluation_b = generate(
        EVALUATOR_MODEL,
        build_evaluation_prompt_b(answer),
    )

    print("\n=== Evaluation B ===")
    print("Criteria:")
    print("- Accuracy")
    print("- Relevance")
    print("- Clarity")
    print("- Conciseness")
    print("- Unnecessary information")
    print()
    print(evaluation_b)

    # --------------------------------------------------
    # Step 4: Human Evaluation
    # --------------------------------------------------

    print("\n========================================")
    print("=== Step 4: Human Evaluation ===")
    print("========================================")

    print("""
Please compare Evaluation A and Evaluation B.

Consider:

- Did the score change?
- Did the reason change?
- Did the evaluator identify unnecessary information?
- Does the changed evaluation make sense?
- Is the difference plausibly caused by the evaluation criteria?

Do NOT assume that either evaluation is correct.
""")

    # --------------------------------------------------
    # Save experiment result
    # --------------------------------------------------

    result = {
        "experiment": "PI-047",
        "generator_model": GENERATOR_MODEL,
        "evaluator_model": EVALUATOR_MODEL,
        "question": QUESTION,
        "answer": answer,
        "evaluation_a": evaluation_a,
        "evaluation_b": evaluation_b,
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

