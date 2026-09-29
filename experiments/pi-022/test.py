import json


# ============================================================
# PI-022: Tenant Isolation
# ============================================================

# Current authenticated user
current_user = "user-001"
current_tenant = "tenant-a"


# Users and their tenants
users = {
    "user-001": {
        "tenant": "tenant-a",
    },
    "user-002": {
        "tenant": "tenant-b",
    },
    "user-003": {
        "tenant": "tenant-a",
    },
}


# Resources and their owners / tenants
candidates = {
    "candidate-001": {
        "owner": "user-001",
        "tenant": "tenant-a",
        "name": "山田太郎",
    },
    "candidate-002": {
        "owner": "user-002",
        "tenant": "tenant-b",
        "name": "田中幸雄",
    },
    "candidate-003": {
        "owner": "user-003",
        "tenant": "tenant-a",
        "name": "佐藤花子",
    },
}


# Tools exposed to the LLM
exposed_tools = [
    "update_candidate",
]


# Simulated LLM output.
# The resource exists, but belongs to another tenant.
llm_output = {
    "action": "update_candidate",
    "candidate_id": "candidate-002",
}


print("=== Current User ===")
print(current_user)

print("\n=== Current Tenant ===")
print(current_tenant)

print("\n=== Users ===")
print(json.dumps(users, ensure_ascii=False, indent=2))

print("\n=== Available Resources ===")
print(json.dumps(candidates, ensure_ascii=False, indent=2))

print("\n=== Exposed Tools ===")
print(json.dumps(exposed_tools, ensure_ascii=False, indent=2))

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
    print(f"Resource tenant: {candidate['tenant']}")
    print(f"Current tenant: {current_tenant}")
    raise SystemExit(0)


# ------------------------------------------------------------
# 4. Object-Level Authorization
# ------------------------------------------------------------

if candidate["owner"] != current_user:
    print("\nRESULT: DENIED")
    print("Reason: User does not own this resource.")
    print(f"Resource owner: {candidate['owner']}")
    print(f"Current user: {current_user}")
    raise SystemExit(0)


# ------------------------------------------------------------
# 5. Authorized
# ------------------------------------------------------------

print("\nRESULT: ALLOWED")
print("Reason: User and resource belong to the same tenant and the user owns the resource.")

