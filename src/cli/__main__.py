"""Entry point for the todo app CLI."""

from src.cli.menu import Menu
from src.services.task_service import TaskService
from src.storage.memory_store import MemoryStore


def main() -> None:
    """Initialize and run the todo app."""
    store = MemoryStore()
    service = TaskService(store)
    menu = Menu(service)
    menu.run()


if __name__ == "__main__":
    main()
