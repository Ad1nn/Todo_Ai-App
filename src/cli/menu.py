"""Menu - Command-line interface for the todo app."""

from src.services.task_service import TaskService

# Message constants for consistency
ERROR_MESSAGES = {
    "empty_title": "Error: Task title cannot be empty.",
    "task_not_found": "Error: Task with ID {task_id} not found.",
    "invalid_id": "Error: Please enter a valid numeric ID.",
    "invalid_option": "Error: Invalid option. Please try again.",
}

SUCCESS_MESSAGES = {
    "task_added": "Task added successfully with ID {task_id}.",
    "task_updated": "Task {task_id} updated successfully.",
    "task_deleted": "Task {task_id} deleted successfully.",
    "task_completed": "Task {task_id} marked as complete.",
    "task_incomplete": "Task {task_id} marked as incomplete.",
}

DISPLAY = {
    "complete_indicator": "[x]",
    "incomplete_indicator": "[ ]",
    "empty_list_message": "No tasks found. Add a task to get started!",
}


class Menu:
    """Command-line menu interface for the todo app.

    Handles user input and displays output for all task operations.
    """

    def __init__(self, service: TaskService) -> None:
        """Initialize menu with a task service.

        Args:
            service: TaskService for handling task operations
        """
        self._service = service

    def display_menu(self) -> None:
        """Display the main menu options."""
        print("\n=== Todo App ===")
        print("1. Add Task")
        print("2. View All Tasks")
        print("3. Mark Task Complete/Incomplete")
        print("4. Update Task")
        print("5. Delete Task")
        print("6. Exit")
        print()

    def add_task(self) -> None:
        """Handle add task workflow."""
        title = input("Enter task title: ")
        description = input("Enter task description (optional): ")

        try:
            task = self._service.add_task(title, description)
            print(SUCCESS_MESSAGES["task_added"].format(task_id=task.id))
        except ValueError as e:
            print(f"Error: {e}")

    def view_tasks(self) -> None:
        """Display all tasks with status indicators."""
        tasks = self._service.get_all_tasks()

        if not tasks:
            print(DISPLAY["empty_list_message"])
            return

        print("\nID  | Status | Title           | Description")
        print("----|--------|-----------------|---------------------------")

        for task in tasks:
            if task.completed:
                status = DISPLAY["complete_indicator"]
            else:
                status = DISPLAY["incomplete_indicator"]
            # Truncate long titles/descriptions for display
            title_display = task.title[:15] if len(task.title) > 15 else task.title.ljust(15)
            desc_display = task.description[:25] if len(task.description) > 25 else task.description
            print(f"{task.id:<3} | {status}    | {title_display} | {desc_display}")

    def toggle_complete(self) -> None:
        """Handle toggle completion status workflow."""
        id_input = input("Enter task ID: ")

        try:
            task_id = int(id_input)
        except ValueError:
            print(ERROR_MESSAGES["invalid_id"])
            return

        task = self._service.toggle_complete(task_id)
        if task is None:
            print(ERROR_MESSAGES["task_not_found"].format(task_id=task_id))
        elif task.completed:
            print(SUCCESS_MESSAGES["task_completed"].format(task_id=task_id))
        else:
            print(SUCCESS_MESSAGES["task_incomplete"].format(task_id=task_id))

    def update_task(self) -> None:
        """Handle update task workflow."""
        id_input = input("Enter task ID: ")

        try:
            task_id = int(id_input)
        except ValueError:
            print(ERROR_MESSAGES["invalid_id"])
            return

        # Check if task exists first
        existing = self._service.get_task(task_id)
        if existing is None:
            print(ERROR_MESSAGES["task_not_found"].format(task_id=task_id))
            return

        new_title = input("Enter new title (press Enter to keep current): ")
        new_description = input("Enter new description (press Enter to keep current): ")

        # Use None if empty to keep current values
        title_arg = new_title if new_title else None
        desc_arg = new_description if new_description else None

        try:
            task = self._service.update_task(task_id, title=title_arg, description=desc_arg)
            if task:
                print(SUCCESS_MESSAGES["task_updated"].format(task_id=task_id))
        except ValueError as e:
            print(f"Error: {e}")

    def delete_task(self) -> None:
        """Handle delete task workflow."""
        id_input = input("Enter task ID: ")

        try:
            task_id = int(id_input)
        except ValueError:
            print(ERROR_MESSAGES["invalid_id"])
            return

        if self._service.delete_task(task_id):
            print(SUCCESS_MESSAGES["task_deleted"].format(task_id=task_id))
        else:
            print(ERROR_MESSAGES["task_not_found"].format(task_id=task_id))

    def process_choice(self, choice: str) -> bool:
        """Process a menu choice.

        Args:
            choice: The user's menu selection

        Returns:
            True to continue running, False to exit
        """
        if choice == "1":
            self.add_task()
        elif choice == "2":
            self.view_tasks()
        elif choice == "3":
            self.toggle_complete()
        elif choice == "4":
            self.update_task()
        elif choice == "5":
            self.delete_task()
        elif choice == "6":
            print("Goodbye!")
            return False
        else:
            print(ERROR_MESSAGES["invalid_option"])

        return True

    def run(self) -> None:
        """Run the main menu loop."""
        running = True
        while running:
            self.display_menu()
            choice = input("Select an option (1-6): ")
            running = self.process_choice(choice)
