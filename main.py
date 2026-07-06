from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler, Priority


def main():
    owner = Owner(name="Alex", available_time_minutes=90)

    # Pets
    pet1 = Pet(name="Mochi", species="cat")
    pet2 = Pet(name="Rex", species="dog")

    # Tasks for Mochi
    # Create tasks out of order to test sorting/filtering
    t_a = Task(title="Grooming", duration_minutes=45, priority=Priority.low, frequency="weekly")
    t_b = Task(title="Morning play", duration_minutes=20, priority=Priority.medium, frequency="daily")
    t_c = Task(title="Feed", duration_minutes=5, priority=Priority.high, frequency="daily")
    t_d = Task(title="Morning walk", duration_minutes=30, priority=Priority.high, frequency="daily")

    # Add them in a deliberately shuffled order
    pet2.add_task(t_a)
    pet1.add_task(t_b)
    pet1.add_task(t_c)
    pet2.add_task(t_d)

    # Add two tasks that require the same fixed start (minute 0) to trigger lightweight conflict warnings
    t_conflict1 = Task(title="Med A", duration_minutes=10, priority=Priority.high, frequency="once")
    t_conflict1.earliest_start_minute = 0
    t_conflict1.latest_start_minute = 0
    t_conflict2 = Task(title="Med B", duration_minutes=15, priority=Priority.high, frequency="once")
    t_conflict2.earliest_start_minute = 0
    t_conflict2.latest_start_minute = 0
    pet1.add_task(t_conflict1)
    pet2.add_task(t_conflict2)

    owner.add_pet(pet1)
    owner.add_pet(pet2)

    # Optionally mark a task completed yesterday to test recurrence logic
    # t1.mark_completed(at=datetime.now() - timedelta(days=1))

    scheduler = Scheduler()
    # mark 'Feed' as already completed to test filtering and recurring creation
    # Use Pet.complete_task so a new recurring instance is created automatically
    pet1.complete_task(t_c.id, at=datetime.now())

    # Demonstrate filtering: all pending tasks for Mochi
    pending_mochi = scheduler.filter_tasks(owner, pet_names=["Mochi"], completed=False)
    print("\nPending tasks for Mochi:")
    for task, pet in pending_mochi:
        print(f"- {task.title} ({pet.name}) — {task.duration_minutes}m — completed={task.completed}")

    result = scheduler.generate_schedule(owner)

    print("Today's Schedule")
    print("------------------")
    if result["accepted"]:
        for idx, item in enumerate(result["accepted"], start=1):
            print(f"{idx}. {item['title']} ({item['pet_name']}) — {item['duration_minutes']}m — {item['priority']}")
    else:
        print("No tasks scheduled.")

    if result["rejected"]:
        print("\nRejected tasks (didn't fit):")
        for item in result["rejected"]:
            print(f"- {item['title']} ({item['pet_name']}) — {item['duration_minutes']}m")

    # Print accepted tasks sorted by time using sort_by_time (already applied by generate_schedule)
    print("\nAccepted tasks (time-ordered):")
    for idx, item in enumerate(result["accepted"], start=1):
        start = item.get("start_minute")
        print(f"{idx}. {item['title']} ({item['pet_name']}) — {item['duration_minutes']}m — start={start}")

    print("\nReasoning:")
    print(result["explanation"])

    if "warnings" in result:
        print("\nWarnings:")
        for w in result["warnings"]:
            print("- ", w)


if __name__ == "__main__":
    main()
