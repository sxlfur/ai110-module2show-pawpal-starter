import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
available_time = st.number_input("Owner available time (minutes)", min_value=1, max_value=1440, value=120)

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")
# Initialize or sync the Owner in session state
owner = st.session_state.get("owner")
if not isinstance(owner, Owner):
    owner = Owner(name=owner_name, available_time_minutes=int(available_time))
    st.session_state["owner"] = owner
else:
    # keep owner in sync with UI inputs
    if owner.name != owner_name:
        owner.name = owner_name
    if owner.available_time_minutes != int(available_time):
        owner.available_time_minutes = int(available_time)

st.markdown("### Pets")
colp1, colp2 = st.columns(2)
with colp1:
    new_pet_name = st.text_input("New pet name", value=pet_name)
with colp2:
    new_species = st.selectbox("New pet species", ["dog", "cat", "other"], index=0)

if st.button("Add pet"):
    # replace any existing pet with same name
    owner.remove_pet(new_pet_name)
    owner.add_pet(Pet(name=new_pet_name, species=new_species))
    st.success(f"Added pet {new_pet_name}")

st.markdown("### Add Task")
if not owner.pets:
    st.info("No pets yet — add a pet before adding tasks.")
else:
    pet_names = [p.name for p in owner.pets]
    selected_pet_name = st.selectbox("Select pet", pet_names)
    selected_pet = next((p for p in owner.pets if p.name == selected_pet_name), None)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task to pet"):
        if selected_pet is None:
            st.error("Selected pet not found")
        else:
            # create Task instance and attach
            task = Task(title=task_title, duration_minutes=int(duration), priority=priority)
            selected_pet.add_task(task)
            st.success(f"Added task '{task_title}' to {selected_pet.name}")

    # display current pets and their tasks
    st.write("Current pets and tasks:")
    rows = []
    for p in owner.pets:
        for t in p.tasks:
            rows.append({"pet": p.name, "task": t.title, "duration_minutes": t.duration_minutes, "priority": t.priority.value if hasattr(t.priority, 'value') else str(t.priority)})
    if rows:
        st.table(rows)
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    # ensure owner exists in session and is the correct type
    owner = st.session_state.get("owner")
    if not isinstance(owner, Owner) or owner.name != owner_name or owner.available_time_minutes != int(available_time):
        owner = Owner(name=owner_name, available_time_minutes=int(available_time))
        st.session_state["owner"] = owner

    # build a Pet from inputs and attach tasks from session_state
    pet = Pet(name=pet_name, species=species)

    for t in st.session_state.tasks:
        duration_val = t.get("duration_minutes") or t.get("duration") or 0
        task = Task(title=t.get("title", "unnamed"), duration_minutes=int(duration_val), priority=t.get("priority", "medium"))
        pet.add_task(task)

    # replace any existing pet with same name
    owner.remove_pet(pet.name)
    owner.add_pet(pet)

    scheduler = Scheduler()
    result = scheduler.generate_schedule(owner)

    st.write("### Scheduled tasks")
    if result["accepted"]:
        st.table(result["accepted"])
    else:
        st.info("No tasks fit in the available time.")

    if result["rejected"]:
        with st.expander("Rejected tasks (didn't fit)"):
            st.table(result["rejected"])

    with st.expander("Reasoning"):
        st.text(result["explanation"])
