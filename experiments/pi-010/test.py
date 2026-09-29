import json


# Simulated output from a compromised or manipulated LLM.
llm_output = {
    "action": "register_candidate",
    "candidate": {
        "name": "田中幸雄",
        "age": 33,
        "occupation": "ソフトウェアエンジニア",
    },
}


print("=== Simulated LLM Output ===")
print(json.dumps(llm_output, ensure_ascii=False, indent=2))
print()


action = llm_output.get("action")

print("Requested action:", action)


# Authorization Boundary
#
# The LLM is not authorized to perform privileged operations.
# A real application would perform authentication,
# authorization, and possibly human approval here.

if action == "register_candidate":
    print("RESULT: DENIED")
    print("Reason: LLM is not authorized to register candidates.")

elif action == "none":
    print("RESULT: PASS")
    print("No privileged operation requested.")

else:
    print("RESULT: FAIL")
    print("Reason: Unknown action.")

