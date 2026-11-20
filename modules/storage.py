"""Tiny SQLite persistence layer for demo shelter and hazard records."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "evacuation_data.db"


def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS shelters (
            name TEXT PRIMARY KEY, node TEXT NOT NULL, capacity INTEGER NOT NULL,
            available INTEGER NOT NULL DEFAULT 1)""")
        connection.execute("""CREATE TABLE IF NOT EXISTS road_conditions (
            edge_key TEXT PRIMARY KEY, hazard INTEGER NOT NULL DEFAULT 0,
            traffic INTEGER NOT NULL DEFAULT 0, blocked INTEGER NOT NULL DEFAULT 0)""")


def save_shelters(shelters):
    initialize_database()
    with sqlite3.connect(DB_PATH) as connection:
        connection.executemany(
            "INSERT OR REPLACE INTO shelters(name,node,capacity,available) VALUES(?,?,?,?)",
            [(s["name"], str(s["node"]), int(s["capacity"]), int(bool(s.get("available", True)))) for s in shelters],
        )


def load_shelters():
    initialize_database()
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute(
            "SELECT name,node,capacity,available FROM shelters ORDER BY name"
        ).fetchall()
    return [
        {"name": name, "node": node, "capacity": int(capacity), "available": bool(available)}
        for name, node, capacity, available in rows
    ]
