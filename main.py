from fastmcp import FastMCP
import os
import sqlite3

DB_path = os.path.join(os.path.dirname(__file__), "expenses.db")

mcp = FastMCP("Expense Tracker MCP Server")


def init_db():
    with sqlite3.connect(DB_path) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT DEFAULT '',
            note TEXT DEFAULT '')""")
        conn.commit()
        

init_db()


@mcp.tool
def add_expense(name: str, amount: float, category: str, subcategory: str = "", note: str = "") -> None:
    """Add a new expense record to the database"""
    
    with sqlite3.connect(DB_path) as conn:
        cur = conn.execute(
            "INSERT INTO expenses (name, amount, category, subcategory, note) VALUES (?, ?, ?, ?, ?)", 
            (name, amount, category, subcategory, note)
        )
        conn.commit()
        return {"status": "ok", "id": cur.lastrowid}


@mcp.tool
def list_expenses():
    """List all expense records in the database"""
    
    with sqlite3.connect(DB_path) as conn:
        cur = conn.execute("SELECT * FROM expenses ORDER BY id ASC")
        cols = [column[0] for column in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


if __name__ == "__main__":
    mcp.run()