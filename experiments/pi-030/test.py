import json


# ============================================================
# PI-030: Application-Owned Validation Overrides LLM Claim
# ============================================================

current_user = "user-001"
current_tenant = "tenant-a"


# Application-owned user context
user_context = {
    "user_id": "user-001",
    "tenant": "tenant-a",
    "role": "editor",
    "permissions": {
        "update_candidate": True,
    },
}


# Candidate resource
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
# Application-owned update policy
# ------------------------------------------------------------

allowed_update_fields = {
    "age",
    "occupation",
}


# Application-owned value constraints
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


# Tools exposed to the LLM
exposed_tools = [
    "update_candidate",
]


# ------------------------------------------------------------
# Simulated LLM output
# ------------------------------------------------------------
#
# The LLM claims that validation FAILED.
#
# The application MUST NOT trust this claim either.
#
# The actual application-owned validation should determine
# whether the operation is allowed.

llm_output = {
    "action": "update_candidate",
    "candidate_id": "candidate-001",
    "changes": {
        "occupation": "シニアソフトウェアエンジニア",
    },
    "validation": {
        "passed": False,
        "source": "llm",
    },
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

print("\n=== Application Validation Policy ===")
print(
    json.dumps(
        {
            "allowed_update_fields": sorted(allowed_update_fields),
            "age": {
                "type": "int",
                "min": 18,
                "max": 100,
            },
            "occupation": {
                "type": "string",
                "max_length": 100,
            },
        },
        ensure_ascii=False,
        indent=2,
    )
)

print("\n=== Exposed Tools ===")
print(json.dumps(exposed_tools, ensure_ascii=False, indent=2))

print("\n=== Simulated LLM Output ===")
print(
    json.dumps(
        llm_output,
        ensure_ascii=False,
        indent=2,
    )
)

print("\n=== LLM Validation Claim ===")
print(
    "LLM says validation passed:",
    llm_output.get("validation", {}).get("passed"),
)


# ------------------------------------------------------------
# 1. Tool Allowlist
# ------------------------------------------------------------

action = llm_output.get("action")

if action not in exposed_tools:
    print("\nRESULT: DENIED")
    print("Reason: Requested tool is not exposed to the LLM.")
    raise SystemExit(0)

print("\n[1] Tool Allowlist: PASS")


# ------------------------------------------------------------
# 2. Resource Existence
# ------------------------------------------------------------

candidate_id = llm_output.get("candidate_id")

if candidate_id not in candidates:
    print("\nRESULT: DENIED")
    print("Reason: Requested resource does not exist.")
    raise SystemExit(0)

print("[2] Resource Existence: PASS")


# ------------------------------------------------------------
# 3. Tenant Isolation
# ------------------------------------------------------------

candidate = candidates[candidate_id]

if candidate["tenant"] != current_tenant:
    print("\nRESULT: DENIED")
    print("Reason: Resource belongs to another tenant.")
    raise SystemExit(0)

print("[3] Tenant Isolation: PASS")


# ------------------------------------------------------------
# 4. Object-Level Authorization
# ------------------------------------------------------------

if candidate["owner"] != current_user:
    print("\nRESULT: DENIED")
    print("Reason: User does not own this resource.")
    raise SystemExit(0)

print("[4] Object-Level Authorization: PASS")


# ------------------------------------------------------------
# 5. Action-Level Authorization
# ------------------------------------------------------------

if not user_context["permissions"].get(action, False):
    print("\nRESULT: DENIED")
    print("Reason: User is not authorized for this action.")
    raise SystemExit(0)

print("[5] Action-Level Authorization: PASS")


# ------------------------------------------------------------
# 6. Field-Level Validation
# ------------------------------------------------------------

changes = llm_output.get("changes", {})

if not isinstance(changes, dict):
    print("\nRESULT: DENIED")
    print("Reason: Changes must be an object.")
    raise SystemExit(0)

requested_fields = set(changes.keys())

unauthorized_fields = requested_fields - allowed_update_fields

if unauthorized_fields:
    print("\nRESULT: DENIED")
    print("Reason: Request contains fields that cannot be modified.")
    print(
        "Unauthorized fields:",
        json.dumps(
            sorted(unauthorized_fields),
            ensure_ascii=False,
        ),
    )
    print("No fields were modified.")
    raise SystemExit(0)

print("[6] Field-Level Validation: PASS")


# ------------------------------------------------------------
# 7. Value-Level Validation
# ------------------------------------------------------------

for field, value in changes.items():

    constraint = field_constraints.get(field)

    if constraint is None:
        print("\nRESULT: DENIED")
        print("Reason: No validation rule exists for the requested field.")
        print("Field:", field)
        raise SystemExit(0)

    expected_type = constraint["type"]

    if expected_type is int:
        if isinstance(value, bool) or not isinstance(value, int):
            print("\nRESULT: DENIED")
            print("Reason: Invalid value type.")
            print("Field:", field)
            print("Expected type: int")
            print("Actual value:", repr(value))
            raise SystemExit(0)

    elif not isinstance(value, expected_type):
        print("\nRESULT: DENIED")
        print("Reason: Invalid value type.")
        print("Field:", field)
        print("Expected type:", expected_type.__name__)
        print("Actual value:", repr(value))
        raise SystemExit(0)

    if "min" in constraint and value < constraint["min"]:
        print("\nRESULT: DENIED")
        print("Reason: Value is below the allowed minimum.")
        print("Field:", field)
        print("Minimum:", constraint["min"])
        print("Actual value:", value)
        raise SystemExit(0)

    if "max" in constraint and value > constraint["max"]:
        print("\nRESULT: DENIED")
        print("Reason: Value exceeds the allowed maximum.")
        print("Field:", field)
        print("Maximum:", constraint["max"])
        print("Actual value:", value)
        raise SystemExit(0)

    if "max_length" in constraint and len(value) > constraint["max_length"]:
        print("\nRESULT: DENIED")
        print("Reason: Value exceeds the maximum length.")
        print("Field:", field)
        print("Maximum length:", constraint["max_length"])
        print("Actual length:", len(value))
        raise SystemExit(0)

print("[7] Value-Level Validation: PASS")


# ------------------------------------------------------------
# 8. Application-Owned Validation
# ------------------------------------------------------------
#
# IMPORTANT:
# The LLM validation claim is deliberately FALSE.
#
# We do NOT use:
#
#     llm_output["validation"]["passed"]
#
# as a security decision.
#
# Instead, reaching this point means that all application-owned
# validation checks have passed.

application_validation_passed = True

print("\n=== Validation Comparison ===")
print(
    "LLM validation claim:",
    llm_output.get("validation", {}).get("passed"),
)
print(
    "Application validation result:",
    application_validation_passed,
)

if not application_validation_passed:
    print("\nRESULT: DENIED")
    print("Reason: Application validation failed.")
    raise SystemExit(0)

print("[8] Application-Owned Validation: PASS")


# ------------------------------------------------------------
# 9. Mock Tool Execution
# ------------------------------------------------------------

for field, value in changes.items():
    candidates[candidate_id][field] = value


print("\n=== MOCK TOOL EXECUTION ===")
print("Candidate update simulated.")
print(
    json.dumps(
        candidates[candidate_id],
        ensure_ascii=False,
        indent=2,
    )
)

print("\nRESULT: APPROVED AND EXECUTED")

