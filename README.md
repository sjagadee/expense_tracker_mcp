# fastmcp-demo-server

A small demo project for building [MCP](https://modelcontextprotocol.io) servers
with [FastMCP](https://github.com/jlowin/fastmcp). It contains two servers:

- **`main.py`** — an **Expense Tracker** MCP server backed by SQLite.
- **`main_old.py`** — a minimal **Demo** MCP server (dice roller + adder), kept
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

### Expense Tracker — [main.py](main.py)

A FastMCP server named `Expense Tracker MCP Server` that persists expenses in a
local SQLite database (`expenses.db`, created automatically on startup and
git-ignored).

The `expenses` table schema:

| Column      | Type    | Notes                          |
| ----------- | ------- | ------------------------------ |
| id          | INTEGER | Primary key, auto-increment    |
| name        | TEXT    | Required                       |
| amount      | REAL    | Required                       |
| category    | TEXT    | Required                       |
| subcategory | TEXT    | Optional, defaults to `''`     |
| note        | TEXT    | Optional, defaults to `''`     |

**Tools:**

- `add_expense(name, amount, category, subcategory="", note="")` — inserts an
  expense and returns `{"status": "ok", "id": <row id>}`.
- `list_expenses()` — returns all expenses ordered by `id` as a list of dicts.

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
├── main.py            # Expense Tracker MCP server (SQLite-backed)
├── main_old.py        # Demo MCP server (dice + add)
├── pyproject.toml     # Project metadata and dependencies
├── uv.lock            # Pinned dependency lockfile
├── .python-version    # Python version (3.11)
└── expenses.db        # SQLite database (auto-created, git-ignored)
```
