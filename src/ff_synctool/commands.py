import sqlite3


def describe_command(cmd_id):
    return {
        1: "Open URL",
        2: "Close tab",
    }.get(cmd_id, f"Unknown command {cmd_id}")


def show_commands(db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, device_id, command, url, time_requested, time_sent "
        "FROM remote_tab_commands ORDER BY time_requested DESC"
    )
    for row in cur.fetchall():
        print({
            "id": row[0],
            "device": row[1],
            "command": describe_command(row[2]),
            "url": row[3],
            "requested": row[4],
            "sent": row[5],
        })


def main():
    filename = "synced_tabs.sqlite3"
    show_commands(filename)
