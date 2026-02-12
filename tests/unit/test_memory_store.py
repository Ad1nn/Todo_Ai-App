"""Unit tests for MemoryStore CRUD operations."""

from src.models.task import Task
from src.storage.memory_store import MemoryStore


class TestMemoryStoreAdd:
    """Tests for MemoryStore add operation."""

    def test_add_task_returns_task_with_id(self) -> None:
        """Adding a task should return it with assigned ID."""
        store = MemoryStore()
        task = Task(id=0, title="Test task")  # ID will be replaced

        result = store.add(task)

        assert result.id == 1
        assert result.title == "Test task"

    def test_add_multiple_tasks_assigns_sequential_ids(self) -> None:
        """Adding multiple tasks should assign sequential IDs."""
        store = MemoryStore()

        task1 = store.add(Task(id=0, title="First"))
        task2 = store.add(Task(id=0, title="Second"))
        task3 = store.add(Task(id=0, title="Third"))

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3


class TestMemoryStoreGet:
    """Tests for MemoryStore get operation."""

    def test_get_existing_task(self) -> None:
        """Getting an existing task should return it."""
        store = MemoryStore()
        added = store.add(Task(id=0, title="Test"))

        result = store.get(added.id)

        assert result is not None
        assert result.id == added.id
        assert result.title == "Test"

    def test_get_nonexistent_task_returns_none(self) -> None:
        """Getting a non-existent task should return None."""
        store = MemoryStore()

        result = store.get(999)

        assert result is None


class TestMemoryStoreGetAll:
    """Tests for MemoryStore get_all operation."""

    def test_get_all_empty_store(self) -> None:
        """Getting all from empty store should return empty list."""
        store = MemoryStore()

        result = store.get_all()

        assert result == []

    def test_get_all_returns_all_tasks(self) -> None:
        """Getting all should return all stored tasks."""
        store = MemoryStore()
        store.add(Task(id=0, title="First"))
        store.add(Task(id=0, title="Second"))
        store.add(Task(id=0, title="Third"))

        result = store.get_all()

        assert len(result) == 3
        titles = [t.title for t in result]
        assert "First" in titles
        assert "Second" in titles
        assert "Third" in titles


class TestMemoryStoreUpdate:
    """Tests for MemoryStore update operation."""

    def test_update_existing_task(self) -> None:
        """Updating an existing task should persist changes."""
        store = MemoryStore()
        added = store.add(Task(id=0, title="Original"))

        updated_task = Task(id=added.id, title="Updated", description="New desc", completed=True)
        result = store.update(updated_task)

        assert result is not None
        assert result.title == "Updated"
        assert result.description == "New desc"
        assert result.completed is True

    def test_update_nonexistent_task_returns_none(self) -> None:
        """Updating a non-existent task should return None."""
        store = MemoryStore()

        result = store.update(Task(id=999, title="Test"))

        assert result is None


class TestMemoryStoreDelete:
    """Tests for MemoryStore delete operation."""

    def test_delete_existing_task(self) -> None:
        """Deleting an existing task should remove it."""
        store = MemoryStore()
        added = store.add(Task(id=0, title="Test"))

        result = store.delete(added.id)

        assert result is True
        assert store.get(added.id) is None

    def test_delete_nonexistent_task_returns_false(self) -> None:
        """Deleting a non-existent task should return False."""
        store = MemoryStore()

        result = store.delete(999)

        assert result is False

    def test_deleted_id_not_reused(self) -> None:
        """Deleted task IDs should not be reused within session."""
        store = MemoryStore()
        task1 = store.add(Task(id=0, title="First"))
        store.delete(task1.id)

        task2 = store.add(Task(id=0, title="Second"))

        assert task2.id != task1.id
        assert task2.id == 2


class TestMemoryStoreNextId:
    """Tests for MemoryStore ID generation."""

    def test_next_id_starts_at_one(self) -> None:
        """First ID should be 1."""
        store = MemoryStore()

        assert store.next_id() == 1

    def test_next_id_increments(self) -> None:
        """Subsequent IDs should increment."""
        store = MemoryStore()

        id1 = store.next_id()
        id2 = store.next_id()
        id3 = store.next_id()

        assert id1 == 1
        assert id2 == 2
        assert id3 == 3
