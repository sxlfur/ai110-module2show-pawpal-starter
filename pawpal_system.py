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
    # earliest/latest allowed start minute for the task (minutes from day start)
    earliest_start_minute: int = 0
    latest_start_minute: Optional[int] = None
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
        # normalize earliest/latest
        if self.earliest_start_minute is None:
            self.earliest_start_minute = 0
        if self.latest_start_minute is not None and self.latest_start_minute < self.earliest_start_minute:
            # enforce consistency
            self.latest_start_minute = self.earliest_start_minute

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
            "earliest_start_minute": self.earliest_start_minute,
            "latest_start_minute": self.latest_start_minute,
        }

    def mark_completed(self, at: Optional[datetime.datetime] = None) -> None:
        """Mark the task completed now or at the given timestamp."""
        self.completed = True
        ts = at or datetime.datetime.now()
        self.last_completed_at = ts.isoformat()

    def is_due(self, reference: Optional[datetime.datetime] = None) -> bool:
        """Determine whether this task instance should be considered due now.

        Logic:
        - For `once` tasks: return True only if not yet completed.
        - For recurring tasks (`daily`, `weekly`): if never completed, the task is due.
          Otherwise, compare `last_completed_at` against `reference` and return True
          when the recurrence interval (1 day for `daily`, 7 days for `weekly`) has passed.

        Args:
            reference: optional datetime to evaluate due-ness against (defaults to now).

        Returns:
            True if the task should be presented to the scheduler as pending.
        """
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

    def complete_task(self, task_id: str, at: Optional[datetime.datetime] = None) -> bool:
        """Mark a task completed and, for recurring tasks, create the next due instance.

        This method performs two actions:
        1. Marks the existing task instance as completed by calling `Task.mark_completed()`.
        2. If the completed task is recurring (`daily` or `weekly`), it clones a new
           Task instance with the same core attributes and sets its `last_completed_at`
           to the completion time so that the new instance will become due only after
           the recurrence interval has elapsed.

        Args:
            task_id: the id of the task to complete.
            at: optional datetime representing when the task was completed (defaults to now).

        Returns:
            True if the specified task was found and processed, False otherwise.
        """
        t = self.find_task_by_id(task_id)
        if not t:
            return False
        ts = at or datetime.datetime.now()
        # mark current instance completed
        t.mark_completed(at=ts)

        # If recurring, create next instance whose last_completed_at is set to now
        if t.frequency in ("daily", "weekly"):
            # clone core fields
            new_task = Task(
                title=t.title,
                duration_minutes=t.duration_minutes,
                priority=t.priority,
                frequency=t.frequency,
                earliest_start_minute=t.earliest_start_minute,
                latest_start_minute=t.latest_start_minute,
                notes=t.notes,
            )
            # set last_completed_at to now so the new instance becomes due after the recurrence interval
            new_task.last_completed_at = ts.isoformat()
            new_task.completed = False
            self.tasks.append(new_task)

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
        """Schedule due tasks into concrete start minutes using a greedy slotting algorithm.

        Behavior and features implemented:
        - Collects due tasks from `owner` (respecting task `frequency` via `Task.is_due`).
        - Expands tasks into single-day instances constrained by per-task `earliest_start_minute`
          and `latest_start_minute` and by the owner's `available_time_minutes` window.
        - Sorts instances by priority (high &gt; medium &gt; low), then earliest allowed start,
          then shortest duration as a tiebreaker.
        - Attempts to place each task at the earliest free minute within its allowed window
          using minute-granularity slots; accepted tasks receive a `start_minute` in the result.
        - Records rejected tasks that couldn't be placed and emits a human-readable `explanation`.
        - Produces lightweight conflict warnings for overlapping fixed-window tasks (where
          `earliest == latest`) to highlight immediate scheduling collisions.

        Returns:
            A dictionary with keys: `accepted` (list), `rejected` (list), `explanation` (str),
            and optional `warnings` (list of strings).
        """
        def overlaps(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
            return not (a_end <= b_start or b_end <= a_start)

        # Parameters (kept simple; callers can extend)
        pets: Optional[List[str]] = None
        include_completed: bool = False
        reference: Optional[datetime.datetime] = None

        # collect due tasks
        candidates = owner.all_tasks(include_completed=include_completed, reference=reference)
        if pets:
            candidates = [(t, p) for (t, p) in candidates if p.name in pets]

        # Expand each task into a single-day instance if it's due
        instances = []
        for task, pet in candidates:
            if not task.is_due(reference):
                continue
            earliest = max(0, task.earliest_start_minute or 0)
            # latest allowed start minute: default to owner's available window minus duration
            if task.latest_start_minute is None:
                latest = max(0, owner.available_time_minutes - task.duration_minutes)
            else:
                latest = task.latest_start_minute
            # clamp latest to owner's available window
            latest = min(latest, max(0, owner.available_time_minutes - task.duration_minutes))

            instances.append({
                "task": task,
                "pet": pet,
                "earliest": earliest,
                "latest": latest,
            })

        # priority score mapping
        PRIORITY_SCORE = {"high": 3, "medium": 2, "low": 1}

        # sort instances by priority desc, then earliest asc, then duration asc
        instances.sort(key=lambda ins: (
            -PRIORITY_SCORE.get(getattr(ins["task"].priority, "value", str(ins["task"].priority)), 0),
            ins["earliest"],
            ins["task"].duration_minutes,
        ))

        occupied: List[Tuple[int, int]] = []  # list of (start, end) end-exclusive
        accepted: List[Dict] = []
        rejected: List[Dict] = []
        conflicts: List[Dict] = []

        for ins in instances:
            task = ins["task"]
            pet = ins["pet"]
            dur = task.duration_minutes
            placed = False
            # try each possible start minute within [earliest, latest]
            for s in range(ins["earliest"], ins["latest"] + 1):
                end = s + dur
                if end > owner.available_time_minutes:
                    continue
                # check overlap with any occupied slot
                if any(overlaps(s, end, a, b) for (a, b) in occupied):
                    continue
                # place task
                occupied.append((s, end))
                occupied.sort()
                accepted.append({
                    "task_id": task.id,
                    "title": task.title,
                    "duration_minutes": dur,
                    "priority": task.priority.value if isinstance(task.priority, Priority) else str(task.priority),
                    "pet_name": pet.name,
                    "start_minute": s,
                })
                placed = True
                break

            if not placed:
                # couldn't place within allowed window
                rejected.append({
                    "task_id": task.id,
                    "title": task.title,
                    "duration_minutes": dur,
                    "priority": task.priority.value if isinstance(task.priority, Priority) else str(task.priority),
                    "pet_name": pet.name,
                    "earliest": ins["earliest"],
                    "latest": ins["latest"],
                })

        # Basic conflict reporting: if rejected but there is free time overall, it may be due to windows
        total_used = sum(item[1] - item[0] for item in occupied)
        explanation_lines = [
            f"Owner '{owner.name}' available time: {owner.available_time_minutes} minutes",
            f"Total scheduled time: {total_used} minutes",
            f"Instances considered: {len(instances)}",
            f"Tasks accepted: {len(accepted)}",
            f"Tasks rejected: {len(rejected)}",
        ]
        if rejected:
            explanation_lines.append("Rejected tasks may conflict with time windows or not fit the owner's available time.")

        # Lightweight conflict detection: warn when multiple fixed-window tasks overlap
        warnings: List[str] = []
        fixed = [ins for ins in instances if ins["earliest"] == ins["latest"]]
        for i in range(len(fixed)):
            a = fixed[i]
            a_start = a["earliest"]
            a_end = a_start + a["task"].duration_minutes
            for j in range(i + 1, len(fixed)):
                b = fixed[j]
                b_start = b["earliest"]
                b_end = b_start + b["task"].duration_minutes
                if not (a_end <= b_start or b_end <= a_start):
                    warnings.append(
                        f"Conflict: '{a['task'].title}' (pet {a['pet'].name}) and '{b['task'].title}' (pet {b['pet'].name}) both require the same fixed time starting at {a_start}.")

        # sort accepted tasks by assigned start time before returning
        accepted = self.sort_by_time(accepted)
        result = {"accepted": accepted, "rejected": rejected, "explanation": "\n".join(explanation_lines)}
        if warnings:
            result["warnings"] = warnings
        return result

    def sort_by_time(self, tasks: List[Dict]) -> List[Dict]:
        """Return tasks sorted by their scheduled start time.

        Primary sort key: `start_minute` if present, otherwise fall back to an `earliest` value.
        Secondary key: `duration_minutes` to give deterministic ordering for equal start times.

        Args:
            tasks: list of task dicts produced by `generate_schedule` (may include `start_minute`).

        Returns:
            A new list sorted by start time then duration.
        """
        def key_fn(t: Dict):
            return (t.get("start_minute", t.get("earliest", 0)), t.get("duration_minutes", 0))

        return sorted(tasks, key=key_fn)

    def filter_tasks(self, owner: Owner, pet_names: Optional[List[str]] = None, completed: Optional[bool] = None, reference: Optional[datetime.datetime] = None) -> List[Tuple[Task, Pet]]:
        """Return (task, pet) pairs filtered by pet names and/or completion status.

        This helper centralizes common filtering logic used by the UI or tests.

        Args:
            owner: the Owner whose tasks will be considered.
            pet_names: optional list of pet names to include (None => include all pets).
            completed: optional boolean to filter by completion state (None => ignore completion).
            reference: optional datetime passed to `all_tasks` for due-ness evaluation.

        Returns:
            List of `(task, pet)` tuples matching the filters.
        """
        pairs = owner.all_tasks(include_completed=True, reference=reference)
        out: List[Tuple[Task, Pet]] = []
        for task, pet in pairs:
            if pet_names and pet.name not in pet_names:
                continue
            if completed is not None and task.completed != completed:
                continue
            out.append((task, pet))
        return out
