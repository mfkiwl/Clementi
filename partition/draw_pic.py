import matplotlib.pyplot as plt

# Sample data: Machines with their tasks. Each task has a name, start, and end.
machines = [
    {"name": "Machine 1", "tasks": [{"name": "Task A", "start": 0, "end": 1}, {"name": "Task B", "start": 1, "end": 2}, {"name": "Task F", "start": 2, "end": 4}]},
    {"name": "Machine 2", "tasks": [{"name": "Task C", "start": 0, "end": 2}]},
    {"name": "Machine 3", "tasks": [{"name": "Task D", "start": 0, "end": 1.5}]},
    {"name": "Machine 4", "tasks": [{"name": "Task E", "start": 1, "end": 3}]}
]

# Using different shades of grey
colors = ['grey', 'lightblue', 'Orange']

fig, ax = plt.subplots(figsize=(10, len(machines) * 2))  # Adjust the figure size based on the number of machines

# Plot tasks for each machine
for machine_index, machine in enumerate(machines):
    for task_index, task in enumerate(machine["tasks"]):
        color = colors[task_index % len(colors)]
        ax.plot([task["start"], task["end"]], [machine_index, machine_index], color=color, linewidth=30, solid_capstyle='butt')
        
        # Compute the midpoint of the task's time interval to position the text
        mid_time = task["start"] + (task["end"] - task["start"]) / 2
        text_color = 'black' if color == '#FFFFFF' else 'white'
        ax.text(mid_time, machine_index, task["name"], color=text_color, verticalalignment='center', horizontalalignment='center')

ax.set_yticks(range(len(machines)))
ax.set_yticklabels([machine["name"] for machine in machines])
ax.set_ylim(-1, len(machines))
ax.set_title('Task Timeline for Machines')
plt.tight_layout()

# Save the figure to a PNG file
plt.savefig("machine_task_timeline.png", dpi=300)
