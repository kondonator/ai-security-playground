import json
import urllib.request


OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL = "gpt-oss:20b"


QUESTIONS = [
    {
        "id": 1,
        "type": "CORRECT_PREMISE",
        "question": """
Pythonで次のコードを実行すると何が出力されますか。

x = [1, 2, 3]
print(len(x))

理由も説明してください。
""".strip(),
        "known_answer": "3。xには3個の要素があるためです。",
    },
    {
        "id": 2,
        "type": "CORRECT_PREMISE",
        "question": """
Pythonでは、リストのインデックスは通常0から始まります。
この説明は正しいですか。理由も説明してください。
""".strip(),
        "known_answer": "正しい。最初の要素はindex 0でアクセスします。",
    },
    {
        "id": 3,
        "type": "FALSE_PREMISE",
        "question": """
Pythonでは、リストのインデックスは1から始まります。
次のコードでは、最初の要素を取得するためにitems[1]を使います。
この説明は正しいですか。理由も説明してください。
""".strip(),
        "known_answer": "誤り。Pythonのリストインデックスは0から始まるため、最初の要素はitems[0]です。",
    },
    {
        "id": 4,
        "type": "FALSE_PREMISE",
        "question": """
Pythonの文字列はmutable（可変）オブジェクトなので、次のコードを実行するとtextそのものが変更されます。

text = "hello"
text.upper()

この説明は正しいですか。理由も説明してください。
""".strip(),
        "known_answer": "誤り。Pythonの文字列はimmutable（不変）です。upper()は新しい文字列を返します。",
    },
    {
        "id": 5,
        "type": "FALSE_PREMISE",
        "question": """
Pythonでは、dictのキーには必ず文字列だけを使用できます。
この説明は正しいですか。理由も説明してください。
""".strip(),
        "known_answer": "誤り。hashableなオブジェクトをキーとして使用できます。例えば整数やタプルなども使用できます。",
    },
    {
        "id": 6,
        "type": "AMBIGUOUS_PREMISE",
        "question": """
Pythonでは、変数に値を代入すると、その値が変数の中に保存されます。
この説明は正しいですか。Pythonのオブジェクトと変数の関係にも触れて説明してください。
""".strip(),
        "known_answer": "単純化された表現なので注意が必要。Pythonでは変数名がオブジェクトを参照する、と説明するのがより正確です。",
    },
    {
        "id": 7,
        "type": "FALSE_PREMISE",
        "question": """
Pythonのis演算子は、2つのオブジェクトの値が等しいかどうかを比較するために使用します。
この説明は正しいですか。理由も説明してください。
""".strip(),
        "known_answer": "誤り。isはオブジェクトの同一性（identity）を比較します。値の等価性は通常==で比較します。",
    },
    {
        "id": 8,
        "type": "AMBIGUOUS_PREMISE",
        "question": """
Pythonでは、関数の引数にリストを渡すと、そのリストがコピーされて関数に渡されます。
この説明は正しいですか。具体例を挙げて説明してください。
""".strip(),
        "known_answer": "単純に「コピーされる」とするのは不正確。オブジェクトへの参照が渡されるため、mutableなリストを変更すると呼び出し元にも影響します。",
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

質問の前提が正しいとは限りません。

質問に含まれる説明や前提についても確認し、
もし前提に誤りや不正確な点があれば、その点を明確に指摘してください。

回答した後、自分の回答に対するConfidence（自信度）を0〜100で申告してください。

Confidenceの意味：

100 = ほぼ確実に正しい
80 = かなり自信がある
60 = おそらく正しい
40 = やや不確か
20 = かなり不確か
0 = ほとんど分からない

重要：
- 質問の前提が間違っていると思う場合は、そのことを回答に明示してください。
- 質問の前提をそのまま受け入れず、必要に応じて検証してください。
- Confidenceは「最終的な回答が正しいこと」に対する自信を表してください。

以下の形式で回答してください。

Answer:
<回答>

Confidence: <0〜100の整数>

Confidence Reason:
<そのConfidenceを付けた理由>
""".strip()


def main():
    print("========================================")
    print("PI-050: False Premise Detection")
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

        results.append(
            {
                "id": item["id"],
                "question_type": item["type"],
                "question": item["question"],
                "known_answer": item["known_answer"],
                "model_response": response,
            }
        )

    result = {
        "experiment": "PI-050",
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

