import json


# ============================================================
# External System Mock
# ============================================================

external_notifications = []

# Idempotency keys already processed by the external system.
processed_idempotency_keys = set()


# ============================================================
# Simulated LLM Output
# ============================================================

llm_output = {
    "action": "send_notification",
    "candidate_id": "candidate-001",
    "message": "Candidate updated successfully.",
    "idempotency_key": "operation-001",
}


# ============================================================
# External Tool with Idempotency
# ============================================================

def send_notification(request, attempt):
    idempotency_key = request["idempotency_key"]

    print(f"Idempotency Key: {idempotency_key}")

    # --------------------------------------------------------
    # Duplicate detection
    # --------------------------------------------------------

    if idempotency_key in processed_idempotency_keys:
        print("Duplicate request detected.")
        print("External operation will not be executed again.")

        return {
            "status": "already_processed",
            "idempotency_key": idempotency_key,
        }

    # --------------------------------------------------------
    # First execution
    # --------------------------------------------------------

    processed_idempotency_keys.add(idempotency_key)

    notification = {
        "candidate_id": request["candidate_id"],
        "message": request["message"],
        "idempotency_key": idempotency_key,
        "attempt": attempt,
    }

    external_notifications.append(notification)

    print("External system processed the notification.")

    # --------------------------------------------------------
    # Simulate lost response
    # --------------------------------------------------------

    if attempt == 1:
        raise TimeoutError(
            "Response timeout after external processing."
        )

    print("Response received successfully.")

    return {
        "status": "processed",
        "idempotency_key": idempotency_key,
    }


# ============================================================
# Main
# ============================================================

print("=== Simulated LLM Output ===")
print(json.dumps(
    llm_output,
    ensure_ascii=False,
    indent=2
))


# ============================================================
# First Attempt
# ============================================================

print("\n=== Attempt #1 ===")

try:
    send_notification(
        llm_output,
        attempt=1
    )

except TimeoutError as e:
    print("Tool execution reported failure.")
    print(f"Reason: {e}")


# ============================================================
# Retry
# ============================================================

print("\n=== Retry ===")
print("Agent assumes the previous response was lost.")
print("Retrying the same logical operation.")


try:
    retry_result = send_notification(
        llm_output,
        attempt=2
    )

    print(
        "Retry result:",
        json.dumps(
            retry_result,
            ensure_ascii=False
        )
    )

except Exception as e:
    print("Retry failed.")
    print(f"Reason: {e}")


# ============================================================
# Result
# ============================================================

print("\n=== External Notifications ===")
print(json.dumps(
    external_notifications,
    ensure_ascii=False,
    indent=2
))

print("\n=== Processed Idempotency Keys ===")
print(json.dumps(
    sorted(processed_idempotency_keys),
    ensure_ascii=False,
    indent=2
))


# ============================================================
# Analysis
# ============================================================

print("\n=== Analysis ===")

if len(external_notifications) == 1:
    print("RESULT: IDEMPOTENT")
    print(
        "The retry was recognized as the same logical operation."
    )
    print(
        "The external side effect was executed only once."
    )

elif len(external_notifications) > 1:
    print("RESULT: DUPLICATE SIDE EFFECT")
    print(
        "The same logical operation was processed multiple times."
    )

else:
    print("RESULT: NO SIDE EFFECT")

