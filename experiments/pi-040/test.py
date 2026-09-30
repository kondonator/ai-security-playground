import json

processed_idempotency_keys = set()
external_notifications = []

llm_output = {
    "action": "send_notification",
    "candidate_id": "candidate-001",
    "message": "Candidate updated successfully.",
    "idempotency_key": "operation-001",
}


def send_notification(request, simulate_crash=False):
    idempotency_key = request["idempotency_key"]

    print(f"Checking Idempotency Key: {idempotency_key}")

    if idempotency_key in processed_idempotency_keys:
        print("Duplicate request detected.")
        print("External operation will not be executed.")

        return {
            "status": "already_processed",
            "idempotency_key": idempotency_key,
        }

    print("Key is not registered.")

    # Idempotency Keyを登録
    processed_idempotency_keys.add(idempotency_key)

    print("Idempotency Key registered.")

    # 外部処理前の障害をシミュレート
    if simulate_crash:
        raise RuntimeError(
            "Simulated process failure before external operation."
        )

    # 外部副作用
    notification = {
        "candidate_id": request["candidate_id"],
        "message": request["message"],
        "idempotency_key": idempotency_key,
    }

    external_notifications.append(notification)

    print("External system processed the notification.")

    return {
        "status": "processed",
        "idempotency_key": idempotency_key,
    }


print("=== Simulated LLM Output ===")
print(json.dumps(llm_output, ensure_ascii=False, indent=2))


# --------------------------------------------------
# Attempt #1
# --------------------------------------------------

print("\n=== Attempt #1 ===")

try:
    send_notification(
        llm_output,
        simulate_crash=True,
    )
except RuntimeError as e:
    print("Process failure occurred.")
    print(f"Reason: {e}")


print("\n=== State After Failure ===")

print("Processed Idempotency Keys:")
print(
    json.dumps(
        sorted(processed_idempotency_keys),
        ensure_ascii=False,
        indent=2,
    )
)

print("\nExternal Notifications:")
print(
    json.dumps(
        external_notifications,
        ensure_ascii=False,
        indent=2,
    )
)


# --------------------------------------------------
# Retry
# --------------------------------------------------

print("\n=== Retry ===")

print("Agent assumes the previous operation may have failed.")
print("Retrying the same logical operation.")

retry_result = send_notification(
    llm_output,
    simulate_crash=False,
)

print(
    "Retry result:",
    json.dumps(
        retry_result,
        ensure_ascii=False,
    ),
)


# --------------------------------------------------
# Final state
# --------------------------------------------------

print("\n=== Final State ===")

print("Processed Idempotency Keys:")
print(
    json.dumps(
        sorted(processed_idempotency_keys),
        ensure_ascii=False,
        indent=2,
    )
)

print("\nExternal Notifications:")
print(
    json.dumps(
        external_notifications,
        ensure_ascii=False,
        indent=2,
    )
)


print("\n=== Analysis ===")

if len(external_notifications) == 1:
    print("RESULT: RECOVERED")
    print(
        "The failed attempt was retried and "
        "the external operation was eventually executed."
    )

elif len(external_notifications) == 0:
    print("RESULT: STUCK")
    print(
        "The idempotency key prevented retry, "
        "but the external operation was never executed."
    )

else:
    print("RESULT: DUPLICATE SIDE EFFECT")
    print(
        "The same logical operation was executed "
        "multiple times."
    )

