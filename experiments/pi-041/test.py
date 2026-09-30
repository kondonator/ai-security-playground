import json
import time


idempotency_records = {}
external_notifications = []


llm_output = {
    "action": "send_notification",
    "candidate_id": "candidate-001",
    "message": "Candidate updated successfully.",
    "idempotency_key": "operation-001",
}


def send_notification(request, simulate_failure=False):
    idempotency_key = request["idempotency_key"]

    print(f"Checking Idempotency Key: {idempotency_key}")

    record = idempotency_records.get(idempotency_key)

    # --------------------------------------------------
    # Existing record
    # --------------------------------------------------

    if record is not None:
        state = record["state"]

        print(f"Existing state: {state}")

        if state == "COMPLETED":
            print("Operation already completed.")

            return {
                "status": "already_completed",
                "idempotency_key": idempotency_key,
            }

        if state == "PROCESSING":
            print("Operation is marked PROCESSING.")
            print("Recovery check is required.")

            # 今回のモックでは、外部通知を確認して
            # 未実行なら再実行可能と判断する
            existing_notifications = [
                notification
                for notification in external_notifications
                if notification["idempotency_key"] == idempotency_key
            ]

            if existing_notifications:
                print(
                    "External operation already exists."
                )

                record["state"] = "COMPLETED"

                return {
                    "status": "recovered_as_completed",
                    "idempotency_key": idempotency_key,
                }

            print(
                "No external operation was found."
            )
            print(
                "Retrying the PROCESSING operation."
            )

    # --------------------------------------------------
    # Start / retry processing
    # --------------------------------------------------

    idempotency_records[idempotency_key] = {
        "state": "PROCESSING",
    }

    print("State changed to PROCESSING.")

    # --------------------------------------------------
    # Simulated failure
    # --------------------------------------------------

    if simulate_failure:
        raise RuntimeError(
            "Simulated process failure before external operation."
        )

    # --------------------------------------------------
    # External side effect
    # --------------------------------------------------

    notification = {
        "candidate_id": request["candidate_id"],
        "message": request["message"],
        "idempotency_key": idempotency_key,
    }

    external_notifications.append(notification)

    print("External system processed the notification.")

    # --------------------------------------------------
    # Mark completed
    # --------------------------------------------------

    idempotency_records[idempotency_key]["state"] = "COMPLETED"

    print("State changed to COMPLETED.")

    return {
        "status": "completed",
        "idempotency_key": idempotency_key,
    }


print("=== Simulated LLM Output ===")
print(json.dumps(llm_output, ensure_ascii=False, indent=2))


# ==================================================
# Case A
# ==================================================

print("\n========================================")
print("=== Case A: Successful Execution ===")
print("========================================")

result = send_notification(
    llm_output,
    simulate_failure=False,
)

print(
    "Result:",
    json.dumps(result, ensure_ascii=False),
)


# ==================================================
# Case B
# ==================================================

print("\n========================================")
print("=== Case B: Failure and Recovery ===")
print("========================================")

failure_request = {
    **llm_output,
    "idempotency_key": "operation-002",
}

try:
    send_notification(
        failure_request,
        simulate_failure=True,
    )

except RuntimeError as e:
    print("Process failure occurred.")
    print(f"Reason: {e}")


print("\n=== State After Failure ===")
print(
    json.dumps(
        idempotency_records,
        ensure_ascii=False,
        indent=2,
    )
)


# ==================================================
# Recovery / Retry
# ==================================================

print("\n=== Recovery / Retry ===")

retry_result = send_notification(
    failure_request,
    simulate_failure=False,
)

print(
    "Retry result:",
    json.dumps(
        retry_result,
        ensure_ascii=False,
    ),
)


# ==================================================
# Final State
# ==================================================

print("\n=== Final Idempotency Records ===")
print(
    json.dumps(
        idempotency_records,
        ensure_ascii=False,
        indent=2,
    )
)

print("\n=== External Notifications ===")
print(
    json.dumps(
        external_notifications,
        ensure_ascii=False,
        indent=2,
    )
)


print("\n=== Analysis ===")

case_a_state = idempotency_records["operation-001"]["state"]
case_b_state = idempotency_records["operation-002"]["state"]

case_b_notifications = [
    notification
    for notification in external_notifications
    if notification["idempotency_key"] == "operation-002"
]

if (
    case_a_state == "COMPLETED"
    and case_b_state == "COMPLETED"
    and len(case_b_notifications) == 1
):
    print("RESULT: STATEFUL RECOVERY")
    print(
        "Completed operations are distinguished from "
        "incomplete operations."
    )
    print(
        "The failed PROCESSING operation was recovered "
        "and executed once."
    )

else:
    print("RESULT: RECOVERY FAILED")

