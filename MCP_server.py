from __future__ import annotations

from fastmcp import FastMCP

# ------------------------------------------------------
# Create MCP Server
# ------------------------------------------------------

mcp = FastMCP("arith")

# ------------------------------------------------------
# Helper
# ------------------------------------------------------

def _as_number(x):
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        return float(x.strip())
    raise TypeError("Expected a number (int/float or numeric string)")

# ------------------------------------------------------
# MCP Tools
# ------------------------------------------------------

@mcp.tool()
async def add(a: float, b: float) -> float:
    """Return a + b."""
    return _as_number(a) + _as_number(b)

@mcp.tool()
async def subtract(a: float, b: float) -> float:
    """Return a - b."""
    return _as_number(a) - _as_number(b)

@mcp.tool()
async def multiply(a: float, b: float) -> float:
    """Return a * b."""
    return _as_number(a) * _as_number(b)

@mcp.tool()
async def divide(a: float, b: float) -> float:
    """Return a / b. Raises on division by zero."""
    a = _as_number(a)
    b = _as_number(b)
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return a / b

@mcp.tool()
async def modulus(a: float, b: float) -> float:
    """Return a % b. Raises on modulus by zero."""
    a = _as_number(a)
    b = _as_number(b)
    if b == 0:
        raise ZeroDivisionError("modulus by zero")
    return a % b

@mcp.tool()
async def power(a: float, b: float) -> float:
    """Return a ** b."""
    return _as_number(a) ** _as_number(b)

# ------------------------------------------------------
# Start MCP Server
# ------------------------------------------------------

if __name__ == "__main__":
    # Starts the MCP server on stdio (default)
    mcp.run()



# from __future__ import annotations
# from fastmcp import FastMCP

# mcp = FastMCP("arith")

# def _as_number(x):
#     if isinstance(x,(int,float)):
#         return float(x)
#     if isinstance(x,str):
#         return float(x.strip())
#     raise TypeError("Expected a number (int/flaot or numeric string)")


# @mcp.tool()
# async def add(a:float,b:float)-> float:
#     """Return a + b."""
#     return _as_number(a) + _as_number(b)

# @mcp.tool()
# async def subtract(a:float,b:float)-> float:
#     """Return a - b."""
#     return _as_number(a) - _as_number(b)

# @mcp.tool()
# async def multiply(a:float,b:float)-> float:
#     """Return a * b."""
#     return _as_number(a) * _as_number(b)

# @mcp.tool()
# async def divide(a:float,b:float)-> float:
#     """Return a / b.Raises on division by zero"""
#     a = _as_number(a) 
#     b =_as_number(b)
#     if b == 0:
#         raise ZeroDivisionError("division by zero")
#     return a / b

# @mcp.tool()
# async def modulus(a:float,b:float)-> float:
#     """Return a % b.Raises on modulus by zero"""
#     a = _as_number(a) 
#     b =_as_number(b)
#     if b == 0:
#         raise ZeroDivisionError("modulus by zero")
#     return a % b

# @mcp.tool()
# async def power(a:float,b:float)-> float:
#     """Return a ** b."""
#     return _as_number(a) ** _as_number(b)


