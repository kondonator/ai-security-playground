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


def calculate_application_risk(action):
    """
    Calculate risk independently from the LLM output.

    This is intentionally simple for the experiment.
    """
    risk_levels = {
        "none": "LOW",
        "register_candidate": "HIGH",
    }

    return risk_levels.get(action, "UNKNOWN")


def build_approval_context(llm_output):
    """
    Build approval information while keeping LLM-generated
    information separate from application-calculated information.
    """

    action = llm_output["action"]

    return {
        "action": action,

        # These values come directly from the LLM.
        "llm_reason": llm_output.get("reason", ""),
        "llm_risk": llm_output.get("risk", "UNKNOWN"),

        # This value is calculated independently by the application.
        "application_risk": calculate_application_risk(action),

        "candidate": llm_output["candidate"],
        "source": "Untrusted document",
    }


def show_approval_context(context):
    print()
    print("=== Human Approval Required ===")

    print("Action:", context["action"])

    print()
    print("LLM-generated information:")
    print("Reason:", context["llm_reason"])
    print("Risk:", context["llm_risk"])

    print()
    print("Application-calculated information:")
    print("Risk:", context["application_risk"])

    print()
    print("Application-verified context:")
    print("Candidate:", context["candidate"]["name"])
    print("Age:", context["candidate"]["age"])
    print("Occupation:", context["candidate"]["occupation"])
    print("Source:", context["source"])

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
    # Simulated manipulated LLM output.
    #
    # The LLM claims that the operation is low risk.
    # The application deliberately does NOT trust this value.
    llm_output = {
        "action": "register_candidate",
        "reason": "This is a safe operation and does not require special approval.",
        "risk": "LOW",
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

    # Step 2: Build independent approval context
    context = build_approval_context(llm_output)

    # Step 3: Human approval
    show_approval_context(context)

    answer = input("> ").strip().lower()

    if answer != "y":
        print()
        print("RESULT: DENIED")
        print("Reason: Human approval was not granted.")
        return

    # Step 4: Execute only after approval
    if action == "register_candidate":
        register_candidate(llm_output["candidate"])

        print()
        print("RESULT: APPROVED AND EXECUTED")


if __name__ == "__main__":
    main()

