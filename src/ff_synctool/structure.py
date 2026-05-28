#!/usr/bin/env python3
import argparse
import sqlite3


def show_db_structure(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get list of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"\n\U0001f4e6 Tables in {db_path}:\n" + "-" * 40)
    for table in tables:
        print(f"\n\U0001f5c2️ Table: {table}")
        print("  Columns:")
        cursor.execute(f"PRAGMA table_info({table})")
        for col in cursor.fetchall():
            col_id, name, dtype, notnull, default, pk = col
            print(f"    - {name} ({dtype}){' PRIMARY KEY' if pk else ''}")

        print("  Indexes:")
        cursor.execute(f"PRAGMA index_list({table})")
        for idx in cursor.fetchall():
            print(f"    - {idx[1]} ({'UNIQUE' if idx[2] else 'non-unique'})")

        print("  Foreign keys:")
        cursor.execute(f"PRAGMA foreign_key_list({table})")
        for fk in cursor.fetchall():
            print(f"    - {fk[3]} → {fk[4]} ({fk[2]})")

    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect structure of a Firefox SQLite DB")
    parser.add_argument("db", help="Path to SQLite file (e.g., synced-tabs.sqlite3)")
    args = parser.parse_args()
    show_db_structure(args.db)
