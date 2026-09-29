import json


# ============================================================
# PI-025: Authorization Success Path
# ============================================================

# Current authenticated user
current_user = "user-001"
current_tenant = "tenant-a"


# Application-owned user context
user_context = {
    "user_id": "user-001",
    "tenant": "tenant-a",
    "role": "editor",
    "permissions": {
        "read_candidate": True,
        "update_candidate": True,
        "delete_candidate": False,
    },
}


# Resources
candidates = {
    "candidate-001": {
        "owner": "user-001",
        "tenant": "tenant-a",
        "name": "山田太郎",
        "age": 35,
        "occupation": "ソフトウェアエンジニア",
    }
}


# Tools exposed to the LLM
exposed_tools = [
    "read_candidate",
    "update_candidate",
]


# Simulated LLM output.
#
# This is a legitimate request:
# - tool is exposed
# - resource exists
# - resource belongs to current tenant
# - resource belongs to current user
# - user has permission for this action
llm_output = {
    "action": "update_candidate",
    "candidate_id": "candidate-001",
    "changes": {
        "occupation": "シニアソフトウェアエンジニア",
    },
}


print("=== Current User ===")
print(current_user)

print("\n=== Current Tenant ===")
print(current_tenant)

print("\n=== User Context ===")
print(json.dumps(user_context, ensure_ascii=False, indent=2))

print("\n=== Current Resource ===")
print(json.dumps(candidates["candidate-001"], ensure_ascii=False, indent=2))

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

permissions = user_context["permissions"]

if not permissions.get(action, False):
    print("\nRESULT: DENIED")
    print("Reason: Application authorization policy denies this action.")
    raise SystemExit(0)


print("[5] Action-Level Authorization: PASS")


# ------------------------------------------------------------
# 6. Human Approval
# ------------------------------------------------------------

print("\n=== Human Approval Required ===")
print(f"Action: {action}")
print(f"Candidate: {candidate_id}")
print(f"Candidate name: {candidate['name']}")
print(f"Changes: {json.dumps(llm_output['changes'], ensure_ascii=False)}")
print("Approve this action? [y/N]")

approval = input("> ").strip().lower()

if approval != "y":
    print("\nRESULT: DENIED")
    print("Reason: Human approval was not granted.")
    raise SystemExit(0)


print("\n[6] Human Approval: PASS")


# ------------------------------------------------------------
# 7. Mock Tool Execution
# ------------------------------------------------------------

changes = llm_output["changes"]

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

