from pawpal_system import Task, Pet, Priority
import datetime


def test_task_completion_changes_state():
    t = Task(title="Test task", duration_minutes=10, priority=Priority.low)
    assert not t.completed
    t.mark_completed(at=datetime.datetime.now())
    assert t.completed
    assert t.last_completed_at is not None


def test_adding_task_increases_pet_count():
    pet = Pet(name="Buddy", species="dog")
    initial = len(pet.tasks)
    t = Task(title="Walk", duration_minutes=15, priority=Priority.medium)
    pet.add_task(t)
    assert len(pet.tasks) == initial + 1
    assert pet.tasks[-1].title == "Walk"
