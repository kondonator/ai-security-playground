import json


# ============================================================
# PI-023: Action-Level Authorization
# ============================================================

# Current authenticated user
current_user = "user-001"
current_tenant = "tenant-a"


# Resource
candidates = {
    "candidate-001": {
        "owner": "user-001",
        "tenant": "tenant-a",
        "name": "山田太郎",
    }
}


# Tools exposed to the LLM
exposed_tools = [
    "read_candidate",
    "update_candidate",
    "delete_candidate",
]


# Application-owned authorization policy.
#
# The LLM does NOT determine these permissions.
authorization_policy = {
    "user-001": {
        "read_candidate": True,
        "update_candidate": True,
        "delete_candidate": False,
    }
}


# Simulated LLM output.
#
# The user has access to candidate-001,
# but is not authorized to delete it.
llm_output = {
    "action": "delete_candidate",
    "candidate_id": "candidate-001",
}


print("=== Current User ===")
print(current_user)

print("\n=== Current Tenant ===")
print(current_tenant)

print("\n=== Available Resources ===")
print(json.dumps(candidates, ensure_ascii=False, indent=2))

print("\n=== Exposed Tools ===")
print(json.dumps(exposed_tools, ensure_ascii=False, indent=2))

print("\n=== Application Authorization Policy ===")
print(
    json.dumps(
        authorization_policy,
        ensure_ascii=False,
        indent=2,
    )
)

print("\n=== Simulated LLM Output ===")
print(json.dumps(llm_output, ensure_ascii=False, indent=2))


# ------------------------------------------------------------
# 1. Tool Allowlist
# ------------------------------------------------------------

action = llm_output.get("action")

if action not in exposed_tools:
    print("\nRESULT: DENIED")
    print("Reason: Requested tool is not exposed to the LLM.")
    raise SystemExit(0)


# ------------------------------------------------------------
# 2. Resource Existence Check
# ------------------------------------------------------------

candidate_id = llm_output.get("candidate_id")

if candidate_id not in candidates:
    print("\nRESULT: DENIED")
    print("Reason: Requested resource does not exist.")
    raise SystemExit(0)


# ------------------------------------------------------------
# 3. Tenant Isolation
# ------------------------------------------------------------

candidate = candidates[candidate_id]

if candidate["tenant"] != current_tenant:
    print("\nRESULT: DENIED")
    print("Reason: Resource belongs to another tenant.")
    raise SystemExit(0)


# ------------------------------------------------------------
# 4. Object-Level Authorization
# ------------------------------------------------------------

if candidate["owner"] != current_user:
    print("\nRESULT: DENIED")
    print("Reason: User does not own this resource.")
    raise SystemExit(0)


# ------------------------------------------------------------
# 5. Action-Level Authorization
# ------------------------------------------------------------

user_policy = authorization_policy.get(current_user, {})

if not user_policy.get(action, False):
    print("\nRESULT: DENIED")
    print("Reason: User is not authorized for this action.")
    print(f"Requested action: {action}")
    raise SystemExit(0)


# ------------------------------------------------------------
# 6. Authorized
# ------------------------------------------------------------

print("\nRESULT: ALLOWED")
print("Reason: User is authorized for this action and resource.")

