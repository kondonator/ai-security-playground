import json


class ExternalNotificationSystem:
    """
    Mock external system.

    The external system itself recognizes the Idempotency Key
    and prevents duplicate execution.
    """

    def __init__(self):
        self.processed_operations = {}

    def send_notification(self, request):
        idempotency_key = request["idempotency_key"]

        print(
            f"[External System] Received request: "
            f"{idempotency_key}"
        )

        if idempotency_key in self.processed_operations:
            print(
                "[External System] "
                "Duplicate Idempotency Key detected."
            )

            return {
                "status": "already_processed",
                "idempotency_key": idempotency_key,
                "result": self.processed_operations[
                    idempotency_key
                ],
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


llm_output = {
    "action": "send_notification",
    "candidate_id": "candidate-001",
    "message": "Candidate updated successfully.",
    "idempotency_key": "operation-001",
}


print("=== Simulated LLM Output ===")
print(json.dumps(llm_output, indent=2, ensure_ascii=False))


print("\n========================================")
print("=== Attempt #1 ===")
print("========================================")

response_1 = external_system.send_notification(
    llm_output
)

print(
    "External response:",
    json.dumps(response_1, ensure_ascii=False)
)

print(
    "Simulating response timeout..."
)


print("\n========================================")
print("=== Attempt #2: Retry ===")
print("========================================")

response_2 = external_system.send_notification(
    llm_output
)

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

response_2_status = response_2["status"]


if operation_count == 1 and response_2_status == "already_processed":
    print("RESULT: EXTERNAL IDEMPOTENCY")

    print(
        "The external system recognized the repeated "
        "Idempotency Key and prevented duplicate execution."
    )

elif operation_count > 1:
    print("RESULT: DUPLICATE SIDE EFFECT")

    print(
        "The external system executed the same logical "
        "operation more than once."
    )

else:
    print("RESULT: UNEXPECTED STATE")

