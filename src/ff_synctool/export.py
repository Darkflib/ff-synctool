#!/usr/bin/env python3
import json
import sqlite3

# sqlite> PRAGMA table_info(tabs);
# 0|guid|TEXT|1||1
# 1|record|TEXT|1||0
# 2|last_modified|INTEGER|1||0


def load_synced_tabs(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT guid, record, last_modified FROM tabs")
    for row in cur.fetchall():
        yield {
            "guid": row[0],
            "record": row[1],
            "last_modified": row[2]
        }


def main():
    import argparse
    p = argparse.ArgumentParser(description="Export Firefox synced tabs from SQLite")
    p.add_argument("db", help="Path to synced-tabs.sqlite3")
    p.add_argument("--json", help="Output JSON file", default="synced_tabs.json")
    args = p.parse_args()

    tabs = list(load_synced_tabs(args.db))
    for tab in tabs:
        with open(f"tab_{tab['guid']}.json", "w", encoding="utf-8") as tab_fp:
            # Parse the escaped JSON string into a Python object and then dump it
            record_data = json.loads(tab["record"])
            json.dump(record_data, tab_fp, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
