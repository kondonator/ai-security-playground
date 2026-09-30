import json


# ============================================================
# External System Mock
# ============================================================

external_notifications = []


# ============================================================
# Simulated LLM Output
# ============================================================

llm_output = {
    "action": "send_notification",
    "candidate_id": "candidate-001",
    "message": "Candidate updated successfully.",
}


# ============================================================
# External Tool
# ============================================================

def send_notification(request, attempt):
    """
    Simulate an external notification service.

    Attempt #1:
        External system accepts the request and records the
        notification, but the response is lost.

    Attempt #2:
        The same request is sent again and is processed again.

    No idempotency protection is implemented.
    """

    notification = {
        "candidate_id": request["candidate_id"],
        "message": request["message"],
        "attempt": attempt,
    }

    # --------------------------------------------------------
    # External system processes the request.
    # --------------------------------------------------------

    external_notifications.append(notification)

    print("External system processed the notification.")

    # --------------------------------------------------------
    # Simulate lost response.
    # --------------------------------------------------------

    if attempt == 1:
        raise TimeoutError(
            "Response timeout after external processing."
        )

    print("Response received successfully.")


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
print("Agent assumes the previous request failed.")
print("Retrying the same operation.")


try:
    send_notification(
        llm_output,
        attempt=2
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

print("\n=== Analysis ===")

if len(external_notifications) == 2:
    print("RESULT: DUPLICATE SIDE EFFECT")
    print(
        "The same logical operation was processed twice."
    )
else:
    print("RESULT: NO DUPLICATE")

