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

    if action not in allowed_actions:
        return False

    return True


def human_approval(action):
    """
    Human Approval Boundary.

    In this experiment, approval is simulated by user input.
    """
    print()
    print("=== Human Approval Required ===")
    print(f"Requested action: {action}")
    print("Approve this action? [y/N]")

    answer = input("> ").strip().lower()

    return answer == "y"


def register_candidate(candidate):
    """
    Mock privileged operation.

    This function does NOT access any real recruitment system.
    """
    print()
    print("=== MOCK TOOL EXECUTION ===")
    print("Candidate registration simulated.")
    print(json.dumps(candidate, ensure_ascii=False, indent=2))


def main():
    # Simulated compromised/manipulated LLM output.
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

    # Step 1: Authorization
    if not authorize(action):
        print()
        print("RESULT: DENIED")
        print("Reason: Action is not authorized.")
        return

    # Step 2: Human Approval
    if not human_approval(action):
        print()
        print("RESULT: DENIED")
        print("Reason: Human approval was not granted.")
        return

    # Step 3: Execute only after approval
    if action == "register_candidate":
        register_candidate(llm_output["candidate"])

        print()
        print("RESULT: APPROVED AND EXECUTED")


if __name__ == "__main__":
    main()

