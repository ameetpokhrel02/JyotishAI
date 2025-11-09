# pandityatra_gantt_offline.py
# 100% OFFLINE GANTT CHART using matplotlib
# NO INTERNET | NO MERMAID.INK | WORKS IN COLLEGE LAB
# Run: python pandityatra_gantt_offline.py

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

# === TASK DATA ===
tasks = [
    # [Task Name, Start Date, Duration in Days, Section]
    ["Literature Review & Market Analysis", "2025-11-01", 14, "Research & Planning"],
    ["Problem Statement & Proposal Draft", "2025-11-15", 10, "Research & Planning"],
    ["Supervisor Feedback & Final Proposal", "2025-11-25", 7, "Research & Planning"],
    ["Tech Stack Finalization", "2025-11-15", 7, "Research & Planning"],

    ["Django + PostgreSQL + Docker", "2025-11-22", 21, "Backend"],
    ["Models (User, Pandit, Booking)", "2025-12-13", 14, "Backend"],
    ["JWT + OTP Auth", "2025-12-27", 10, "Backend"],
    ["Admin Dashboard (4 Roles)", "2025-12-15", 14, "Backend"],
    ["API Endpoints", "2026-01-01", 14, "Backend"],

    ["React + Tailwind + shadcn", "2025-12-01", 21, "Frontend"],
    ["User Dashboard (6 Tabs)", "2025-12-22", 10, "Frontend"],
    ["AI Pandit Recommender", "2026-01-01", 14, "Frontend"],
    ["Unified Cart", "2026-01-15", 10, "Frontend"],
    ["Payments (Khalti/Stripe)", "2026-01-20", 14, "Frontend"],
    ["PWA Offline", "2026-02-03", 7, "Frontend"],

    ["Offline Kundali Chatbot", "2026-02-01", 21, "Innovation"],
    ["Books Buy/Borrow", "2026-02-22", 10, "Innovation"],
    ["Whereby Video Call", "2026-02-15", 14, "Innovation"],
    ["Real-Time Chat", "2026-03-01", 10, "Innovation"],
    ["Local Storage", "2026-03-11", 7, "Innovation"],

    ["AR Puja Planner (Optional)", "2026-03-01", 21, "Optional"],
    ["Community Sharing (Optional)", "2026-03-22", 14, "Optional"],
    ["Testing & UAT", "2026-03-15", 31, "Testing"],
    ["Documentation & PPT", "2026-04-01", 14, "Documentation"],
    ["Final Presentation", "2026-04-30", 1, "Documentation"],
]

# === MILESTONES ===
milestones = [
    ["Pandit Verification", "2025-12-28"],
    ["MVP Ready", "2026-02-01"],
    ["Final Report", "2026-04-10"],
    ["Defense", "2026-04-30"],
]

# === SETUP FIGURE ===
fig, ax = plt.subplots(figsize=(14, 10))
plt.title("PanditYatra – FYP Gantt Chart (Nov 2025 – Apr 2026)", fontsize=16, fontweight='bold', pad=20)

# === COLORS BY SECTION ===
colors = {
    "Research & Planning": "#4CAF50",
    "Backend": "#2196F3",
    "Frontend": "#FF9800",
    "Innovation": "#9C27B0",
    "Optional": "#F44336",
    "Testing": "#FFEB3B",
    "Documentation": "#795548"
}

# === PLOT BARS ===
y_pos = np.arange(len(tasks))
start_dates = []
durations = []
labels = []
sections = []

for i, (task, start, duration, section) in enumerate(tasks):
    start_date = datetime.strptime(start, "%Y-%m-%d")
    start_dates.append(start_date)
    durations.append(int(duration))
    labels.append(task)
    sections.append(section)

    ax.barh(y_pos[i], duration, left=start_date, color=colors.get(section, "#777777"), edgecolor='black', height=0.6)

# === MILESTONES (Diamonds) ===
for name, date in milestones:
    mdate = datetime.strptime(date, "%Y-%m-%d")
    ax.plot(mdate, y_pos[0], 'D', markersize=12, color='red', label="Milestone" if name == milestones[0][0] else "")

# === FORMATTING ===
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=9)
ax.invert_yaxis()
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_minor_locator(mdates.DayLocator(interval=15))
plt.xlabel("Timeline", fontsize=12)
plt.grid(True, axis='x', alpha=0.3)

# === LEGEND ===
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=color, label=section) for section, color in colors.items()]
legend_elements.append(plt.Line2D([0], [0], marker='D', color='w', markerfacecolor='red', markersize=10, label='Milestone'))
ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1), fontsize=9)

# === SAVE FILES ===
plt.tight_layout()
plt.savefig("pandityatra_gantt_offline.png", dpi=300, bbox_inches='tight')
plt.savefig("pandityatra_gantt_offline.pdf", bbox_inches='tight')
print("Gantt Chart Saved:")
print("   pandityatra_gantt_offline.png")
print("   pandityatra_gantt_offline.pdf")

# Optional: Show plot
# plt.show()