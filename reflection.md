# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

## System Design

**Core User Actions:**
1. Enter Owner & Pet Information: A user can input and save basic profiles for themselves and their pet to tailor the experience.
2. Add/Edit Care Tasks: A user can create, update, or remove specific pet care tasks (e.g., walking, feeding), setting specific constraints like duration and priority level.
3. Generate a Daily Schedule: A user can request an automated daily plan that schedules their entered tasks based on available time and priorities, and view the reasoning behind the schedule.

- Briefly describe your initial UML design.

My initial UML design for PawPal+ uses four primary classes to structure the pet care scheduling system:
Owner and Pet Classes: These form the core relationship, where one Owner can own multiple Pet objects (a 1-to-many composition). The Owner holds the primary constraint (available_time_minutes), while the Pet stores specific identification details.
Task Class: This class acts as the building block for the schedule, owned by the Pet. It holds crucial scheduling variables like duration and priority.
Scheduler Class: This is the operational engine of the system. It is designed to pull constraints from the Owner and the pool of tasks from the Pet to sort, filter, and generate a final care schedule.


- What classes did you include, and what responsibilities did you assign to each?

Owner: This class is responsible for representing the user. Its main job is to track the user's overall daily time limit (available_time_minutes) and manage the collection of pets they own.
Pet: This class is responsible for holding the specific profile of the animal (name, species/breed). Its primary role in the system is to act as a container for all the care tasks that the specific pet requires.
Task: This class is responsible for representing a single, actionable pet care activity. It holds all the specific variables needed for scheduling, such as how long the task takes (duration), how important it is (priority), and when it should happen.
Scheduler: This class is the engine responsible for all the logic. It does not store permanent data; instead, its job is to collect the time constraints from the Owner and the required tasks from the Pet, sort them by priority, filter out what doesn't fit within the time limit, and output the final generated schedule and reasoning.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Changes made in pawpal_system.py:
Added Priority Enum (low, medium, high) and used it for Task.priority.
Added id, notes, and created_at to Task, with __post_init__ validation (positive duration) and string-to-enum conversion.
Expanded Task.to_dict() to include metadata.
Added to_dict() to Pet and Owner.
Implemented Scheduler.generate_schedule() with a simple greedy algorithm (priority high→low, shorter-first tiebreaker). Returns accepted, rejected, and explanation.
Updated the todo list: added and completed "Apply review changes to pawpal_system.py".
Next steps I can take:

Run quick unit tests to verify validation and scheduling behavior.
Wire app.py to use pawpal_system.py instead of the other scheduler module.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

 - **What constraints does your scheduler consider?**
	 - **Owner available time:** a global daily time budget (`available_time_minutes`) that caps scheduled work.
	 - **Task priority:** high/medium/low ranking to prefer important tasks when time is limited.
	 - **Task duration:** how many minutes each task takes (used to fit tasks into the time budget and slots).
	 - **Recurrence / frequency:** whether a task is once, daily, or weekly (affects whether it's due today).
	 - **Time windows / preferences:** per-task `earliest_start_minute` / `latest_start_minute` to express preferred times of day.
	 - **Completion status:** skip tasks already completed for the current recurrence.
	 - **Pet context / fairness:** tasks are associated with pets; scheduler can filter by pet and optionally apply simple fairness rules.

 - **How did you decide which constraints mattered most?**
	 - **Owner available time first:** the owner's daily available time is the fundamental resource; nothing can be scheduled beyond it, so it governs feasibility.
	 - **Priority second:** when time is scarce, honoring task priority preserves the most important care actions (meds, feeding) before lower-value items.
	 - **Duration third:** shorter tasks are useful tiebreakers because they allow packing more useful actions into the same budget.
	 - **Recurrence & windows next:** recurrence determines whether a task should appear today; windows are enforced when assigning concrete start times to keep the plan practical.
	 - **Simplicity & UX last:** for an MVP I favored simple, explainable rules over complex optimization — this made the scheduler predictable and easier to explain in the `explanation` output.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
 
- **Tradeoff chosen:** The scheduler performs a lightweight conflict detection that only flags exact fixed-start-time matches (tasks whose `earliest_start_minute == latest_start_minute`) rather than checking all overlapping durations.

- **Why this is reasonable:** This keeps the implementation simple and fast and provides a clear, actionable warning to the user (for example, two medication events scheduled at the exact same time). It avoids complex interval data structures and reduces the chance of noisy or confusing diagnostics in the MVP.

- **Downside:** The current strategy can miss conflicts where tasks overlap but do not have identical fixed start times (e.g., a 30-minute walk starting at minute 10 and a 20-minute grooming starting at minute 20). Those overlapping durations will not produce a warning under this approach.

- **Decision / next steps:** I kept the lightweight exact-match strategy for readability and maintainability. If users need stricter conflict detection, the scheduler can be extended to perform full interval-overlap checks (or use an interval-tree) and to offer automatic resolution suggestions.

- **AI-assisted review of `generate_schedule()` simplification:** I shared the `generate_schedule()` implementation with an AI coding assistant and asked how to simplify it. The assistant suggested using classic interval-scheduling optimizations (e.g., sort-by-end-time or a weighted interval selection) to improve performance and optimality. While these approaches can be more efficient or optimal in certain formal settings, they assume a simpler model (no per-task earliest/latest windows or per-task priorities expressed as weights). I chose to keep the current, explicit greedy slotting approach because it is clearer to read, easier to extend with per-task windows and recurring logic, and produces human-readable reasoning in the `explanation` output.
---
## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
