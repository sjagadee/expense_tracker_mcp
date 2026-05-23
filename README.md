# fastmcp-demo-server

A small demo project for building [MCP](https://modelcontextprotocol.io) servers
with [FastMCP](https://github.com/jlowin/fastmcp). It contains two servers:

- **[main.py](main.py)** — a **Transaction Tracker** MCP server backed by SQLite.
- **[main_old.py](main_old.py)** — a minimal **Demo** MCP server (dice roller + adder), kept
  as a starting-point reference.

## Requirements

- Python `>=3.11` (see [.python-version](.python-version))
- [`uv`](https://docs.astral.sh/uv/) for dependency management and running
- [`fastmcp`](https://github.com/jlowin/fastmcp) `>=3.3.1` (see [pyproject.toml](pyproject.toml))

## Setup

```bash
uv sync
```

This installs dependencies into a local `.venv` from [uv.lock](uv.lock).

## Servers

### Transaction Tracker — [main.py](main.py)

A FastMCP server named `Transaction Tracker MCP Server` that persists debit and
credit transactions in a local SQLite database (`transactions.db`, created
automatically on startup and git-ignored).

The `transactions` table schema:

| Column      | Type    | Notes                                                  |
| ----------- | ------- | ------------------------------------------------------ |
| id          | INTEGER | Primary key, auto-increment                            |
| name        | TEXT    | Required                                               |
| amount      | REAL    | Required, must be positive                             |
| category    | TEXT    | Required                                               |
| subcategory | TEXT    | Optional, defaults to `''`                             |
| side        | TEXT    | `debit` or `credit`, defaults to `''`                  |
| date        | TEXT    | `YYYY-MM-DD`, defaults to current date                 |
| note        | TEXT    | Optional, defaults to `''`                             |

**Tools:**

- `add_transaction(name, amount, category, subcategory="", date=None, note="", side="debit")`
  — inserts a transaction and returns `{"status": "ok", "id": <row id>}`.
  `date` defaults to today; `side` must be `"debit"` or `"credit"`.
- `list_transactions(start_date, end_date, category=None, side=None)`
  — returns transactions in the given date range, optionally filtered by
  `category` and/or `side`, ordered by `id`.
- `summarize(start_date, end_date, category=None, side="debit")`
  — returns totals grouped by category for the given date range and `side`,
  ordered by total descending.
- `edit_transaction(id, name=None, amount=None, category=None, subcategory=None, date=None, note=None, side=None)`
  — updates only the fields you pass. Raises if `id` does not exist.
- `delete_transaction(id)` — deletes the row. Raises if `id` does not exist.

Dates must be ISO `YYYY-MM-DD`; `amount` must be `> 0`.

### Demo — [main_old.py](main_old.py)

A minimal FastMCP server named `Demo MCP Server`.

**Tools:**

- `roll_dice(n_dice=1)` — rolls `n_dice` six-sided dice and returns a list of results.
- `add_numbers(a, b)` — adds two numbers and returns the sum.

## Usage

Replace `main.py` with `main_old.py` in any command below to target the demo server.

### Test the server in the FastMCP Inspector

```bash
uv run fastmcp inspector main.py
```

### Run the server locally

```bash
uv run fastmcp run main.py
```

### Connect the server to a client (Claude Desktop)

```bash
uv run fastmcp install claude-desktop main.py
```

## Project structure

```text
fastmcp-demo-server/
├── main.py             # Transaction Tracker MCP server (SQLite-backed)
├── main_old.py         # Demo MCP server (dice + add)
├── pyproject.toml      # Project metadata and dependencies
├── uv.lock             # Pinned dependency lockfile
├── .python-version     # Python version (3.11)
└── transactions.db     # SQLite database (auto-created, git-ignored)
```
