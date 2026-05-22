from fastmcp import FastMCP
import random

# Creatr a FastMCP server instance 
mcp = FastMCP("Demo MCP Server")


@mcp.tool
def roll_dice(n_dice: int = 1) -> list[int]:
    "Role n_dice 6-sided and return the result"
    return [random.randint(1, 6) for _ in range(n_dice)]


@mcp.tool
def add_numbers(a: float, b: float) -> float:
    "Add two numbers and return the value"
    return a+b


if __name__ == "__main__":
    mcp.run()
