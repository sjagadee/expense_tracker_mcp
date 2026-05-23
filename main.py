from fastmcp import FastMCP
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")

mcp = FastMCP("Expense Tracker MCP Server")


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS expenses (
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
def add_expense(
    name: str,
    amount: float,
    category: str,
    subcategory: str = "",
    date: str = "",
    note: str = "",
    side: str = "debit",
) -> dict:
    """Add a new expense record to the database"""

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "INSERT INTO expenses (name, amount, category, subcategory, side, date, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, amount, category, subcategory, side, date, note),
        )
        conn.commit()
        return {"status": "ok", "id": cur.lastrowid}


@mcp.tool
def list_expenses(start_date: str, end_date: str) -> list[dict]:
    """List all expense records in the database"""

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            """
            SELECT * FROM expenses 
            WHERE date BETWEEN ? AND ?
            ORDER BY id ASC
            """,
            (start_date, end_date),
        )
        cols = [column[0] for column in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


@mcp.tool
def summarize(start_date: str, end_date: str, category: str | None = None) -> list[dict]:
    """Summarize expenses by category"""

    with sqlite3.connect(DB_PATH) as conn:
        query = (
            "SELECT category, SUM(amount) as total FROM expenses "
            "WHERE date BETWEEN ? AND ?"
        )

        params = (start_date, end_date)
        if category:
            query += " AND category = ?"
            params += (category,)

        query += " GROUP BY category ORDER BY total DESC"

        cur = conn.execute(query, params)
        cols = [column[0] for column in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


@mcp.tool
def edit_expense(
    id: int,
    name: str,
    amount: float,
    category: str,
    subcategory: str,
    date: str,
    note: str,
) -> dict:
    """Edit an existing expense record in the database"""

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "UPDATE expenses SET name = ?, amount = ?, category = ?, subcategory = ?, date = ?, note = ? WHERE id = ?",
            (name, amount, category, subcategory, date, note, id),
        )
        conn.commit()
        
        if cur.rowcount == 0:
            return {"status": "error", "message": "Expense not found"}
        return {"status": "ok"}


@mcp.tool
def delete_expense(id: int) -> dict:
    """Delete an existing expense record from the database"""

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("DELETE FROM expenses WHERE id = ?", (id,))
        conn.commit()
        
        if cur.rowcount == 0:
            return {"status": "error", "message": "Expense not found"}
        return {"status": "ok"}


@mcp.tool
def add_credit(
    name: str,
    amount: float,
    category: str,
    subcategory: str,
    date: str,
    note: str,
    side: str = "credit",
) -> dict:
    """Add a new credit record to the database"""

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO expenses (name, amount, category, subcategory, side, date, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, amount, category, subcategory, side, date, note),
        )
        conn.commit()
        return {"status": "ok"}


if __name__ == "__main__":
    mcp.run()
