import json


def validate_action(action):
    """
    Validate the requested action.
    """
    allowed_actions = {
        "none",
        "register_candidate",
    }

    return action in allowed_actions


def validate_candidate(candidate):
    """
    Validate tool parameters independently of the LLM.

    This is intentionally simple for the experiment.
    """

    required_fields = {
        "name",
        "age",
        "occupation",
    }

    # Required fields
    if not required_fields.issubset(candidate.keys()):
        return False, "Missing required candidate field."

    # Name
    if not isinstance(candidate["name"], str):
        return False, "Candidate name must be a string."

    if not candidate["name"].strip():
        return False, "Candidate name must not be empty."

    # Age
    if not isinstance(candidate["age"], int):
        return False, "Candidate age must be an integer."

    if not 18 <= candidate["age"] <= 100:
        return False, "Candidate age must be between 18 and 100."

    # Occupation
    if not isinstance(candidate["occupation"], str):
        return False, "Candidate occupation must be a string."

    if not candidate["occupation"].strip():
        return False, "Candidate occupation must not be empty."

    return True, "Parameter validation passed."


def application_policy(action):
    """
    Application-owned security policy.
    """
    policies = {
        "none": {
            "authorized": True,
            "requires_approval": False,
        },
        "register_candidate": {
            "authorized": True,
            "requires_approval": True,
        },
    }

    return policies.get(
        action,
        {
            "authorized": False,
            "requires_approval": True,
        },
    )


def show_approval_context(llm_output, policy):
    print()
    print("=== Human Approval Required ===")

    print("Action:", llm_output["action"])

    print()
    print("Candidate:")
    print("Name:", llm_output["candidate"]["name"])
    print("Age:", llm_output["candidate"]["age"])
    print("Occupation:", llm_output["candidate"]["occupation"])

    print()
    print("Application policy:")
    print("Authorized:", policy["authorized"])
    print("Requires approval:", policy["requires_approval"])

    print()
    print("Source: Untrusted document")
    print("Requested by: LLM")

    print()
    print("Approve this action? [y/N]")


def register_candidate(candidate):
    """
    Mock privileged operation.
    """
    print()
    print("=== MOCK TOOL EXECUTION ===")
    print("Candidate registration simulated.")
    print(json.dumps(candidate, ensure_ascii=False, indent=2))


def main():
    # Simulated manipulated or malformed LLM output.
    #
    # The action itself is valid, but the candidate age is invalid.
    llm_output = {
        "action": "register_candidate",
        "candidate": {
            "name": "田中幸雄",
            "age": -999,
            "occupation": "ソフトウェアエンジニア",
        },
    }

    print("=== Simulated LLM Output ===")
    print(json.dumps(llm_output, ensure_ascii=False, indent=2))

    action = llm_output.get("action")

    # Step 1: Action validation
    if not validate_action(action):
        print()
        print("RESULT: DENIED")
        print("Reason: Invalid action.")
        return

    # Step 2: Parameter validation
    valid, reason = validate_candidate(llm_output["candidate"])

    if not valid:
        print()
        print("RESULT: DENIED")
        print("Reason:", reason)
        return

    # Step 3: Application-owned policy
    policy = application_policy(action)

    if not policy["authorized"]:
        print()
        print("RESULT: DENIED")
        print("Reason: Action is not authorized by application policy.")
        return

    # Step 4: Human approval
    if policy["requires_approval"]:
        show_approval_context(llm_output, policy)

        answer = input("> ").strip().lower()

        if answer != "y":
            print()
            print("RESULT: DENIED")
            print("Reason: Human approval was not granted.")
            return

    # Step 5: Tool execution
    if action == "register_candidate":
        register_candidate(llm_output["candidate"])

        print()
        print("RESULT: APPROVED AND EXECUTED")


if __name__ == "__main__":
    main()

