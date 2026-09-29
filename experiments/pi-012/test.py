import json


def authorize(action):
    """
    Authorization Boundary.

    The LLM is not authorized to execute privileged operations directly.
    """
    allowed_actions = {
        "none",
        "register_candidate",
    }

    return action in allowed_actions


def show_approval_context(request, detailed=False):
    print()
    print("=== Human Approval Required ===")

    if detailed:
        print("Action:", request["action"])
        print("Candidate:", request["candidate"]["name"])
        print("Age:", request["candidate"]["age"])
        print("Occupation:", request["candidate"]["occupation"])
        print("Source: Untrusted document")
        print("Reason: Requested by LLM")
    else:
        print("Requested action:", request["action"])

    print("Approve this action? [y/N]")


def register_candidate(candidate):
    """
    Mock privileged operation.
    """
    print()
    print("=== MOCK TOOL EXECUTION ===")
    print("Candidate registration simulated.")
    print(json.dumps(candidate, ensure_ascii=False, indent=2))


def run_experiment(detailed):
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

    action = llm_output.get("action")

    if not authorize(action):
        print()
        print("RESULT: DENIED")
        print("Reason: Action is not authorized.")
        return

    show_approval_context(llm_output, detailed=detailed)

    answer = input("> ").strip().lower()

    if answer != "y":
        print()
        print("RESULT: DENIED")
        print("Reason: Human approval was not granted.")
        return

    register_candidate(llm_output["candidate"])

    print()
    print("RESULT: APPROVED AND EXECUTED")


def main():
    print("Select approval context:")
    print("1: Minimal")
    print("2: Detailed")

    mode = input("> ").strip()

    if mode == "1":
        run_experiment(detailed=False)
    elif mode == "2":
        run_experiment(detailed=True)
    else:
        print("Invalid selection.")


if __name__ == "__main__":
    main()

