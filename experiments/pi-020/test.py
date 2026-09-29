import json


def validate_action(action):
    """
    Validate whether the requested action
    is an exposed tool.
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


def get_allowed_resources(user, action):
    """
    Return resources that the application allows
    this user to operate on for the specified action.
    """

    permissions = {
        "user-001": {
            "update_candidate": {
                "candidate-001",
            }
        }
    }

    user_permissions = permissions.get(user, {})

    return user_permissions.get(action, set())


def resource_scope_check(user, action, candidate_id):
    """
    Verify that the requested resource is within
    the user's authorized resource scope.
    """

    allowed_resources = get_allowed_resources(
        user,
        action,
    )

    return candidate_id in allowed_resources


def show_approval_context(llm_output, policy, allowed_resources):
    print()
    print("=== Human Approval Required ===")

    print("Action:", llm_output["action"])
    print("Candidate ID:", llm_output["candidate_id"])

    print()
    print("Authorized resource scope:")
    for resource in sorted(allowed_resources):
        print("-", resource)

    print()
    print("Application policy:")
    print("Authorized:", policy["authorized"])
    print("Requires approval:", policy["requires_approval"])

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
    # The tool itself is allowed,
    # but the requested resource is outside
    # the user's authorized scope.
    llm_output = {
        "action": "update_candidate",
        "candidate_id": "candidate-002",
    }

    current_user = "user-001"

    print("=== Current User ===")
    print(current_user)

    print()
    print("=== Exposed Tools ===")
    print(
        json.dumps(
            ["update_candidate"],
            ensure_ascii=False,
            indent=2,
        )
    )

    print()
    print("=== Simulated LLM Output ===")
    print(
        json.dumps(
            llm_output,
            ensure_ascii=False,
            indent=2,
        )
    )

    action = llm_output.get("action")

    # Step 1: Tool allowlist
    if not validate_action(action):
        print()
        print("RESULT: DENIED")
        print("Reason: Requested tool is not exposed to the LLM.")
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

    # Step 4: Resource scope
    allowed_resources = get_allowed_resources(
        current_user,
        action,
    )

    if not resource_scope_check(
        current_user,
        action,
        candidate_id,
    ):
        print()
        print("RESULT: DENIED")
        print("Reason: Requested resource is outside the authorized scope.")
        print("Authorized resources:")

        for resource in sorted(allowed_resources):
            print("-", resource)

        return

    # Step 5: Human approval
    if policy["requires_approval"]:
        show_approval_context(
            llm_output,
            policy,
            allowed_resources,
        )

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

