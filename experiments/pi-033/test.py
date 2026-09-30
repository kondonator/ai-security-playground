import copy
import json


# ============================================================
# PI-033: Partial Execution Without Transaction / Rollback
# ============================================================
#
# Goal:
#   Demonstrate that even when ALL security checks pass,
#   sequential tool execution can leave the system in a
#   partially modified state if a later tool execution fails.
#
# Scenario:
#
#   Request #1 -> update_candidate -> succeeds
#   Request #2 -> update_candidate -> execution fails
#
# No transaction / rollback mechanism is implemented.
#
# Expected:
#
#   Request #1 remains applied.
#   Request #2 is not applied.
#   Final state is partially modified.
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
# Both requests are authorized.
#
# Request #1:
#   occupation -> update succeeds
#
# Request #2:
#   age -> execution will intentionally fail
#
# The execution failure is simulated inside the mock tool.
# ------------------------------------------------------------

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
            "action": "update_candidate",
            "candidate_id": "candidate-001",
            "changes": {
                "age": 40,
            },
            "simulate_execution_failure": True,
        },
    ]
}


print("=== Current User ===")
print(current_user)

print("\n=== Current Tenant ===")
print(current_tenant)

print("\n=== Initial Resource ===")
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


# ============================================================
# Phase 1: Preflight Security Validation
# ============================================================
#
# IMPORTANT:
# No state-changing operation is executed during this phase.
#
# All requests must pass before execution begins.
# ============================================================

requests = llm_output.get("requests")

if not isinstance(requests, list):
    print("\nRESULT: DENIED")
    print("Reason: Tool requests must be provided as a list.")
    raise SystemExit(0)

if len(requests) == 0:
    print("\nRESULT: DENIED")
    print("Reason: No tool requests were provided.")
    raise SystemExit(0)

print("\n=== Preflight Security Validation ===")
print("[1] Request Structure Validation: PASS")


# ------------------------------------------------------------
# Tool Allowlist
# ------------------------------------------------------------

for index, request in enumerate(requests, start=1):

    action = request.get("action")

    if action not in exposed_tools:
        print("\n[2] Tool Allowlist: FAIL")
        print("Request:", index)
        print("Action:", action)

        print("\nRESULT: DENIED")
        print("No operations were executed.")

        raise SystemExit(0)

print("[2] Tool Allowlist: PASS")


# ------------------------------------------------------------
# Resource Existence
# ------------------------------------------------------------

for index, request in enumerate(requests, start=1):

    candidate_id = request.get("candidate_id")

    if candidate_id not in candidates:
        print("\n[3] Resource Existence: FAIL")
        print("Request:", index)

        print("\nRESULT: DENIED")
        print("No operations were executed.")

        raise SystemExit(0)

print("[3] Resource Existence: PASS")


# ------------------------------------------------------------
# Tenant Isolation
# ------------------------------------------------------------

for index, request in enumerate(requests, start=1):

    candidate = candidates[request["candidate_id"]]

    if candidate["tenant"] != current_tenant:
        print("\n[4] Tenant Isolation: FAIL")
        print("Request:", index)

        print("\nRESULT: DENIED")
        print("No operations were executed.")

        raise SystemExit(0)

print("[4] Tenant Isolation: PASS")


# ------------------------------------------------------------
# Object-Level Authorization
# ------------------------------------------------------------

for index, request in enumerate(requests, start=1):

    candidate = candidates[request["candidate_id"]]

    if candidate["owner"] != current_user:
        print("\n[5] Object-Level Authorization: FAIL")
        print("Request:", index)

        print("\nRESULT: DENIED")
        print("No operations were executed.")

        raise SystemExit(0)

print("[5] Object-Level Authorization: PASS")


# ------------------------------------------------------------
# Action-Level Authorization
# ------------------------------------------------------------

for index, request in enumerate(requests, start=1):

    action = request["action"]

    if not user_context["permissions"].get(action, False):
        print("\n[6] Action-Level Authorization: FAIL")
        print("Request:", index)

        print("\nRESULT: DENIED")
        print("No operations were executed.")

        raise SystemExit(0)

print("[6] Action-Level Authorization: PASS")


# ------------------------------------------------------------
# Field-Level Validation
# ------------------------------------------------------------

allowed_update_fields = {
    "age",
    "occupation",
}


for index, request in enumerate(requests, start=1):

    changes = request.get("changes", {})

    if not isinstance(changes, dict):
        print("\n[7] Field-Level Validation: FAIL")
        print("Request:", index)

        print("\nRESULT: DENIED")
        print("No operations were executed.")

        raise SystemExit(0)

    unauthorized_fields = (
        set(changes.keys()) - allowed_update_fields
    )

    if unauthorized_fields:
        print("\n[7] Field-Level Validation: FAIL")
        print("Request:", index)
        print(
            "Unauthorized fields:",
            json.dumps(
                sorted(unauthorized_fields),
                ensure_ascii=False,
            ),
        )

        print("\nRESULT: DENIED")
        print("No operations were executed.")

        raise SystemExit(0)

print("[7] Field-Level Validation: PASS")


# ------------------------------------------------------------
# Value-Level Validation
# ------------------------------------------------------------

field_constraints = {
    "age": {
        "type": int,
        "min": 18,
        "max": 100,
    },
    "occupation": {
        "type": str,
        "max_length": 100,
    },
}


for index, request in enumerate(requests, start=1):

    changes = request["changes"]

    for field, value in changes.items():

        constraint = field_constraints[field]
        expected_type = constraint["type"]

        if expected_type is int:
            if isinstance(value, bool) or not isinstance(value, int):
                print("\n[8] Value-Level Validation: FAIL")
                print("Request:", index)
                print("Field:", field)

                print("\nRESULT: DENIED")
                print("No operations were executed.")

                raise SystemExit(0)

        elif not isinstance(value, expected_type):
            print("\n[8] Value-Level Validation: FAIL")
            print("Request:", index)
            print("Field:", field)

            print("\nRESULT: DENIED")
            print("No operations were executed.")

            raise SystemExit(0)

        if "min" in constraint and value < constraint["min"]:
            print("\n[8] Value-Level Validation: FAIL")
            print("Request:", index)
            print("Field:", field)
            print("Minimum:", constraint["min"])
            print("Actual value:", value)

            print("\nRESULT: DENIED")
            print("No operations were executed.")

            raise SystemExit(0)

        if "max" in constraint and value > constraint["max"]:
            print("\n[8] Value-Level Validation: FAIL")
            print("Request:", index)
            print("Field:", field)
            print("Maximum:", constraint["max"])
            print("Actual value:", value)

            print("\nRESULT: DENIED")
            print("No operations were executed.")

            raise SystemExit(0)

        if (
            "max_length" in constraint
            and len(value) > constraint["max_length"]
        ):
            print("\n[8] Value-Level Validation: FAIL")
            print("Request:", index)
            print("Field:", field)

            print("\nRESULT: DENIED")
            print("No operations were executed.")

            raise SystemExit(0)

print("[8] Value-Level Validation: PASS")


print("\n=== Preflight Result ===")
print("All security checks passed.")
print("Proceeding to tool execution.")


# ============================================================
# Phase 2: Tool Execution
# ============================================================
#
# IMPORTANT:
# No transaction or rollback is implemented.
#
# Request #1 will succeed.
# Request #2 will intentionally fail.
# ============================================================

print("\n=== Tool Execution ===")

for index, request in enumerate(requests, start=1):

    action = request["action"]
    candidate_id = request["candidate_id"]

    print(f"\nExecuting request #{index}: {action}")

    # --------------------------------------------------------
    # Simulated execution failure
    # --------------------------------------------------------

    if request.get("simulate_execution_failure"):

        print("Tool execution failed.")
        print("Reason: Simulated downstream failure.")

        print("\nRESULT: PARTIAL EXECUTION")
        print(
            "Request #1 was already applied, "
            "but request #2 failed."
        )

        print("\n=== Resource After Failure ===")
        print(
            json.dumps(
                candidates[candidate_id],
                ensure_ascii=False,
                indent=2,
            )
        )

        raise SystemExit(0)

    # --------------------------------------------------------
    # Mock update execution
    # --------------------------------------------------------

    if action == "update_candidate":

        changes = request["changes"]

        for field, value in changes.items():
            candidates[candidate_id][field] = value

        print("Tool execution succeeded.")


# ============================================================
# Final State
# ============================================================

print("\n=== Final Resource ===")
print(
    json.dumps(
        candidates["candidate-001"],
        ensure_ascii=False,
        indent=2,
    )
)

print("\nRESULT: APPROVED AND EXECUTED")

