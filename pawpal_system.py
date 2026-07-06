"""
PawPal+ logic layer: class skeletons for Owner, Pet, Task, Scheduler.

This module contains lightweight, well-typed class skeletons capturing
the main responsibilities from the UML draft. Methods are intentionally
left as stubs to be implemented in later steps.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Dict


@dataclass
class Task:
    """Represents a single actionable pet-care task.

    Attributes
    - title: human-readable name of the task
    - duration_minutes: how long the task takes in minutes
    - priority: string priority label (e.g. 'low', 'medium', 'high')
    """

    title: str
    duration_minutes: int
    priority: str = "medium"

    def to_dict(self) -> Dict:
        """Return a serializable representation of the task."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
        }


@dataclass
class Pet:
    """Represents a pet and the collection of care tasks it requires.

    One `Pet` instance owns multiple `Task` instances (composition).
    """

    name: str
    species: str = "unknown"
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a `Task` to this pet."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove a task by title (no-op if not found)."""
        self.tasks = [t for t in self.tasks if t.title != title]


@dataclass
class Owner:
    """Represents the user/owner with global constraints and pets.

    Responsibilities:
    - track `available_time_minutes` constraint
    - own multiple `Pet` instances
    """

    name: str
    available_time_minutes: int = 120
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        self.pets = [p for p in self.pets if p.name != name]

    def all_tasks(self) -> List[Tuple[Task, Pet]]:
        """Return a flat list of (task, pet) pairs for scheduling."""
        out: List[Tuple[Task, Pet]] = []
        for pet in self.pets:
            for task in pet.tasks:
                out.append((task, pet))
        return out


class Scheduler:
    """Scheduling engine skeleton.

    The Scheduler is responsible for collecting tasks from `Owner` and
    producing a schedule respecting the owner's time constraint.

    Implementations of the scheduling algorithm (priority sorting,
    filtering, and tie-breaking) will be provided in later iterations.
    """

    def __init__(self) -> None:
        # No persistent state; Scheduler instances are lightweight.
        pass

    def generate_schedule(self, owner: Owner) -> Dict:
        """Generate a schedule for the given `Owner`.

        Returns a dict containing at minimum the following keys:
        - "accepted": list of scheduled tasks
        - "rejected": list of tasks that didn't fit
        - "explanation": human-readable reasoning

        This method is a placeholder and should be implemented later.
        """
        raise NotImplementedError("Scheduler.generate_schedule must be implemented")
