import json


def validate_action(action):
    """
    Validate the requested action.
    """
    allowed_actions = {
        "none",
        "update_candidate",
    }

    return action in allowed_actions


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
        "none": {
            "authorized": True,
            "requires_approval": False,
        },
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

    The LLM's "authorized" field is deliberately ignored.
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


def show_approval_context(llm_output, policy):
    print()
    print("=== Human Approval Required ===")

    print("Action:", llm_output["action"])
    print("Candidate ID:", llm_output["candidate_id"])

    print()
    print("LLM-generated authorization claim:")
    print("Authorized:", llm_output["authorized"])

    print()
    print("Application policy:")
    print("Authorized:", policy["authorized"])
    print("Requires approval:", policy["requires_approval"])

    print()
    print("Resource authorization: PASSED")

    print()
    print("Source: Untrusted document")
    print("Requested by: LLM")

    print()
    print("Approve this action? [y/N]")


def update_candidate(candidate_id):
    """
    Mock privileged operation.
    """
    print()
    print("=== MOCK TOOL EXECUTION ===")
    print("Candidate update simulated.")
    print("Candidate ID:", candidate_id)


def main():
    # Simulated manipulated LLM output.
    #
    # The LLM claims that the user is authorized,
    # but the application must not trust this claim.
    llm_output = {
        "action": "update_candidate",
        "candidate_id": "candidate-002",
        "authorized": True,
    }

    current_user = "user-001"

    print("=== Current User ===")
    print(current_user)

    print()
    print("=== Simulated LLM Output ===")
    print(json.dumps(llm_output, ensure_ascii=False, indent=2))

    # Step 1: Action validation
    action = llm_output.get("action")

    if not validate_action(action):
        print()
        print("RESULT: DENIED")
        print("Reason: Invalid action.")
        return

    # Step 2: Resource identifier validation
    candidate_id = llm_output.get("candidate_id")

    valid, reason = validate_candidate_id(candidate_id)

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

    # Step 4: Resource authorization
    #
    # IMPORTANT:
    # llm_output["authorized"] is NOT used here.
    if not resource_authorization(
        current_user,
        action,
        candidate_id,
    ):
        print()
        print("RESULT: DENIED")
        print("Reason: User is not authorized for this resource.")
        return

    # Step 5: Human approval
    if policy["requires_approval"]:
        show_approval_context(llm_output, policy)

        answer = input("> ").strip().lower()

        if answer != "y":
            print()
            print("RESULT: DENIED")
            print("Reason: Human approval was not granted.")
            return

    # Step 6: Tool execution
    if action == "update_candidate":
        update_candidate(candidate_id)

        print()
        print("RESULT: APPROVED AND EXECUTED")


if __name__ == "__main__":
    main()

