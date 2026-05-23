from fastmcp import FastMCP
from typing import Literal
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "transactions.db")

mcp = FastMCP("Expense Tracker MCP Server")


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

    if date is None:
        date = datetime.now().date().isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "INSERT INTO transactions (name, amount, category, subcategory, side, date, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, amount, category, subcategory, side, date, note),
        )
        conn.commit()
        return {"status": "ok", "id": cur.lastrowid}


@mcp.tool
def list_transactions(start_date: str, end_date: str) -> list[dict]:
    """List all transactions in the database within the given date range"""

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            """
            SELECT * FROM transactions
            WHERE date BETWEEN ? AND ?
            ORDER BY id ASC
            """,
            (start_date, end_date),
        )
        cols = [column[0] for column in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


@mcp.tool
def summarize(start_date: str, end_date: str, category: str | None = None, side: str = "debit") -> list[dict]:
    """Summarize transactions by category and side within the given date range"""

    with sqlite3.connect(DB_PATH) as conn:
        query = (
            "SELECT category, SUM(amount) as total FROM transactions "
            "WHERE date BETWEEN ? AND ? AND side = ?"
        )

        params = (start_date, end_date, side)
        if category:
            query += " AND category = ?"
            params += (category,)

        query += " GROUP BY category, side ORDER BY total DESC"

        cur = conn.execute(query, params)
        cols = [column[0] for column in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


@mcp.tool
def edit_transaction(
    id: int,
    name: str,
    amount: float,
    category: str,
    subcategory: str,
    date: str,
    note: str,
    side: Literal["debit", "credit"],
) -> dict:
    """Edit an existing transaction in the database"""

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "UPDATE transactions SET name = ?, amount = ?, category = ?, subcategory = ?, side = ?, date = ?, note = ? WHERE id = ?",
            (name, amount, category, subcategory, side, date, note, id),
        )
        conn.commit()

        if cur.rowcount == 0:
            return {"status": "error", "message": "Transaction not found"}
        return {"status": "ok"}


@mcp.tool
def delete_transaction(id: int) -> dict:
    """Delete an existing transaction from the database"""

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("DELETE FROM transactions WHERE id = ?", (id,))
        conn.commit()

        if cur.rowcount == 0:
            return {"status": "error", "message": "Transaction not found"}
        return {"status": "ok"}


if __name__ == "__main__":
    mcp.run()
