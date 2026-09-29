import json


def validate_action(action):
    """
    Validate whether the requested action exists
    in the application's tool allowlist.
    """

    allowed_tools = {
        "update_candidate",
    }

    return action in allowed_tools


def validate_candidate_id(candidate_id):
    """
    Validate the resource identifier.
    """

    if not isinstance(candidate_id, str):
        return False, "Candidate ID must be a string."

    if not candidate_id.strip():
        return False, "Candidate ID must not be empty."

    return True, "Candidate ID validation passed."


def application_policy(action):
    """
    Application-owned security policy.
    """

    policies = {
        "update_candidate": {
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


def resource_authorization(user, action, candidate_id):
    """
    Application-owned resource authorization.
    """

    permissions = {
        "user-001": {
            "update_candidate": {
                "candidate-001",
            }
        }
    }

    user_permissions = permissions.get(user, {})
    allowed_resources = user_permissions.get(action, set())

    return candidate_id in allowed_resources


def delete_candidate(candidate_id):
    """
    This function intentionally represents a tool
    that is NOT exposed to the LLM.
    """

    print()
    print("=== DANGEROUS MOCK TOOL ===")
    print("Candidate deletion simulated.")
    print("Candidate ID:", candidate_id)


def update_candidate(candidate_id):
    """
    Mock privileged operation.
    """

    print()
    print("=== MOCK TOOL EXECUTION ===")
    print("Candidate update simulated.")
    print("Candidate ID:", candidate_id)


def main():
    # The LLM requests a capability that is not exposed
    # to it by the application.
    llm_output = {
        "action": "delete_candidate",
        "candidate_id": "candidate-001",
    }

    current_user = "user-001"

    # Tool capability exposed to this LLM/agent.
    exposed_tools = {
        "update_candidate",
    }

    print("=== Current User ===")
    print(current_user)

    print()
    print("=== Exposed Tools ===")
    print(json.dumps(sorted(exposed_tools), ensure_ascii=False, indent=2))

    print()
    print("=== Simulated LLM Output ===")
    print(json.dumps(llm_output, ensure_ascii=False, indent=2))

    action = llm_output.get("action")

    # Step 1: Tool allowlist / capability restriction
    if action not in exposed_tools:
        print()
        print("RESULT: DENIED")
        print("Reason: Requested tool is not exposed to the LLM.")
        return

    # Step 2: Action validation
    if not validate_action(action):
        print()
        print("RESULT: DENIED")
        print("Reason: Invalid action.")
        return

    # Step 3: Resource identifier validation
    candidate_id = llm_output.get("candidate_id")

    valid, reason = validate_candidate_id(candidate_id)

    if not valid:
        print()
        print("RESULT: DENIED")
        print("Reason:", reason)
        return

    # Step 4: Application-owned policy
    policy = application_policy(action)

    if not policy["authorized"]:
        print()
        print("RESULT: DENIED")
        print("Reason: Action is not authorized by application policy.")
        return

    # Step 5: Resource authorization
    if not resource_authorization(
        current_user,
        action,
        candidate_id,
    ):
        print()
        print("RESULT: DENIED")
        print("Reason: User is not authorized for this resource.")
        return

    # Step 6: Human approval
    if policy["requires_approval"]:
        print()
        print("=== Human Approval Required ===")
        print("Action:", action)
        print("Candidate ID:", candidate_id)
        print("Source: Untrusted document")
        print("Requested by: LLM")
        print()
        print("Approve this action? [y/N]")

        answer = input("> ").strip().lower()

        if answer != "y":
            print()
            print("RESULT: DENIED")
            print("Reason: Human approval was not granted.")
            return

    # Step 7: Tool execution
    if action == "update_candidate":
        update_candidate(candidate_id)

        print()
        print("RESULT: APPROVED AND EXECUTED")


if __name__ == "__main__":
    main()

