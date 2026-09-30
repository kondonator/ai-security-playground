import json


idempotency_records = {}
external_notifications = []


llm_output = {
    "action": "send_notification",
    "candidate_id": "candidate-001",
    "message": "Candidate updated successfully.",
    "idempotency_key": "operation-001",
}


def send_notification(request, simulate_failure_after_external=False):
    idempotency_key = request["idempotency_key"]

    print(f"Checking Idempotency Key: {idempotency_key}")

    record = idempotency_records.get(idempotency_key)

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

            existing_notifications = [
                notification
                for notification in external_notifications
                if notification["idempotency_key"] == idempotency_key
            ]

            if existing_notifications:
                print("External operation already exists.")
                print("Recovering state to COMPLETED.")

                record["state"] = "COMPLETED"

                return {
                    "status": "recovered_as_completed",
                    "idempotency_key": idempotency_key,
                }

            print("No external operation was found.")
            print("Retrying the PROCESSING operation.")

    idempotency_records[idempotency_key] = {
        "state": "PROCESSING"
    }

    print("State changed to PROCESSING.")

    notification = {
        "candidate_id": request["candidate_id"],
        "message": request["message"],
        "idempotency_key": idempotency_key,
    }

    external_notifications.append(notification)

    print("External system processed the notification.")

    if simulate_failure_after_external:
        raise RuntimeError(
            "Simulated process failure after external operation "
            "but before COMPLETED state update."
        )

    idempotency_records[idempotency_key]["state"] = "COMPLETED"

    print("State changed to COMPLETED.")

    return {
        "status": "completed",
        "idempotency_key": idempotency_key,
    }


print("=== Simulated LLM Output ===")
print(json.dumps(llm_output, indent=2, ensure_ascii=False))

print("\n========================================")
print("=== Initial Execution ===")
print("========================================")

try:
    result = send_notification(
        llm_output,
        simulate_failure_after_external=True,
    )

    print(f"Result: {json.dumps(result)}")

except RuntimeError as e:
    print("Process failure occurred.")
    print(f"Reason: {e}")


print("\n=== State After Failure ===")
print(json.dumps(idempotency_records, indent=2, ensure_ascii=False))

print("\n=== External Notifications After Failure ===")
print(json.dumps(external_notifications, indent=2, ensure_ascii=False))


print("\n========================================")
print("=== Recovery / Retry ===")
print("========================================")

try:
    retry_result = send_notification(llm_output)

    print(f"Retry result: {json.dumps(retry_result)}")

except RuntimeError as e:
    print("Retry failed.")
    print(f"Reason: {e}")


print("\n=== Final Idempotency Records ===")
print(json.dumps(idempotency_records, indent=2, ensure_ascii=False))

print("\n=== Final External Notifications ===")
print(json.dumps(external_notifications, indent=2, ensure_ascii=False))


print("\n=== Analysis ===")

notification_count = sum(
    1
    for notification in external_notifications
    if notification["idempotency_key"]
    == llm_output["idempotency_key"]
)

final_state = idempotency_records[
    llm_output["idempotency_key"]
]["state"]


if notification_count == 1 and final_state == "COMPLETED":
    print("RESULT: SAFE RECOVERY")
    print(
        "The external operation was detected as already completed "
        "and was not executed again."
    )

elif notification_count > 1:
    print("RESULT: DUPLICATE SIDE EFFECT")
    print(
        "The external operation was executed multiple times "
        "for the same Idempotency Key."
    )

else:
    print("RESULT: UNEXPECTED STATE")

