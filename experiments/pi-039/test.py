import json
import threading
import time

external_notifications = []
processed_idempotency_keys = set()

# Idempotency Keyの確認と登録を保護するLock
idempotency_lock = threading.Lock()

llm_output = {
    "action": "send_notification",
    "candidate_id": "candidate-001",
    "message": "Candidate updated successfully.",
    "idempotency_key": "operation-001",
}


def send_notification(request, request_name):
    idempotency_key = request["idempotency_key"]

    print(f"[{request_name}] Waiting for idempotency lock...")

    with idempotency_lock:
        print(f"[{request_name}] Lock acquired.")
        print(
            f"[{request_name}] Checking Idempotency Key: "
            f"{idempotency_key}"
        )

        if idempotency_key in processed_idempotency_keys:
            print(f"[{request_name}] Duplicate request detected.")
            return {
                "status": "already_processed",
                "idempotency_key": idempotency_key,
            }

        print(f"[{request_name}] Key is not registered.")

        # Lockを保持したままKeyを登録する
        processed_idempotency_keys.add(idempotency_key)

        print(f"[{request_name}] Idempotency Key registered.")

    # Lockの外で外部処理を実行する
    print(f"[{request_name}] Lock released.")
    print(f"[{request_name}] Executing external operation...")

    time.sleep(0.1)

    notification = {
        "candidate_id": request["candidate_id"],
        "message": request["message"],
        "idempotency_key": idempotency_key,
        "request": request_name,
    }

    external_notifications.append(notification)

    print(
        f"[{request_name}] "
        "External system processed the notification."
    )

    return {
        "status": "processed",
        "idempotency_key": idempotency_key,
    }


print("=== Simulated LLM Output ===")
print(json.dumps(llm_output, ensure_ascii=False, indent=2))

print("\n=== Concurrent Requests ===")

thread_a = threading.Thread(
    target=send_notification,
    args=(llm_output, "Request A"),
)

thread_b = threading.Thread(
    target=send_notification,
    args=(llm_output, "Request B"),
)

thread_a.start()
thread_b.start()

thread_a.join()
thread_b.join()

print("\n=== External Notifications ===")
print(json.dumps(external_notifications, ensure_ascii=False, indent=2))

print("\n=== Processed Idempotency Keys ===")
print(
    json.dumps(
        sorted(processed_idempotency_keys),
        ensure_ascii=False,
        indent=2,
    )
)

print("\n=== Analysis ===")

if len(external_notifications) == 1:
    print("RESULT: IDEMPOTENT")
    print(
        "The idempotency check and registration "
        "were protected by a lock."
    )
    print(
        "The concurrent duplicate request "
        "was prevented."
    )

elif len(external_notifications) > 1:
    print("RESULT: RACE CONDITION")
    print(
        "Multiple concurrent requests "
        "executed the same operation."
    )

else:
    print("RESULT: NO SIDE EFFECT")

