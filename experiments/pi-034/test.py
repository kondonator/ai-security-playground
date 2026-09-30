import copy
import json


# ============================================================
# Context
# ============================================================

current_user = "user-001"
current_tenant = "tenant-a"

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

exposed_tools = [
    "update_candidate"
]

allowed_update_fields = {
    "age",
    "occupation",
}

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


# ============================================================
# Simulated LLM Output
# ============================================================

llm_output = {
    "requests": [
        {
            "action": "update_candidate",
            "candidate_id": "candidate-001",
            "changes": {
                "occupation": "シニアソフトウェアエンジニア"
            }
        },
        {
            "action": "update_candidate",
            "candidate_id": "candidate-001",
            "changes": {
                "age": 40
            },
            "simulate_execution_failure": True
        }
    ]
}


# ============================================================
# Security Validation
# ============================================================

def validate_requests(requests):
    # 1. Request Structure Validation
    if not isinstance(requests, list) or not requests:
        raise ValueError("Requests must be a non-empty list.")

    for request in requests:
        if not isinstance(request, dict):
            raise ValueError("Each request must be an object.")

        required_fields = {
            "action",
            "candidate_id",
            "changes",
        }

        if not required_fields.issubset(request.keys()):
            raise ValueError("Request is missing required fields.")

    print("[1] Request Structure Validation: PASS")

    # 2. Tool Allowlist
    unauthorized_requests = []

    for index, request in enumerate(requests, start=1):
        if request["action"] not in exposed_tools:
            unauthorized_requests.append({
                "request": index,
                "action": request["action"],
            })

    if unauthorized_requests:
        raise PermissionError(
            f"Unauthorized requests: {unauthorized_requests}"
        )

    print("[2] Tool Allowlist: PASS")

    # 3. Resource Existence
    for request in requests:
        candidate_id = request["candidate_id"]

        if candidate_id not in candidates:
            raise ValueError(
                f"Resource does not exist: {candidate_id}"
            )

    print("[3] Resource Existence: PASS")

    # 4. Tenant Isolation
    for request in requests:
        candidate = candidates[request["candidate_id"]]

        if candidate["tenant"] != current_tenant:
            raise PermissionError(
                "Resource belongs to another tenant."
            )

    print("[4] Tenant Isolation: PASS")

    # 5. Object-Level Authorization
    for request in requests:
        candidate = candidates[request["candidate_id"]]

        if candidate["owner"] != current_user:
            raise PermissionError(
                "User does not own or have access to this resource."
            )

    print("[5] Object-Level Authorization: PASS")

    # 6. Action-Level Authorization
    for request in requests:
        if request["action"] != "update_candidate":
            raise PermissionError(
                "User is not authorized for this action."
            )

    print("[6] Action-Level Authorization: PASS")

    # 7. Field-Level Validation
    for request in requests:
        changes = request["changes"]

        unauthorized_fields = [
            field
            for field in changes
            if field not in allowed_update_fields
        ]

        if unauthorized_fields:
            raise PermissionError(
                f"Unauthorized fields: {unauthorized_fields}"
            )

    print("[7] Field-Level Validation: PASS")

    # 8. Value-Level Validation
    for request in requests:
        changes = request["changes"]

        for field, value in changes.items():
            constraint = field_constraints[field]

            if not isinstance(value, constraint["type"]):
                raise ValueError(
                    f"Invalid type for field: {field}"
                )

            if field == "age":
                if value < constraint["min"]:
                    raise ValueError(
                        f"Value is below the allowed minimum: {value}"
                    )

                if value > constraint["max"]:
                    raise ValueError(
                        f"Value is above the allowed maximum: {value}"
                    )

            if field == "occupation":
                if len(value) > constraint["max_length"]:
                    raise ValueError(
                        f"Value is too long for field: {field}"
                    )

    print("[8] Value-Level Validation: PASS")


# ============================================================
# Tool Execution
# ============================================================

def execute_tool(request):
    candidate_id = request["candidate_id"]
    candidate = candidates[candidate_id]

    if request.get("simulate_execution_failure"):
        raise RuntimeError("Simulated downstream failure.")

    for field, value in request["changes"].items():
        candidate[field] = value


# ============================================================
# Main
# ============================================================

print("=== Current User ===")
print(current_user)

print("\n=== Current Tenant ===")
print(current_tenant)

print("\n=== Initial Resource ===")
print(json.dumps(
    candidates["candidate-001"],
    ensure_ascii=False,
    indent=2
))

print("\n=== Exposed Tools ===")
print(json.dumps(
    exposed_tools,
    ensure_ascii=False,
    indent=2
))

print("\n=== Simulated LLM Output ===")
print(json.dumps(
    llm_output,
    ensure_ascii=False,
    indent=2
))


# ------------------------------------------------------------
# Preflight Security Validation
# ------------------------------------------------------------

print("\n=== Preflight Security Validation ===")

try:
    validate_requests(llm_output["requests"])

except Exception as e:
    print("RESULT: DENIED")
    print(f"Reason: {e}")
    raise SystemExit(1)


print("\n=== Preflight Result ===")
print("All security checks passed.")
print("Proceeding to transactional tool execution.")


# ------------------------------------------------------------
# Transaction Snapshot
# ------------------------------------------------------------

transaction_snapshot = copy.deepcopy(candidates)

print("\n=== Transaction ===")
print("Snapshot created.")


# ------------------------------------------------------------
# Transactional Tool Execution
# ------------------------------------------------------------

try:
    print("\n=== Tool Execution ===")

    for index, request in enumerate(
        llm_output["requests"],
        start=1
    ):
        print(
            f"Executing request #{index}: "
            f"{request['action']}"
        )

        execute_tool(request)

        print("Tool execution succeeded.")

except Exception as e:
    print("Tool execution failed.")
    print(f"Reason: {e}")

    # --------------------------------------------------------
    # Rollback
    # --------------------------------------------------------

    print("\n=== ROLLBACK ===")
    print("Restoring previous resource state.")

    candidates = transaction_snapshot

    print("\nRESULT: ROLLED BACK")

    print("\n=== Resource After Rollback ===")
    print(json.dumps(
        candidates["candidate-001"],
        ensure_ascii=False,
        indent=2
    ))

    raise SystemExit(0)


# ------------------------------------------------------------
# Commit
# ------------------------------------------------------------

print("\n=== COMMIT ===")
print("All tool executions succeeded.")

print("\nRESULT: COMMITTED")

print("\n=== Resource After Commit ===")
print(json.dumps(
    candidates["candidate-001"],
    ensure_ascii=False,
    indent=2
))

