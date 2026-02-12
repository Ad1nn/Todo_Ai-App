"""Agent configuration for OpenAI Agents SDK."""

from typing import Any
from uuid import UUID

from agents import Agent, function_tool
from sqlalchemy.ext.asyncio import AsyncSession

from src.agent.prompts import SYSTEM_PROMPT, TOOL_DESCRIPTIONS
from src.config import settings
from src.mcp.tools import MCPToolError, MCPTools


def get_tool_definitions() -> list[dict[str, Any]]:
    """Get OpenAI function tool definitions for all MCP tools."""
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": TOOL_DESCRIPTIONS["add_task"],
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The task title (1-200 characters)",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional task description",
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Due date in ISO format (e.g., 2024-12-31T09:00:00)",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "normal", "high", "urgent"],
                            "description": "Task priority level",
                        },
                        "category": {
                            "type": "string",
                            "description": "Task category (e.g., work, personal, shopping, health, finance)",
                        },
                    },
                    "required": ["title"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": TOOL_DESCRIPTIONS["list_tasks"],
                "parameters": {
                    "type": "object",
                    "properties": {
                        "completed": {
                            "type": "boolean",
                            "description": (
                                "Filter by completion status "
                                "(true=completed, false=pending, omit=all)"
                            ),
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "normal", "high", "urgent"],
                            "description": "Filter by priority level",
                        },
                        "category": {
                            "type": "string",
                            "description": "Filter by category name",
                        },
                        "overdue": {
                            "type": "boolean",
                            "description": "Set to true to show only overdue tasks",
                        },
                        "sort_by": {
                            "type": "string",
                            "enum": ["created_at", "due_date", "priority"],
                            "description": "Sort results by field",
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": TOOL_DESCRIPTIONS["complete_task"],
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "The UUID of the task to complete",
                        },
                    },
                    "required": ["task_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": TOOL_DESCRIPTIONS["delete_task"],
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "The UUID of the task to delete",
                        },
                    },
                    "required": ["task_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": TOOL_DESCRIPTIONS["update_task"],
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "The UUID of the task to update",
                        },
                        "title": {
                            "type": "string",
                            "description": "New task title (optional)",
                        },
                        "description": {
                            "type": "string",
                            "description": "New task description (optional)",
                        },
                        "due_date": {
                            "type": "string",
                            "description": "New due date in ISO format (optional)",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "normal", "high", "urgent"],
                            "description": "New priority level (optional)",
                        },
                        "category": {
                            "type": "string",
                            "description": "New category (optional)",
                        },
                        "clear_due_date": {
                            "type": "boolean",
                            "description": "Set to true to remove the due date",
                        },
                        "clear_priority": {
                            "type": "boolean",
                            "description": "Set to true to remove the priority",
                        },
                        "clear_category": {
                            "type": "boolean",
                            "description": "Set to true to remove the category",
                        },
                    },
                    "required": ["task_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "uncomplete_task",
                "description": TOOL_DESCRIPTIONS["uncomplete_task"],
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "The UUID of the task to mark as pending",
                        },
                    },
                    "required": ["task_id"],
                },
            },
        },
    ]


def create_agent(session: AsyncSession, user_id: UUID) -> Agent:
    """
    Create an agent instance with MCP tools bound to a user session.

    Args:
        session: Database session for tool operations
        user_id: Authenticated user ID for task ownership

    Returns:
        Configured Agent instance with task management tools
    """
    mcp_tools = MCPTools(session, user_id)

    @function_tool
    async def add_task(
        title: str,
        description: str | None = None,
        due_date: str | None = None,
        priority: str | None = None,
        category: str | None = None,
    ) -> dict[str, Any]:
        """Create a new task for the user."""
        try:
            return await mcp_tools.add_task(title, description, due_date, priority, category)
        except MCPToolError as e:
            return {"status": "error", "error": e.message}

    @function_tool
    async def list_tasks(
        completed: bool | None = None,
        priority: str | None = None,
        category: str | None = None,
        overdue: bool | None = None,
        sort_by: str | None = None,
    ) -> dict[str, Any]:
        """List all tasks for the user, optionally filtered."""
        try:
            return await mcp_tools.list_tasks(completed, priority, category, overdue, sort_by)
        except MCPToolError as e:
            return {"status": "error", "error": e.message}

    @function_tool
    async def complete_task(task_id: str) -> dict[str, Any]:
        """Mark a task as completed."""
        try:
            return await mcp_tools.complete_task(task_id)
        except MCPToolError as e:
            return {"status": "error", "error": e.message}

    @function_tool
    async def delete_task(task_id: str) -> dict[str, Any]:
        """Delete a task."""
        try:
            return await mcp_tools.delete_task(task_id)
        except MCPToolError as e:
            return {"status": "error", "error": e.message}

    @function_tool
    async def update_task(
        task_id: str,
        title: str | None = None,
        description: str | None = None,
        due_date: str | None = None,
        priority: str | None = None,
        category: str | None = None,
        clear_due_date: bool = False,
        clear_priority: bool = False,
        clear_category: bool = False,
    ) -> dict[str, Any]:
        """Update a task's fields."""
        try:
            return await mcp_tools.update_task(
                task_id, title, description, due_date, priority, category,
                clear_due_date, clear_priority, clear_category
            )
        except MCPToolError as e:
            return {"status": "error", "error": e.message}

    @function_tool
    async def uncomplete_task(task_id: str) -> dict[str, Any]:
        """Mark a completed task as pending again."""
        try:
            return await mcp_tools.uncomplete_task(task_id)
        except MCPToolError as e:
            return {"status": "error", "error": e.message}

    return Agent(
        name="TaskAssistant",
        instructions=SYSTEM_PROMPT,
        model=settings.openai_model,
        tools=[
            add_task,
            list_tasks,
            complete_task,
            delete_task,
            update_task,
            uncomplete_task,
        ],
    )
