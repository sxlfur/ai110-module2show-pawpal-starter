# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Sample terminal run of `main.py` (this repository's test harness) producing a generated daily plan:

```
Today's Schedule
------------------
1. Feed (Mochi) — 5m — high
2. Morning walk (Rex) — 30m — high
3. Morning play (Mochi) — 20m — medium

Rejected tasks (didn't fit):
- Grooming (Rex) — 45m

Reasoning:
Owner 'Alex' available time: 90 minutes
Total scheduled time: 55 minutes
Tasks considered: 4
Tasks accepted: 3
Tasks rejected: 1
```

## 🧪 Testing PawPal+

Run the automated test suite to verify the core scheduling system.

```bash
python -m pytest
```

The current tests cover:

- the `Task` recurrence and due-ness logic in `Task.is_due()`
- recurring task completion and auto-clone behavior in `Pet.complete_task()`
- schedule generation, ordering, and filtering behavior in `Scheduler.generate_schedule()`
- ordering by start time in `Scheduler.sort_by_time()` and filtering by pet/completion in `Scheduler.filter_tasks()`

Sample successful test output:

```bash
============================= test session starts ==============================
platform darwin -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/kevinshan/Desktop/CodePath/Github/ai110-module2show-pawpal-starter
plugins: anyio-4.13.0
collected 2 items                                                               

tests/test_pawpal.py ..                                                  [100%]

============================== 2 passed in 0.01s ==============================
```

Confidence Level: ★★★☆☆

This reflects the current correctness of the covered behaviors while acknowledging that the scheduler is still a simple greedy implementation and could be extended with richer overlap/conflict handling.

## 📐 Smarter Scheduling

This project implements a lightweight scheduling engine with several practical features. Below is a concise mapping from feature to the method(s) that implement it.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sorting behavior | `Scheduler.sort_by_time()` and internal sorting in `Scheduler.generate_schedule()` | Sorts instances by priority (high &gt; medium &gt; low), then earliest allowed start, then shortest duration as tiebreaker.
| Filtering behavior | `Scheduler.filter_tasks()`, `Owner.all_tasks()` | Filter by pet name(s) and completion status; `Owner.all_tasks()` supplies due tasks (uses `Task.is_due()`).
| Conflict detection logic | `Scheduler.generate_schedule()` (lightweight fixed-window warnings) | Emits warnings when multiple fixed-start tasks (where `earliest == latest`) overlap; used to notify immediate scheduling collisions.
| Recurring task logic | `Task.is_due()`, `Pet.complete_task()`, `Pet.get_pending_tasks()` | `is_due()` evaluates daily/weekly recurrence; `complete_task()` auto-clones the next recurrence instance when a recurring task is completed.

These methods and behaviors form the core of the scheduling approach used by the Streamlit UI (`app.py`) and the terminal demo (`main.py`).

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
