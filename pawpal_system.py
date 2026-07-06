"""
PawPal+ logic layer: class skeletons for Owner, Pet, Task, Scheduler.

This module contains lightweight, well-typed class skeletons capturing
the main responsibilities from the UML draft. Methods are intentionally
left as stubs to be implemented in later steps.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
from enum import Enum
import uuid
import datetime


@dataclass
class Priority(Enum):
    low = "low"
    medium = "medium"
    high = "high"


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
    priority: Priority = field(default_factory=lambda: Priority.medium)
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    # frequency controls recurrence: once, daily, weekly
    frequency: str = "once"
    # completion state
    completed: bool = False
    last_completed_at: Optional[str] = None

    def __post_init__(self) -> None:
        """Normalize priority and validate duration and frequency."""
        # allow creating Task with a priority string
        if isinstance(self.priority, str):
            try:
                self.priority = Priority(self.priority)
            except ValueError:
                # fallback to medium if unknown
                self.priority = Priority.medium

        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        # normalize frequency
        if self.frequency not in ("once", "daily", "weekly"):
            self.frequency = "once"

    def to_dict(self) -> Dict:
        """Return a serializable representation of the task."""
        return {
            "id": self.id,
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority.value if isinstance(self.priority, Priority) else str(self.priority),
            "notes": self.notes,
            "created_at": self.created_at,
            "frequency": self.frequency,
            "completed": self.completed,
            "last_completed_at": self.last_completed_at,
        }

    def mark_completed(self, at: Optional[datetime.datetime] = None) -> None:
        """Mark the task completed now or at the given timestamp."""
        self.completed = True
        ts = at or datetime.datetime.now()
        self.last_completed_at = ts.isoformat()

    def is_due(self, reference: Optional[datetime.datetime] = None) -> bool:
        """Return True when the task is due based on its frequency and completion."""
        ref = reference or datetime.datetime.now()
        if self.frequency == "once":
            return not self.completed

        if not self.last_completed_at:
            return True

        try:
            last = datetime.datetime.fromisoformat(self.last_completed_at)
        except Exception:
            return True

        if self.frequency == "daily":
            return (ref - last) >= datetime.timedelta(days=1)
        if self.frequency == "weekly":
            return (ref - last) >= datetime.timedelta(days=7)

        return True


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

    def to_dict(self) -> Dict:
        """Serializable representation of the pet and its tasks."""
        return {
            "name": self.name,
            "species": self.species,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    def get_pending_tasks(self, reference: Optional[datetime.datetime] = None) -> List[Task]:
        """Return tasks considered due based on frequency/completion."""
        ref = reference or datetime.datetime.now()
        return [t for t in self.tasks if t.is_due(ref)]

    def find_task_by_id(self, task_id: str) -> Optional[Task]:
        """Find and return a Task by its `id`, or None if not found."""
        for t in self.tasks:
            if t.id == task_id:
                return t
        return None

    def update_task(self, task_id: str, **changes) -> bool:
        """Update task fields by id and return True if updated."""
        t = self.find_task_by_id(task_id)
        if not t:
            return False
        for k, v in changes.items():
            if hasattr(t, k):
                setattr(t, k, v)
        return True


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
        """Add a Pet to the owner."""
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        """Remove a Pet by name (no-op if not found)."""
        self.pets = [p for p in self.pets if p.name != name]

    def all_tasks(self, include_completed: bool = False, reference: Optional[datetime.datetime] = None) -> List[Tuple[Task, Pet]]:
        """Return flat list of (task, pet) pairs, filtering by due status by default."""
        out: List[Tuple[Task, Pet]] = []
        ref = reference or datetime.datetime.now()
        for pet in self.pets:
            for task in pet.tasks:
                if include_completed or task.is_due(ref):
                    out.append((task, pet))
        return out

    def to_dict(self) -> Dict:
        """Return a serializable representation of the Owner."""
        return {
            "name": self.name,
            "available_time_minutes": self.available_time_minutes,
            "pets": [p.to_dict() for p in self.pets],
        }


class Scheduler:
    """Scheduling engine skeleton.

    The Scheduler is responsible for collecting tasks from `Owner` and
    producing a schedule respecting the owner's time constraint.

    Implementations of the scheduling algorithm (priority sorting,
    filtering, and tie-breaking) will be provided in later iterations.
    """

    def __init__(self) -> None:
        """Initialize a Scheduler (stateless)."""
        # No persistent state; Scheduler instances are lightweight.
        pass

    def generate_schedule(self, owner: Owner) -> Dict:
        """Greedy scheduler: high->low priority, shorter duration as tiebreaker.

        This simple algorithm is deterministic and easy to reason about;
        it selects tasks until the owner's available time is exhausted.
        """
        # prepare candidates
        # Only consider tasks that are currently due
        candidates = owner.all_tasks(include_completed=False)

        # priority score mapping (use string keys to avoid Enum hashing issues)
        PRIORITY_SCORE = {"high": 3, "medium": 2, "low": 1}

        # sort: priority desc, duration asc
        candidates.sort(key=lambda tp: (-PRIORITY_SCORE.get(getattr(tp[0].priority, "value", str(tp[0].priority)), 0), tp[0].duration_minutes))

        remaining = int(owner.available_time_minutes)
        accepted: List[Dict] = []
        rejected: List[Dict] = []
        used = 0

        for task, pet in candidates:
            if task.duration_minutes <= remaining:
                accepted.append({
                    "task_id": task.id,
                    "title": task.title,
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority.value if isinstance(task.priority, Priority) else str(task.priority),
                    "pet_name": pet.name,
                })
                remaining -= task.duration_minutes
                used += task.duration_minutes
            else:
                rejected.append({
                    "task_id": task.id,
                    "title": task.title,
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority.value if isinstance(task.priority, Priority) else str(task.priority),
                    "pet_name": pet.name,
                })

        explanation_lines = [
            f"Owner '{owner.name}' available time: {owner.available_time_minutes} minutes",
            f"Total scheduled time: {used} minutes",
            f"Tasks considered: {len(candidates)}",
            f"Tasks accepted: {len(accepted)}",
            f"Tasks rejected: {len(rejected)}",
        ]

        return {"accepted": accepted, "rejected": rejected, "explanation": "\n".join(explanation_lines)}
