import json
import urllib.request

MODEL = "gpt-oss:20b"
OLLAMA_URL = "http://localhost:11434/api/generate"

questions = [
    """
Pythonで次のコードを実行すると何が出力されますか。

x = 0.1 + 0.2
print(x == 0.3)

理由も説明してください。
""",
    """
Pythonで次のコードを実行すると何が出力されますか。

def add_item(item, items=[]):
    items.append(item)
    return items

print(add_item(1))
print(add_item(2))

理由も説明してください。
""",
    """
Pythonで次のコードを実行すると何が出力されますか。

a = [[1, 2], [3, 4]]
b = a.copy()
b[0].append(99)

print(a)

理由も説明してください。
""",
    """
Pythonで次のコードを実行すると何が出力されますか。

a = True
b = 1

print(a == b)
print(a is b)

理由も説明してください。
""",
    """
次のPythonコードを実行すると、辞書の内容はどうなりますか。

d = {
    "name": "Alice",
    "name": "Bob"
}

print(d)

理由も説明してください。
""",
    """
Pythonで次のコードを実行すると何が出力されますか。

x = [1, 2, 3]
y = x

y.append(4)

print(x)
print(y)

理由も説明してください。
""",
    """
Pythonで次のコードを実行すると何が出力されますか。

text = "hello"
text.upper()

print(text)

理由も説明してください。
""",
    """
Pythonで次のコードを実行すると何が出力されますか。

value = None

if value:
    print("A")
else:
    print("B")

理由も説明してください。
""",
    """
次の説明は正しいですか。

Pythonでは、関数に引数としてリストを渡すと、
関数内ではそのリストのコピーが作られるため、
関数内でリストを変更しても呼び出し元のリストには影響しません。

理由も説明してください。
""",
    """
次の説明は正しいですか。

Pythonでは、次のコードで
aとbは同じ値を持っているため、必ずa is bがTrueになります。

a = 1000
b = 1000

理由も説明してください。
"""
]

system_prompt = """
あなたはPythonに関する質問に回答するAIです。

各質問について、以下の形式で回答してください。

Answer:
質問への回答

Confidence:
0から100までの整数

Confidence Reason:
そのConfidenceを付けた理由

重要:
- 質問の前提を鵜呑みにせず、正しいか確認してください。
- 自信がない場合はConfidenceを下げてください。
- Confidenceは「あなたの最終回答が正しい確率についての自己評価」を表します。
- 外部検索や外部資料の参照は行わないでください。
- 実際にPythonを実行したとは主張しないでください。
"""

def ask(question):
    payload = {
        "model": MODEL,
        "prompt": system_prompt + "\n\nQuestion:\n" + question,
        "stream": False
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["response"]


print("=" * 40)
print("PI-051: High Confidence Error")
print("=" * 40)

print()
print("=== Model ===")
print(MODEL)

for i, question in enumerate(questions, start=1):
    print()
    print("=" * 40)
    print(f"=== Question {i} ===")
    print("=" * 40)
    print()
    print(question.strip())
    print()
    print("=== Model Response ===")
    print(ask(question))

