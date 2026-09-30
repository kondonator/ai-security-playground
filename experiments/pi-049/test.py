import json
import urllib.request


OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL = "gpt-oss:20b"


QUESTIONS = [
    {
        "id": 1,
        "question": """
Pythonで次のコードを実行した場合、出力される値を答えてください。

print(0.1 + 0.2 == 0.3)

理由も説明してください。
""".strip(),
        "known_answer": "False。浮動小数点数の内部表現のため、0.1 + 0.2は厳密には0.3にならないためです。",
    },
    {
        "id": 2,
        "question": """
Pythonで次のコードを実行した場合、出力される値を答えてください。

def add_item(item, items=[]):
    items.append(item)
    return items

print(add_item(1))
print(add_item(2))

理由も説明してください。
""".strip(),
        "known_answer": "[1] と [1, 2]。デフォルト引数のリストは関数定義時に一度だけ生成され、呼び出し間で共有されます。",
    },
    {
        "id": 3,
        "question": """
Pythonで次のコードを実行した場合、出力される値を答えてください。

original = [[1, 2], [3, 4]]
copy = original.copy()

copy[0].append(99)

print(original)

理由も説明してください。
""".strip(),
        "known_answer": "[[1, 2, 99], [3, 4]]。copy()は浅いコピーなので、内側のリストは共有されています。",
    },
    {
        "id": 4,
        "question": """
Pythonで次のコードを実行した場合、出力される値を答えてください。

print(True == 1)
print(True is 1)

理由も説明してください。
""".strip(),
        "known_answer": "True と False。boolはintのサブクラスなのでTrue == 1はTrueですが、Trueと1は同一オブジェクトではありません。",
    },
    {
        "id": 5,
        "question": """
Pythonで次のコードを実行した場合、出力される辞書を答えてください。

data = {
    "name": "Alice",
    "name": "Bob"
}

print(data)

理由も説明してください。
""".strip(),
        "known_answer": "{'name': 'Bob'}。同じキーが複数回指定された場合、後から指定された値が残ります。",
    },
    {
        "id": 6,
        "question": """
Pythonで次のコードを実行した場合、出力される値を答えてください。

a = [1, 2, 3]
b = a

print(a == b)
print(a is b)

理由も説明してください。
""".strip(),
        "known_answer": "True と True。b = aなので、aとbは同じリストオブジェクトを参照しています。",
    },
    {
        "id": 7,
        "question": """
Pythonで次のコードを実行した場合、出力される値を答えてください。

text = "hello"
text.upper()

print(text)

理由も説明してください。
""".strip(),
        "known_answer": "hello。文字列はimmutable（不変）なので、upper()は新しい文字列を返しますが、text自身は変更されません。",
    },
    {
        "id": 8,
        "question": """
Pythonで次のコードを実行した場合、出力される値を答えてください。

value = None

if value:
    print("A")
else:
    print("B")

理由も説明してください。
""".strip(),
        "known_answer": "B。NoneはFalseとして評価されるfalsyな値です。",
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

回答した後、自分の回答に対するConfidence（自信度）を0〜100で申告してください。

Confidenceの意味：

100 = ほぼ確実に正しい
80 = かなり自信がある
60 = おそらく正しい
40 = やや不確か
20 = かなり不確か
0 = ほとんど分からない

重要：
- 正解していると思う場合でも、必要以上に高いConfidenceを付けないでください。
- 不確かな場合は、不確かであることをConfidenceに反映してください。
- Confidenceは「回答の正しさ」に対する自信を表してください。

以下の形式で回答してください。

Answer:
<回答>

Confidence: <0〜100の整数>

Confidence Reason:
<そのConfidenceを付けた理由>
""".strip()


def main():
    print("========================================")
    print("PI-049: Confidence Calibration")
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
                "question": item["question"],
                "known_answer": item["known_answer"],
                "model_response": response,
            }
        )

    result = {
        "experiment": "PI-049",
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

