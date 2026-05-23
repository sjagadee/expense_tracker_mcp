from fastmcp import FastMCP
from typing import Literal
import os
import sqlite3
from datetime import date, datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "transactions.db")

mcp = FastMCP("Transaction Tracker MCP Server")


def _validate_date(value: str, field: str) -> None:
    try:
        date.fromisoformat(value)
    except ValueError:
        raise ValueError(f"{field} must be in YYYY-MM-DD format, got {value!r}")


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT DEFAULT '',
            side TEXT DEFAULT '',
            date TEXT DEFAULT (strftime('%Y-%m-%d', 'now')),
            note TEXT DEFAULT '')""")
        conn.commit()


init_db()


@mcp.tool
def add_transaction(
    name: str,
    amount: float,
    category: str,
    subcategory: str = "",
    date: str | None = None,
    note: str = "",
    side: Literal["debit", "credit"] = "debit",
) -> dict:
    """Add a new transaction (debit or credit) to the database"""

    if amount <= 0:
        raise ValueError(f"amount must be positive, got {amount}")
    if date is None:
        date = datetime.now().date().isoformat()
    else:
        _validate_date(date, "date")

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "INSERT INTO transactions (name, amount, category, subcategory, side, date, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, amount, category, subcategory, side, date, note),
        )
        conn.commit()
        return {"status": "ok", "id": cur.lastrowid}


@mcp.tool
def list_transactions(
    start_date: str,
    end_date: str,
    category: str | None = None,
    side: Literal["debit", "credit"] | None = None,
) -> list[dict]:
    """List transactions within the given date range, optionally filtered by category and side"""

    _validate_date(start_date, "start_date")
    _validate_date(end_date, "end_date")

    query = (
        "SELECT id, name, amount, category, subcategory, side, date, note "
        "FROM transactions WHERE date BETWEEN ? AND ?"
    )
    params: tuple = (start_date, end_date)
    if category:
        query += " AND category = ?"
        params += (category,)
    if side:
        query += " AND side = ?"
        params += (side,)
    query += " ORDER BY id ASC"

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(query, params)
        cols = [column[0] for column in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


@mcp.tool
def summarize(start_date: str, end_date: str, category: str | None = None, side: Literal["debit", "credit"] = "debit") -> list[dict]:
    """Summarize transactions by category and side within the given date range"""

    _validate_date(start_date, "start_date")
    _validate_date(end_date, "end_date")

    with sqlite3.connect(DB_PATH) as conn:
        query = (
            "SELECT category, SUM(amount) as total FROM transactions "
            "WHERE date BETWEEN ? AND ? AND side = ?"
        )

        params = (start_date, end_date, side)
        if category:
            query += " AND category = ?"
            params += (category,)

        query += " GROUP BY category ORDER BY total DESC"

        cur = conn.execute(query, params)
        cols = [column[0] for column in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


@mcp.tool
def edit_transaction(
    id: int,
    name: str | None = None,
    amount: float | None = None,
    category: str | None = None,
    subcategory: str | None = None,
    date: str | None = None,
    note: str | None = None,
    side: Literal["debit", "credit"] | None = None,
) -> dict:
    """Edit an existing transaction. Only fields you pass are updated."""

    if amount is not None and amount <= 0:
        raise ValueError(f"amount must be positive, got {amount}")
    if date is not None:
        _validate_date(date, "date")

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            """
            UPDATE transactions SET
                name = COALESCE(?, name),
                amount = COALESCE(?, amount),
                category = COALESCE(?, category),
                subcategory = COALESCE(?, subcategory),
                side = COALESCE(?, side),
                date = COALESCE(?, date),
                note = COALESCE(?, note)
            WHERE id = ?
            """,
            (name, amount, category, subcategory, side, date, note, id),
        )
        conn.commit()

        if cur.rowcount == 0:
            raise LookupError(f"Transaction {id} not found")
        return {"status": "ok"}


@mcp.tool
def delete_transaction(id: int) -> dict:
    """Delete an existing transaction from the database"""

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("DELETE FROM transactions WHERE id = ?", (id,))
        conn.commit()

        if cur.rowcount == 0:
            raise LookupError(f"Transaction {id} not found")
        return {"status": "ok"}


if __name__ == "__main__":
    mcp.run()
