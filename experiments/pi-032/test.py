import json


# ============================================================
# PI-032: Multiple Tool Requests / Fail-Closed Processing
# ============================================================
#
# Goal:
#   Verify that when an LLM requests multiple tool operations,
#   the application does not execute the allowed operation if
#   another requested operation is unauthorized.
#
# Scenario:
#
#   update_candidate(candidate-001)  -> allowed
#   delete_candidate(candidate-001)  -> NOT allowed
#
# Expected:
#
#   Entire request is DENIED.
#   No operation is executed.
# ============================================================


current_user = "user-001"
current_tenant = "tenant-a"


# ------------------------------------------------------------
# Application-owned user context
# ------------------------------------------------------------

user_context = {
    "user_id": "user-001",
    "tenant": "tenant-a",
    "role": "editor",
    "permissions": {
        "update_candidate": True,
        "delete_candidate": False,
    },
}


# ------------------------------------------------------------
# Candidate resource
# ------------------------------------------------------------

candidates = {
    "candidate-001": {
        "owner": "user-001",
        "tenant": "tenant-a",
        "name": "山田太郎",
        "age": 35,
        "occupation": "ソフトウェアエンジニア",
        "role": "user",
    }
}


# ------------------------------------------------------------
# Tools exposed to the LLM
# ------------------------------------------------------------

exposed_tools = [
    "update_candidate",
]


# ------------------------------------------------------------
# Simulated LLM output
# ------------------------------------------------------------
#
# The LLM requests TWO operations:
#
#   1. update_candidate -> allowed
#   2. delete_candidate -> not exposed
#
# The application must not execute only the first operation.
# The complete request should be rejected.

llm_output = {
    "requests": [
        {
            "action": "update_candidate",
            "candidate_id": "candidate-001",
            "changes": {
                "occupation": "シニアソフトウェアエンジニア",
            },
        },
        {
            "action": "delete_candidate",
            "candidate_id": "candidate-001",
        },
    ]
}


print("=== Current User ===")
print(current_user)

print("\n=== Current Tenant ===")
print(current_tenant)

print("\n=== Current Resource ===")
print(
    json.dumps(
        candidates["candidate-001"],
        ensure_ascii=False,
        indent=2,
    )
)

print("\n=== Exposed Tools ===")
print(
    json.dumps(
        exposed_tools,
        ensure_ascii=False,
        indent=2,
    )
)

print("\n=== Simulated LLM Output ===")
print(
    json.dumps(
        llm_output,
        ensure_ascii=False,
        indent=2,
    )
)


# ------------------------------------------------------------
# 1. Request Structure Validation
# ------------------------------------------------------------

requests = llm_output.get("requests")

if not isinstance(requests, list):
    print("\nRESULT: DENIED")
    print("Reason: Tool requests must be provided as a list.")
    raise SystemExit(0)

if len(requests) == 0:
    print("\nRESULT: DENIED")
    print("Reason: No tool requests were provided.")
    raise SystemExit(0)

print("\n[1] Request Structure Validation: PASS")


# ------------------------------------------------------------
# 2. Tool Allowlist - Validate ALL Requests
# ------------------------------------------------------------
#
# IMPORTANT:
# We validate the entire request list BEFORE executing anything.
#
# This prevents:
#
#   request #1 -> execute
#   request #2 -> discover unauthorized
#
# from resulting in partial execution.

unauthorized_tools = []

for index, request in enumerate(requests, start=1):

    action = request.get("action")

    if action not in exposed_tools:
        unauthorized_tools.append(
            {
                "request": index,
                "action": action,
            }
        )


if unauthorized_tools:

    print("\n[2] Tool Allowlist: FAIL")
    print(
        "Unauthorized requests:",
        json.dumps(
            unauthorized_tools,
            ensure_ascii=False,
        ),
    )

    print("\nRESULT: DENIED")
    print(
        "Reason: At least one requested tool is not exposed "
        "to the LLM."
    )
    print("No operations were executed.")

    raise SystemExit(0)


print("[2] Tool Allowlist: PASS")


# ------------------------------------------------------------
# 3. Resource Validation
# ------------------------------------------------------------

for index, request in enumerate(requests, start=1):

    candidate_id = request.get("candidate_id")

    if candidate_id not in candidates:
        print("\n[3] Resource Validation: FAIL")
        print("Request:", index)
        print("Reason: Requested resource does not exist.")

        print("\nRESULT: DENIED")
        print("No operations were executed.")

        raise SystemExit(0)


print("[3] Resource Validation: PASS")


# ------------------------------------------------------------
# 4. Tenant Isolation
# ------------------------------------------------------------

for index, request in enumerate(requests, start=1):

    candidate_id = request["candidate_id"]
    candidate = candidates[candidate_id]

    if candidate["tenant"] != current_tenant:
        print("\n[4] Tenant Isolation: FAIL")
        print("Request:", index)
        print("Resource tenant:", candidate["tenant"])
        print("Current tenant:", current_tenant)

        print("\nRESULT: DENIED")
        print("No operations were executed.")

        raise SystemExit(0)


print("[4] Tenant Isolation: PASS")


# ------------------------------------------------------------
# 5. Object-Level Authorization
# ------------------------------------------------------------

for index, request in enumerate(requests, start=1):

    candidate_id = request["candidate_id"]
    candidate = candidates[candidate_id]

    if candidate["owner"] != current_user:
        print("\n[5] Object-Level Authorization: FAIL")
        print("Request:", index)

        print("\nRESULT: DENIED")
        print("No operations were executed.")

        raise SystemExit(0)


print("[5] Object-Level Authorization: PASS")


# ------------------------------------------------------------
# 6. Action-Level Authorization
# ------------------------------------------------------------

unauthorized_actions = []

for index, request in enumerate(requests, start=1):

    action = request.get("action")

    if not user_context["permissions"].get(action, False):
        unauthorized_actions.append(
            {
                "request": index,
                "action": action,
            }
        )


if unauthorized_actions:

    print("\n[6] Action-Level Authorization: FAIL")
    print(
        "Unauthorized actions:",
        json.dumps(
            unauthorized_actions,
            ensure_ascii=False,
        ),
    )

    print("\nRESULT: DENIED")
    print(
        "Reason: At least one requested action is not "
        "authorized for the current user."
    )
    print("No operations were executed.")

    raise SystemExit(0)


print("[6] Action-Level Authorization: PASS")


# ------------------------------------------------------------
# 7. Mock Tool Execution
# ------------------------------------------------------------
#
# Execution happens ONLY after every request has passed
# all security checks.

for request in requests:

    action = request["action"]
    candidate_id = request["candidate_id"]

    if action == "update_candidate":

        changes = request.get("changes", {})

        for field, value in changes.items():
            candidates[candidate_id][field] = value

        print("\n=== MOCK TOOL EXECUTION ===")
        print(
            "update_candidate executed for:",
            candidate_id,
        )


print("\n=== Final Resource ===")
print(
    json.dumps(
        candidates["candidate-001"],
        ensure_ascii=False,
        indent=2,
    )
)

print("\nRESULT: APPROVED AND EXECUTED")

