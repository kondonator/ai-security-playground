import json
import threading
import time

external_notifications = []
processed_idempotency_keys = set()

llm_output = {
    "action": "send_notification",
    "candidate_id": "candidate-001",
    "message": "Candidate updated successfully.",
    "idempotency_key": "operation-001",
}


def send_notification(request, request_name):
    idempotency_key = request["idempotency_key"]

    print(f"[{request_name}] Checking Idempotency Key: {idempotency_key}")

    # Idempotency Keyのチェック
    if idempotency_key in processed_idempotency_keys:
        print(f"[{request_name}] Duplicate request detected.")
        return {
            "status": "already_processed",
            "idempotency_key": idempotency_key,
        }

    print(f"[{request_name}] Key is not registered.")

    # わざと待機してRace Conditionを発生しやすくする
    print(f"[{request_name}] Waiting before registering key...")
    time.sleep(0.1)

    # Idempotency Keyを登録
    processed_idempotency_keys.add(idempotency_key)

    print(f"[{request_name}] Idempotency Key registered.")

    # 外部副作用
    notification = {
        "candidate_id": request["candidate_id"],
        "message": request["message"],
        "idempotency_key": idempotency_key,
        "request": request_name,
    }

    external_notifications.append(notification)

    print(f"[{request_name}] External system processed the notification.")

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
    print("The concurrent duplicate request was prevented.")

elif len(external_notifications) > 1:
    print("RESULT: RACE CONDITION")
    print("Multiple concurrent requests passed the idempotency check.")
    print("The same logical operation was executed multiple times.")

else:
    print("RESULT: NO SIDE EFFECT")

