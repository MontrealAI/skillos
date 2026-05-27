from __future__ import annotations


class PermissionError(Exception):
    pass


class PermissionCenter:
    def __init__(self, blocked_by_default: bool = True):
        self.blocked_by_default = blocked_by_default

    def check_tool(self, tool: str, allowed_tools: list[str], blocked_tools: list[str]) -> bool:
        if tool in blocked_tools:
            return False
        if tool in allowed_tools:
            return True
        return not self.blocked_by_default

    def require_tool(self, tool: str, allowed_tools: list[str], blocked_tools: list[str]) -> None:
        if not self.check_tool(tool, allowed_tools, blocked_tools):
            raise PermissionError(f"Tool not allowed: {tool}")
