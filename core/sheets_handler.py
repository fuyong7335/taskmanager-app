def add_task(due_date: str, due_time: str, task: str, source: str = "LINE") -> int | str:
    ws = ws_tasks()
    rows = ws.get_all_records()

    # ★ダブルブッキングチェック
    for r in rows:
        if r.get("date") == due_date and r.get("time") == due_time and r.get("status") != "DONE":
            print("DEBUG: duplicate detected", due_date, due_time, r.get("id"))
            return f"W:{r.get('id')}"  # ←ここでWを返す

    tid = next_id(ws)
    ws.append_row([
        tid, due_date, due_time, task.strip(),
        "OPEN", now_str(), "", source
    ])
    print("DEBUG: task added", tid, due_date, due_time)
    return tid
