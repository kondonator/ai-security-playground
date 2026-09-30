import json


class ExternalNotificationSystem:
    """
    Mock external system with payload-aware idempotency.

    The same Idempotency Key must be used with the same request payload.
    A different payload with the same key is treated as a conflict.
    """

    def __init__(self):
        self.processed_operations = {}

    def send_notification(self, request):
        idempotency_key = request["idempotency_key"]

        print(
            f"[External System] Received request: "
            f"{idempotency_key}"
        )

        existing = self.processed_operations.get(
            idempotency_key
        )

        if existing is not None:
            existing_payload = {
                "candidate_id": existing["candidate_id"],
                "message": existing["message"],
            }

            current_payload = {
                "candidate_id": request["candidate_id"],
                "message": request["message"],
            }

            if existing_payload != current_payload:
                print(
                    "[External System] "
                    "Idempotency Key conflict detected."
                )

                return {
                    "status": "idempotency_conflict",
                    "idempotency_key": idempotency_key,
                    "reason": (
                        "The same Idempotency Key was used "
                        "with a different request payload."
                    ),
                }

            print(
                "[External System] "
                "Duplicate Idempotency Key detected "
                "with identical payload."
            )

            return {
                "status": "already_processed",
                "idempotency_key": idempotency_key,
                "result": existing,
            }

        notification = {
            "candidate_id": request["candidate_id"],
            "message": request["message"],
            "idempotency_key": idempotency_key,
        }

        self.processed_operations[idempotency_key] = notification

        print(
            "[External System] "
            "Notification processed."
        )

        return {
            "status": "processed",
            "idempotency_key": idempotency_key,
            "result": notification,
        }


external_system = ExternalNotificationSystem()


request_1 = {
    "action": "send_notification",
    "candidate_id": "candidate-001",
    "message": "Candidate updated successfully.",
    "idempotency_key": "operation-001",
}


request_2 = {
    "action": "send_notification",
    "candidate_id": "candidate-001",
    "message": "Candidate update completed successfully.",
    "idempotency_key": "operation-001",
}


print("=== Request #1 ===")
print(json.dumps(request_1, indent=2, ensure_ascii=False))


print("\n========================================")
print("=== Attempt #1 ===")
print("========================================")

response_1 = external_system.send_notification(request_1)

print(
    "External response:",
    json.dumps(response_1, ensure_ascii=False)
)


print("\n========================================")
print("=== Attempt #2: Modified Retry ===")
print("========================================")

print("Request payload was changed before retry.")

print(json.dumps(request_2, indent=2, ensure_ascii=False))

response_2 = external_system.send_notification(request_2)

print(
    "External response:",
    json.dumps(response_2, ensure_ascii=False)
)


print("\n========================================")
print("=== Final External System State ===")
print("========================================")

print(
    json.dumps(
        external_system.processed_operations,
        indent=2,
        ensure_ascii=False,
    )
)


print("\n=== Analysis ===")

operation_count = len(
    external_system.processed_operations
)

if (
    operation_count == 1
    and response_2["status"] == "idempotency_conflict"
):
    print("RESULT: IDEMPOTENCY CONFLICT DETECTED")

    print(
        "The same Idempotency Key was rejected because "
        "the retry request had a different payload."
    )

elif operation_count > 1:
    print("RESULT: DUPLICATE SIDE EFFECT")

    print(
        "The same Idempotency Key resulted in "
        "multiple external operations."
    )

elif response_2["status"] == "already_processed":
    print("RESULT: UNEXPECTED ACCEPTANCE")

    print(
        "The modified request was treated as the "
        "same operation."
    )

else:
    print("RESULT: UNEXPECTED STATE")

