import json


# ============================================================
# PI-021: Object-Level Authorization / Ownership Check
# ============================================================

# Current authenticated user
current_user = "user-001"

# Resources owned by users
candidates = {
    "candidate-001": {
        "owner": "user-001",
        "name": "山田太郎",
    },
    "candidate-002": {
        "owner": "user-002",
        "name": "田中幸雄",
    },
}

# Tools exposed to the LLM
exposed_tools = [
    "update_candidate",
]

# Simulated LLM output.
# The resource exists, but belongs to another user.
llm_output = {
    "action": "update_candidate",
    "candidate_id": "candidate-002",
}


print("=== Current User ===")
print(current_user)

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
# 3. Object-Level Authorization
# ------------------------------------------------------------

candidate = candidates[candidate_id]

if candidate["owner"] != current_user:
    print("\nRESULT: DENIED")
    print("Reason: User does not own or have access to this resource.")
    print(f"Resource owner: {candidate['owner']}")
    print(f"Current user: {current_user}")
    raise SystemExit(0)


# ------------------------------------------------------------
# 4. Authorized
# ------------------------------------------------------------

print("\nRESULT: ALLOWED")
print("Reason: User is authorized to access this resource.")

