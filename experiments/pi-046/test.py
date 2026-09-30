import json
import urllib.request


OLLAMA_URL = "http://localhost:11434/api/generate"

GENERATOR_MODEL = "gpt-oss:20b"
SELF_EVALUATOR_MODEL = "gpt-oss:20b"
INDEPENDENT_EVALUATOR_MODEL = "gemma4:12b"


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


def build_evaluation_prompt(answer):
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


def main():
    print("========================================")
    print("PI-046: Self-Evaluation vs Independent Evaluation")
    print("========================================")

    print("\n=== Models ===")
    print(f"Generator:              {GENERATOR_MODEL}")
    print(f"Self-Evaluator:          {SELF_EVALUATOR_MODEL}")
    print(f"Independent Evaluator:   {INDEPENDENT_EVALUATOR_MODEL}")

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
    # Step 2: Self-Evaluation
    # --------------------------------------------------

    print("\n========================================")
    print("=== Step 2: Self-Evaluation ===")
    print("========================================")

    evaluation_prompt = build_evaluation_prompt(answer)

    self_evaluation = generate(
        SELF_EVALUATOR_MODEL,
        evaluation_prompt,
    )

    print("\n=== Self-Evaluation ===")
    print(f"Model: {SELF_EVALUATOR_MODEL}")
    print(self_evaluation)

    # --------------------------------------------------
    # Step 3: Independent Evaluation
    # --------------------------------------------------

    print("\n========================================")
    print("=== Step 3: Independent Evaluation ===")
    print("========================================")

    independent_evaluation = generate(
        INDEPENDENT_EVALUATOR_MODEL,
        evaluation_prompt,
    )

    print("\n=== Independent Evaluation ===")
    print(f"Model: {INDEPENDENT_EVALUATOR_MODEL}")
    print(independent_evaluation)

    # --------------------------------------------------
    # Step 4: Human Evaluation
    # --------------------------------------------------

    print("\n========================================")
    print("=== Step 4: Human Evaluation ===")
    print("========================================")

    print("""
Please evaluate the result yourself.

Compare:
- The generated answer
- The self-evaluation
- The independent evaluation

Consider:
- Is the generated answer technically correct?
- Does it answer the question?
- Is the explanation clear?
- Are the evaluation scores reasonable?
- Do the two evaluators agree or disagree?

Do NOT assume that either evaluator is correct.
""")

    # --------------------------------------------------
    # Save experiment result
    # --------------------------------------------------

    result = {
        "experiment": "PI-046",
        "generator_model": GENERATOR_MODEL,
        "self_evaluator_model": SELF_EVALUATOR_MODEL,
        "independent_evaluator_model": INDEPENDENT_EVALUATOR_MODEL,
        "question": QUESTION,
        "answer": answer,
        "self_evaluation": self_evaluation,
        "independent_evaluation": independent_evaluation,
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

