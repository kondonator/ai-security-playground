import json


# ============================================================
# PI-028: Mass Assignment Protection
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
#
# Only these fields may be modified through update_candidate.

allowed_update_fields = {
    "age",
    "occupation",
}


# Tools exposed to the LLM
exposed_tools = [
    "update_candidate",
]


# ------------------------------------------------------------
# Simulated LLM output
# ------------------------------------------------------------
#
# occupation is allowed.
# role and tenant are NOT allowed.
#
# The application will reject the entire request rather than
# partially applying the allowed field.

llm_output = {
    "action": "update_candidate",
    "candidate_id": "candidate-001",
    "changes": {
        "occupation": "シニアソフトウェアエンジニア",
        "role": "admin",
        "tenant": "tenant-b",
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

print("\n=== Allowed Update Fields ===")
print(
    json.dumps(
        sorted(allowed_update_fields),
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
    print(
        "No fields were modified."
    )
    raise SystemExit(0)

print("[6] Field-Level Validation: PASS")


# ------------------------------------------------------------
# 7. Mock Tool Execution
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

